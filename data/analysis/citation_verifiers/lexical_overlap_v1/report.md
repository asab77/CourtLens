# Citation verifier offline evaluation

Verifier: lexical-overlap v1.0. Benchmark v1.0.
Benchmark SHA-256: `2519c6563bcd21ac651e90a0151a67cbd37d6e4d50e6681c061b78884e18cffa`

Lexical overlap is a demonstration heuristic, not semantic legal verification.

```json
{
  "accuracy": 0.5625,
  "confusion_matrix": {
    "counts": {
      "CONTRADICTED": {
        "CONTRADICTED": 0,
        "PARTIALLY_SUPPORTED": 6,
        "SUPPORTED": 2,
        "UNSUPPORTED": 0
      },
      "PARTIALLY_SUPPORTED": {
        "CONTRADICTED": 0,
        "PARTIALLY_SUPPORTED": 7,
        "SUPPORTED": 0,
        "UNSUPPORTED": 0
      },
      "SUPPORTED": {
        "CONTRADICTED": 0,
        "PARTIALLY_SUPPORTED": 3,
        "SUPPORTED": 7,
        "UNSUPPORTED": 0
      },
      "UNSUPPORTED": {
        "CONTRADICTED": 0,
        "PARTIALLY_SUPPORTED": 3,
        "SUPPORTED": 0,
        "UNSUPPORTED": 4
      }
    },
    "label_order": [
      "SUPPORTED",
      "PARTIALLY_SUPPORTED",
      "UNSUPPORTED",
      "CONTRADICTED"
    ],
    "orientation": "rows=gold, columns=prediction"
  },
  "failure_counts": {
    "EXECUTION_FAILURE": 0,
    "INVALID_LABEL": 0,
    "INVALID_RESPONSE_SCHEMA": 0,
    "MISSING_PREDICTION": 0,
    "PROVIDER_ERROR": 0,
    "TIMEOUT": 0
  },
  "false_support_denominator_valid": 22,
  "false_support_numerator": 2,
  "false_support_rate": 0.09090909090909091,
  "macro_f1": 0.5006440927493558,
  "metric_scope": "valid predictions only; coverage/failures use all examples. FSR denominator is valid non-SUPPORTED gold examples; failures are not negative predictions.",
  "non_supported_gold_count_all": 22,
  "per_class": {
    "CONTRADICTED": {
      "f1": 0.0,
      "gold_count_valid": 8,
      "precision": 0.0,
      "predicted_count": 0,
      "recall": 0.0,
      "true_positives": 0
    },
    "PARTIALLY_SUPPORTED": {
      "f1": 0.5384615384615384,
      "gold_count_valid": 7,
      "precision": 0.3684210526315789,
      "predicted_count": 19,
      "recall": 1.0,
      "true_positives": 7
    },
    "SUPPORTED": {
      "f1": 0.7368421052631577,
      "gold_count_valid": 10,
      "precision": 0.7777777777777778,
      "predicted_count": 9,
      "recall": 0.7,
      "true_positives": 7
    },
    "UNSUPPORTED": {
      "f1": 0.7272727272727273,
      "gold_count_valid": 7,
      "precision": 1.0,
      "predicted_count": 4,
      "recall": 0.5714285714285714,
      "true_positives": 4
    }
  },
  "prediction_coverage": 1.0,
  "supported_class_precision": 0.7777777777777778,
  "supported_class_recall": 0.7,
  "total_examples": 32,
  "valid_predictions": 32
}
```

## Limitations

- 32 claims and 6 answers: small curated challenge set, not deployment-representative.
- 30 of 32 claim examples are synthetic pairings/claims; original source passages remain authentic.
- Concentrated on Miranda and Obergefell, with three supplementary concurrence cases.
- Example selection was influenced by observed CourtLens failures.
- AI-assisted, user-authorized adjudication; no independent human legal-expert review.
- Not an independent generalization benchmark; no held-out split or leakage-resistant evaluation design.
- Success does not establish legal accuracy, claim completeness or deployment safety.
- OCR-derived attribution remains uncertain; original metadata and text are preserved.
- No semantic verifier, LLM judge, NLI model or generation/retrieval change is implemented.
- The lexical baseline does not understand negation, attribution or legal scope, and never predicts CONTRADICTED.
- Classifier metrics are conditional on valid predictions; inspect coverage and failure counts alongside them.
- No provider implementation, paid inference, application integration, or answer-level scoring is included.
