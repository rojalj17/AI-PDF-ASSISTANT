"""
Wraps the Ollama chat model and turns retrieved chunks into a grounded,
naturally-worded answer (no PDF/page citations spoken in the reply).
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

from backend import config

_llm = OllamaLLM(model=config.LLM_MODEL)

PROMPT_TEMPLATE = """You are a helpful assistant answering questions using the information below.

Use ONLY the information in the context to answer. Do not mention PDFs,
documents, filenames, or page numbers in your answer - just answer naturally,
as if you already knew this information.

If the answer isn't in the context, say exactly:
"I don't have that information."

Keep the answer clear and concise.

Context:
{context}

Question:
{question}

Answer:
"""

_prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
_chain = _prompt | _llm


def format_context(docs) -> str:
    parts = []
    for doc in docs:
        parts.append(doc.page_content)
    return "\n\n".join(parts)


def answer_question(question: str, docs) -> str:
    context = format_context(docs)
    return _chain.invoke({"question": question, "context": context})


def stream_answer(question: str, docs):
    """Yield the answer incrementally as the model generates it."""
    context = format_context(docs)
    for chunk in _chain.stream({"question": question, "context": context}):
        yield chunk
