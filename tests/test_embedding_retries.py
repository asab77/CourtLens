"""Unit tests for bounded embedding rate-limit retries and pacing."""

import unittest
from contextlib import redirect_stdout
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import numpy as np
from openai import RateLimitError

from build_index import BATCH_SIZE, create_embeddings
from gateway_config import EXPERIMENT_EMBEDDING_MODEL
from retrieve import embed_question


def rate_limit_error() -> RateLimitError:
    request = httpx.Request("POST", "https://gateway.example/v1/embeddings")
    response = httpx.Response(429, request=request)
    return RateLimitError("rate limited", response=response, body={})


def embedding_response(vectors: list[list[float]], reverse: bool = False):
    data = [
        SimpleNamespace(index=index, embedding=embedding)
        for index, embedding in enumerate(vectors)
    ]
    if reverse:
        data.reverse()
    return SimpleNamespace(data=data)


class FakeEmbeddings:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


def fake_client(*outcomes):
    return SimpleNamespace(embeddings=FakeEmbeddings(outcomes))


class DocumentEmbeddingRetryTests(unittest.TestCase):
    def test_rate_limited_batch_succeeds_with_schedule_and_preserves_order(self):
        client = fake_client(
            rate_limit_error(),
            rate_limit_error(),
            embedding_response([[1.0, 0.0], [0.0, 1.0]], reverse=True),
        )

        with patch("embedding_retry.time.sleep") as retry_sleep:
            with redirect_stdout(StringIO()) as output:
                matrix = create_embeddings(
                    client,
                    ["first", "second"],
                    model=EXPERIMENT_EMBEDDING_MODEL,
                )

        self.assertEqual(retry_sleep.call_args_list[0].args, (60,))
        self.assertEqual(retry_sleep.call_args_list[1].args, (120,))
        self.assertEqual(retry_sleep.call_count, 2)
        self.assertEqual(len(client.embeddings.calls), 3)
        self.assertTrue(
            all(
                call["model"] == EXPERIMENT_EMBEDDING_MODEL
                for call in client.embeddings.calls
            )
        )
        np.testing.assert_array_equal(matrix, [[1.0, 0.0], [0.0, 1.0]])
        self.assertIn("batch 1/1 (chunks 1-2)", output.getvalue())
        self.assertIn("retry 1/3 in 60 seconds", output.getvalue())
        self.assertIn("retry 2/3 in 120 seconds", output.getvalue())

    def test_retry_schedule_is_bounded_and_final_rate_limit_is_reraised(self):
        errors = [rate_limit_error() for _ in range(4)]
        client = fake_client(*errors)

        with patch("embedding_retry.time.sleep") as retry_sleep:
            with redirect_stdout(StringIO()):
                with self.assertRaises(RateLimitError) as raised:
                    create_embeddings(client, ["text"])

        self.assertIs(raised.exception, errors[-1])
        self.assertEqual([call.args[0] for call in retry_sleep.call_args_list], [60, 120, 240])
        self.assertEqual(len(client.embeddings.calls), 4)

    def test_unrelated_error_propagates_without_retry(self):
        error = RuntimeError("unrelated")
        client = fake_client(error)

        with patch("embedding_retry.time.sleep") as retry_sleep:
            with self.assertRaises(RuntimeError) as raised:
                create_embeddings(client, ["text"])

        self.assertIs(raised.exception, error)
        retry_sleep.assert_not_called()
        self.assertEqual(len(client.embeddings.calls), 1)

    def test_successful_batches_are_paced_only_between_batches(self):
        first = [[float(index), 1.0] for index in range(BATCH_SIZE)]
        second = [[999.0, 1.0]]
        client = fake_client(embedding_response(first), embedding_response(second))

        with patch("build_index.time.sleep") as pacing_sleep:
            with redirect_stdout(StringIO()):
                matrix = create_embeddings(client, ["text"] * (BATCH_SIZE + 1))

        pacing_sleep.assert_called_once_with(10)
        self.assertEqual(len(client.embeddings.calls), 2)
        self.assertEqual(matrix.shape, (BATCH_SIZE + 1, 2))
        np.testing.assert_array_equal(matrix[-1], [999.0, 1.0])


class QueryEmbeddingRetryTests(unittest.TestCase):
    def test_query_embedding_retries_after_rate_limit(self):
        client = fake_client(
            rate_limit_error(),
            embedding_response([[3.0, 4.0]]),
        )

        with patch("embedding_retry.time.sleep") as retry_sleep:
            with redirect_stdout(StringIO()):
                vector = embed_question(
                    "question", client=client, model=EXPERIMENT_EMBEDDING_MODEL
                )

        retry_sleep.assert_called_once_with(60)
        self.assertEqual(len(client.embeddings.calls), 2)
        self.assertTrue(
            all(
                call["model"] == EXPERIMENT_EMBEDDING_MODEL
                for call in client.embeddings.calls
            )
        )
        np.testing.assert_allclose(vector, [[0.6, 0.8]])

    def test_query_embedding_reraises_after_bounded_retries(self):
        errors = [rate_limit_error() for _ in range(4)]
        client = fake_client(*errors)

        with patch("embedding_retry.time.sleep") as retry_sleep:
            with redirect_stdout(StringIO()):
                with self.assertRaises(RateLimitError) as raised:
                    embed_question("question", client=client)

        self.assertIs(raised.exception, errors[-1])
        self.assertEqual([call.args[0] for call in retry_sleep.call_args_list], [60, 120, 240])
        self.assertEqual(len(client.embeddings.calls), 4)

    def test_query_embedding_does_not_retry_unrelated_errors(self):
        error = ValueError("bad request")
        client = fake_client(error)

        with patch("embedding_retry.time.sleep") as retry_sleep:
            with self.assertRaises(ValueError) as raised:
                embed_question("question", client=client)

        self.assertIs(raised.exception, error)
        retry_sleep.assert_not_called()
        self.assertEqual(len(client.embeddings.calls), 1)


if __name__ == "__main__":
    unittest.main()
