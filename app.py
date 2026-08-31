"""CourtLens Streamlit interface for retrieval and grounded RAG assistance."""

import re

import streamlit as st

from evaluation import SCORE_NAMES, append_evaluation, build_evaluation_record
from gateway_config import get_nyu_api_gateway_api_key
from rag import (
    ANSWER_MODELS,
    CITATION_PATTERN,
    attach_source_ids,
    generate_grounded_answer,
    generate_grounded_answer_from_evidence,
)
from retrieve import load_vector_store, semantic_search


st.set_page_config(
    page_title="CourtLens | Supreme Court Research",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .courtlens-header {
        margin-bottom: 0.7rem;
        overflow: visible;
        padding-top: 0.25rem;
    }
    .courtlens-title {
        color: var(--text-color);
        font-size: 2rem;
        font-weight: 650;
        letter-spacing: -0.025em;
        line-height: 1.35;
        margin: 0;
        overflow: visible;
    }
    .courtlens-subtitle {
        color: var(--text-color);
        font-size: 1rem;
        margin: 0.3rem 0 0;
        opacity: 0.68;
    }
    .section-kicker {
        color: var(--text-color);
        font-size: 0.72rem;
        font-weight: 650;
        letter-spacing: 0.09em;
        margin-bottom: 0.35rem;
        opacity: 0.62;
    }
    .index-summary {
        color: var(--text-color);
        font-size: 0.84rem;
        line-height: 1.65;
        opacity: 0.68;
    }
    .chat-empty-state {
        padding: 3.5rem 1rem 1.5rem;
        text-align: center;
    }
    .chat-empty-icon {
        color: var(--text-color);
        font-size: 2rem;
        margin-bottom: 0.55rem;
        opacity: 0.78;
    }
    .chat-empty-title {
        color: var(--text-color);
        font-size: 1.35rem;
        font-weight: 600;
        margin-bottom: 0.35rem;
    }
    .chat-empty-copy {
        color: var(--text-color);
        font-size: 0.95rem;
        line-height: 1.45;
        opacity: 0.68;
    }
    div[data-testid="stSidebar"] hr {
        margin: 1.15rem 0;
    }
    .stMarkdown h1 {
        font-size: 1.45rem;
        line-height: 1.35;
        margin: 1rem 0 0.45rem;
    }
    .stMarkdown h2 {
        font-size: 1.25rem;
        line-height: 1.4;
        margin: 0.9rem 0 0.4rem;
    }
    .stMarkdown h3 {
        font-size: 1.08rem;
        line-height: 1.4;
        margin: 0.8rem 0 0.35rem;
    }
    .stMarkdown code {
        color: var(--primary-color);
        background: rgba(128, 128, 128, 0.08);
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 0.25rem;
        padding: 0.02rem 0.25rem;
    }
    @media (max-width: 700px) {
        .block-container { padding-top: 1.5rem; }
        .courtlens-title { font-size: 1.7rem; }
        .chat-empty-state { padding-top: 2rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def cached_vector_store():
    """Load the local index once per Streamlit server process."""
    return load_vector_store()


def passage_preview(text: str, limit: int = 420) -> str:
    """Create a compact preview without altering stored text."""
    preview = " ".join(display_text(text).split())
    return preview if len(preview) <= limit else preview[:limit].rsplit(" ", 1)[0] + "…"


PAGE_MARKER_PATTERN = re.compile(r"(?im)^\s*=+\s*PAGE\s+\d+\s*=+\s*$")


def display_text(text: str) -> str:
    """Remove extraction-only page markers from a UI copy of stored text."""
    cleaned = PAGE_MARKER_PATTERN.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def display_answer(answer: str) -> str:
    """Style valid inline source IDs without changing the stored model output."""
    return CITATION_PATTERN.sub(lambda match: f"`[S{match.group(1)}]`", answer)


def source_label(metadata: dict) -> str:
    """Prefer the actual raw filename while retaining a safe fallback."""
    return metadata.get("original_source_file") or metadata["source_file"]


def page_label(metadata: dict) -> str:
    """Format a single page or inclusive page range."""
    start, end = metadata["page_start"], metadata["page_end"]
    return str(start) if start == end else f"{start}–{end}"


def key_is_configured() -> bool:
    return bool(get_nyu_api_gateway_api_key())


def choose_retrieval_example(question: str) -> None:
    """Populate the retrieval field and run the existing search on the next rerun."""
    st.session_state.retrieval_question = question
    st.session_state.run_retrieval_example = True


def show_retrieval_result(result: dict, rank: int) -> None:
    """Render one evidence card used by Retrieval mode."""
    metadata = result["metadata"]
    with st.container(border=True):
        heading, score = st.columns([5, 1.25])
        with heading:
            st.subheader(f"#{rank}  {metadata['case_name']}")
            st.caption(f"Pages {page_label(metadata)}")
        with score:
            st.caption(f"{result['similarity']:.0%} similarity")
        st.write(passage_preview(result["text"]))
        st.caption(f"Chunk {metadata['chunk_index']}")
        with st.expander("View full passage", expanded=False):
            st.caption(
                f"Source PDF: {source_label(metadata)} · Chunk {metadata['chunk_index']}"
            )
            st.text(display_text(result["text"]))


def cited_evidence(answer: str, evidence: list[dict]) -> list[dict]:
    """Return retrieved items whose source IDs actually appear in an answer."""
    cited_ids = {f"S{number}" for number in CITATION_PATTERN.findall(answer)}
    return [item for item in evidence if item["source_id"] in cited_ids]


def show_source_summary(answer: str, evidence: list[dict]) -> None:
    """Display cited sources, falling back transparently to retrieved evidence."""
    cited = cited_evidence(answer, evidence)
    st.markdown(f"**{'Sources used' if cited else 'Retrieved evidence'}**")
    for item in cited or evidence:
        metadata = item["metadata"]
        st.caption(
            f"[{item['source_id']}] {metadata['case_name']}, pp. {page_label(metadata)}"
        )


def show_evidence(evidence: list[dict], label: str = "View retrieved evidence") -> None:
    """Render a compact, collapsed, responsive two-column evidence grid."""
    with st.expander(label, expanded=False):
        for row_start in range(0, len(evidence), 2):
            columns = st.columns(2, gap="medium")
            for column, item in zip(columns, evidence[row_start : row_start + 2]):
                metadata = item["metadata"]
                with column:
                    with st.container(border=True):
                        st.markdown(f"**[{item['source_id']}] {metadata['case_name']}**")
                        st.caption(
                            f"Pages {page_label(metadata)} · Similarity {item['similarity']:.2f} · "
                            f"Chunk {metadata['chunk_index']}"
                        )
                        st.text(display_text(item["text"]))


def show_assistant_message(message: dict) -> None:
    """Render an assistant answer with its own citations and evidence."""
    with st.chat_message("assistant"):
        if message.get("model_name"):
            st.caption(f"CourtLens · {message['model_name']}")
        st.markdown(display_answer(message["content"]))

        evidence = message.get("evidence", [])
        if evidence:
            show_source_summary(message["content"], evidence)
            st.caption("Grounded in retrieved CourtLens evidence")
            show_evidence(evidence)


def show_comparison_answer(label: str, model_name: str, answer: str, evidence: list[dict]) -> None:
    """Render one side of the human evaluation workspace."""
    st.caption(label.upper())
    st.subheader(model_name)
    st.divider()
    st.markdown(display_answer(answer))
    show_source_summary(answer, evidence)
    st.caption("Grounded in retrieved CourtLens evidence")


METRIC_DETAILS = {
    "correctness": "Does the answer correctly address the question?",
    "faithfulness": "Is the answer supported by the retrieved evidence?",
    "clarity": "Is the answer clear and well structured?",
    "citation_quality": "Do the citations appropriately support the claims?",
}


try:
    vector_store = cached_vector_store()
    index, records, manifest = vector_store
except Exception as error:
    st.error(f"CourtLens could not load the local vector store: {error}")
    st.stop()

case_names = sorted({record["metadata"]["case_name"] for record in records})
st.session_state.setdefault("court_messages", [])

st.markdown(
    """
    <div class="courtlens-header">
        <div class="courtlens-title">⚖️ CourtLens</div>
        <div class="courtlens-subtitle">AI-powered research across landmark U.S. Supreme Court opinions</div>
    </div>
    """,
    unsafe_allow_html=True,
)

mode = st.segmented_control(
    "Application mode",
    ["Retrieval", "AI Assistant"],
    default="Retrieval",
    key="application_mode",
    label_visibility="collapsed",
)

with st.sidebar:
    st.header("Retrieval settings")
    top_k = st.slider("Top-K results", min_value=1, max_value=10, value=5)
    selected_case = st.selectbox("Case filter", ["All cases", *case_names])
    st.divider()
    st.markdown('<div class="section-kicker">ABOUT THIS INDEX</div>', unsafe_allow_html=True)
    embedding_name = manifest["embedding_model"].split("/")[-1]
    st.markdown(
        f'<div class="index-summary">{len(case_names)} cases · {index.ntotal} chunks<br>'
        f'FAISS cosine similarity<br>{embedding_name}</div>',
        unsafe_allow_html=True,
    )
    if mode == "AI Assistant":
        st.caption("Each question retrieves fresh evidence from the indexed opinions.")

case_filter = None if selected_case == "All cases" else selected_case

if mode == "Retrieval":
    st.subheader("Search Supreme Court opinions")

    with st.form("search_form"):
        question = st.text_input(
            "Research question",
            placeholder="What rights does Miranda protect?",
            key="retrieval_question",
        )
        search_clicked = st.form_submit_button("Search", type="primary")

    example_questions = {
        "Miranda rights": "What rights does Miranda protect?",
        "Right to counsel": "When must states provide counsel to criminal defendants?",
        "Student speech": "What constitutional protection applies to student expression?",
    }
    st.caption("Try an example")
    example_columns = st.columns(3)
    for column, (label, example_question) in zip(example_columns, example_questions.items()):
        column.button(
            label,
            key=f"retrieval_example_{label}",
            on_click=choose_retrieval_example,
            args=(example_question,),
            use_container_width=True,
        )

    search_clicked = search_clicked or st.session_state.pop("run_retrieval_example", False)

    if search_clicked:
        if not question.strip():
            st.warning("Enter a research question before searching.")
        elif not key_is_configured():
            st.error(
                "NYU AI Gateway API key is not configured. Add it to Streamlit "
                "secrets or your local environment."
            )
        else:
            try:
                with st.spinner("Searching Supreme Court opinions…"):
                    results = semantic_search(
                        question,
                        top_k=top_k,
                        case_name=case_filter,
                        vector_store=vector_store,
                    )
            except Exception as error:
                st.error(f"Search failed: {error}")
            else:
                st.divider()
                st.header("Retrieved Evidence")
                st.caption(
                    f"{len(results)} passage{'s' if len(results) != 1 else ''} retrieved "
                    f"for “{question}”"
                )
                if not results:
                    st.info("No passages matched the selected case filter.")
                for rank, result in enumerate(results, start=1):
                    show_retrieval_result(result, rank)

else:
    assistant_mode = st.segmented_control(
        "AI Assistant mode",
        ["Normal Chat", "Compare Models"],
        default="Normal Chat",
        key="assistant_mode",
        label_visibility="collapsed",
    )

    if assistant_mode == "Normal Chat":
        conversation_header, clear_column, spacer_column = st.columns(
            [2.3, 1.15, 3.55], vertical_alignment="bottom"
        )
        with conversation_header:
            answer_model_name = st.selectbox("Model", list(ANSWER_MODELS))
        with clear_column:
            if st.button("+ New chat", use_container_width=True):
                st.session_state.court_messages = []
                st.rerun()
        st.divider()

        empty_state_prompt = None
        if not st.session_state.court_messages:
            st.markdown(
                """
                <div class="chat-empty-state">
                    <div class="chat-empty-icon">⚖️</div>
                    <div class="chat-empty-title">Ask CourtLens</div>
                    <div class="chat-empty-copy">Ask a question about the indexed<br>Supreme Court opinions.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            chat_examples = [
                "What rights does Miranda protect?",
                "When is counsel constitutionally required?",
                "What protections apply to student speech?",
            ]
            example_columns = st.columns(3)
            for column, example in zip(example_columns, chat_examples):
                if column.button(example, key=f"chat_example_{example}", use_container_width=True):
                    empty_state_prompt = example

        for message in st.session_state.court_messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(message["content"])
            else:
                show_assistant_message(message)

        prompt = st.chat_input("Ask a question about the indexed Supreme Court opinions")
        prompt = prompt or empty_state_prompt
        if prompt:
            st.session_state.court_messages.append({"role": "user", "content": prompt})
            try:
                if not key_is_configured():
                    raise ValueError(
                        "NYU AI Gateway API key is not configured. Add it to Streamlit "
                        "secrets or your local environment."
                    )
                with st.spinner("Retrieving evidence and drafting a grounded answer…"):
                    results = semantic_search(
                        prompt,
                        top_k=top_k,
                        case_name=case_filter,
                        vector_store=vector_store,
                    )
                    answer, evidence = generate_grounded_answer(
                        prompt,
                        results,
                        ANSWER_MODELS[answer_model_name],
                        conversation_history=st.session_state.court_messages[:-1],
                    )
            except Exception as error:
                st.session_state.court_messages.append(
                    {"role": "assistant", "content": f"I could not complete the request: {error}"}
                )
            else:
                st.session_state.court_messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "evidence": evidence,
                        "model_name": answer_model_name,
                    }
                )
            st.rerun()

    else:
        st.subheader("Model comparison workspace")
        st.caption(
            "Both models receive one shared FAISS retrieval and the exact same labeled evidence."
        )
        model_a_column, model_b_column = st.columns(2)
        with model_a_column:
            model_a_name = st.selectbox("Model A", list(ANSWER_MODELS), index=0)
        with model_b_column:
            model_b_name = st.selectbox("Model B", list(ANSWER_MODELS), index=1)

        with st.form("comparison_form"):
            comparison_question = st.text_input(
                "Evaluation question", placeholder="What rights does Miranda protect?"
            )
            compare_clicked = st.form_submit_button("Compare answers", type="primary")

        if model_a_name == model_b_name:
            st.warning("Choose two different answer models.")

        if compare_clicked:
            if not comparison_question.strip():
                st.warning("Enter an evaluation question before comparing models.")
            elif model_a_name == model_b_name:
                st.warning("Model A and Model B must be different.")
            elif not key_is_configured():
                st.error(
                    "NYU AI Gateway API key is not configured. Add it to Streamlit "
                    "secrets or your local environment."
                )
            else:
                try:
                    with st.spinner("Retrieving once and generating both answers…"):
                        # This is the only retrieval call in the comparison workflow.
                        results = semantic_search(
                            comparison_question,
                            top_k=top_k,
                            case_name=case_filter,
                            vector_store=vector_store,
                        )
                        evidence = attach_source_ids(results)
                        model_a_answer = generate_grounded_answer_from_evidence(
                            comparison_question,
                            evidence,
                            ANSWER_MODELS[model_a_name],
                        )
                        model_b_answer = generate_grounded_answer_from_evidence(
                            comparison_question,
                            evidence,
                            ANSWER_MODELS[model_b_name],
                        )
                except Exception as error:
                    st.error(f"Comparison failed: {error}")
                else:
                    chunk_ids = [item["metadata"]["chunk_index"] for item in evidence]
                    st.session_state.comparison_result = {
                        "question": comparison_question,
                        "model_a_name": model_a_name,
                        "model_a_id": ANSWER_MODELS[model_a_name],
                        "model_b_name": model_b_name,
                        "model_b_id": ANSWER_MODELS[model_b_name],
                        "model_a_answer": model_a_answer,
                        "model_b_answer": model_b_answer,
                        "evidence": evidence,
                        "model_a_chunk_ids": chunk_ids,
                        "model_b_chunk_ids": list(chunk_ids),
                        "top_k": top_k,
                        "case_filter": case_filter,
                    }
                    st.session_state.comparison_version = (
                        st.session_state.get("comparison_version", 0) + 1
                    )
                    st.rerun()

        comparison = st.session_state.get("comparison_result")
        if comparison:
            st.divider()
            answer_a_column, answer_b_column = st.columns(2, gap="large")
            with answer_a_column:
                show_comparison_answer(
                    "Model A",
                    comparison["model_a_name"],
                    comparison["model_a_answer"],
                    comparison["evidence"],
                )
            with answer_b_column:
                show_comparison_answer(
                    "Model B",
                    comparison["model_b_name"],
                    comparison["model_b_answer"],
                    comparison["evidence"],
                )

            st.markdown("**Shared retrieved evidence**")
            st.caption("Both models received these exact labeled passages.")
            show_evidence(comparison["evidence"], label="View shared retrieved evidence")

            st.divider()
            st.header("Evaluate responses")
            st.caption("Rate each answer from 1 (poor) to 5 (excellent). All fields are required.")
            version = st.session_state.get("comparison_version", 0)
            score_headers = st.columns([2, 1, 1])
            score_headers[1].markdown(f"**{comparison['model_a_name']}**")
            score_headers[2].markdown(f"**{comparison['model_b_name']}**")

            model_a_scores = {}
            model_b_scores = {}
            for score_name in SCORE_NAMES:
                label = score_name.replace("_", " ").title()
                metric_column, a_column, b_column = st.columns([2, 1, 1])
                with metric_column:
                    st.markdown(f"**{label}**")
                    st.caption(METRIC_DETAILS[score_name])
                with a_column:
                    model_a_scores[score_name] = st.number_input(
                        f"Model A {label}",
                        min_value=1,
                        max_value=5,
                        value=None,
                        step=1,
                        placeholder="1–5",
                        key=f"a_{score_name}_{version}",
                        label_visibility="collapsed",
                    )
                with b_column:
                    model_b_scores[score_name] = st.number_input(
                        f"Model B {label}",
                        min_value=1,
                        max_value=5,
                        value=None,
                        step=1,
                        placeholder="1–5",
                        key=f"b_{score_name}_{version}",
                        label_visibility="collapsed",
                    )

            winner = st.radio(
                "Which answer was better?",
                ["Model A", "Model B", "Tie"],
                index=None,
                horizontal=True,
                key=f"winner_{version}",
                format_func=lambda choice: {
                    "Model A": comparison["model_a_name"],
                    "Model B": comparison["model_b_name"],
                    "Tie": "Tie",
                }[choice],
            )
            if st.button("Save Evaluation", type="primary"):
                try:
                    record = build_evaluation_record(
                        comparison, model_a_scores, model_b_scores, winner
                    )
                    append_evaluation(record)
                except ValueError as error:
                    st.warning(str(error))
                else:
                    st.success("Evaluation saved to data/evaluations.jsonl.")
