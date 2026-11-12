"""
AI PDF Assistant - Gradio front end.

Run with:
    python app.py
"""

import os
import gradio as gr

from backend import config
from backend import llm, pdf_loader, vectorstore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_indexed_list_markdown() -> str:
    sources = vectorstore.list_indexed_sources()
    if not sources:
        return "_No documents indexed yet._"
    return "\n".join(f"- {s}" for s in sources)


def handle_upload(files):
    if not files:
        return get_indexed_list_markdown(), "No files selected."

    status_lines = []

    for file in files:
        file_path = file.name if hasattr(file, "name") else file
        filename = os.path.basename(file_path)

        try:
            chunks = pdf_loader.process_pdf(file_path)
            vectorstore.index_documents(chunks)
            status_lines.append(
                f"✅ Indexed **{filename}** ({len(chunks)} chunks)"
            )
        except Exception as e:
            status_lines.append(
                f"❌ Failed to index **{filename}**: {e}"
            )

    return get_indexed_list_markdown(), "\n".join(status_lines)


def clear_all():
    vectorstore.clear_collection()
    return (
        get_indexed_list_markdown(),
        "Cleared all indexed documents.",
        WELCOME_MESSAGE,
        None,
    )


# ---------------------------------------------------------------------------
# Chat
# ---------------------------------------------------------------------------

def respond(message, history):

    history = history or []

    message = (message or "").strip()

    if not message:
        yield history, ""
        return

    history.append(
        {
            "role": "user",
            "content": message,
        }
    )

    sources = vectorstore.list_indexed_sources()

    if not sources:
        history.append(
            {
                "role": "assistant",
                "content": "Please upload and index a PDF first.",
            }
        )
        yield history, ""
        return

    docs = vectorstore.search(message)

    if not docs:
        history.append(
            {
                "role": "assistant",
                "content": "I don't have that information.",
            }
        )
        yield history, ""
        return

    history.append(
        {
            "role": "assistant",
            "content": "",
        }
    )

    yield history, ""

    answer = ""

    for token in llm.stream_answer(message, docs):
        answer += token
        history[-1]["content"] = answer
        yield history, ""


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

CUSTOM_CSS = """
.gradio-container {
    max-width:1100px !important;
    margin:auto;
}

#status_box {
    font-size:0.85em;
}
"""

WELCOME_MESSAGE = [
    {
        "role": "assistant",
        "content": "👋 Hi! Upload one or more PDFs, click **Index PDFs**, then ask me anything about them.",
    }
]

with gr.Blocks(
    title=config.APP_TITLE,
    css=CUSTOM_CSS,
    theme=gr.themes.Soft(),
) as demo:

    gr.Markdown(f"# {config.APP_ICON} {config.APP_TITLE}")

    gr.Markdown(
        "Upload PDFs, index them, then chat naturally with your documents."
    )

    with gr.Row():

        with gr.Column(scale=1):

            gr.Markdown("### Upload PDFs")

            file_upload = gr.Files(
                label="PDF Files",
                file_types=[".pdf"],
                file_count="multiple",
            )

            index_btn = gr.Button(
                "Index PDFs",
                variant="primary",
            )

            status_box = gr.Markdown(
                "",
                elem_id="status_box",
            )

            gr.Markdown("### Indexed Documents")

            indexed_list = gr.Markdown(
                get_indexed_list_markdown()
            )

            clear_btn = gr.Button(
                "Clear All Documents",
                variant="stop",
            )

        with gr.Column(scale=2):

            chatbot = gr.Chatbot(
                type="messages",
                value=WELCOME_MESSAGE,
                label="Assistant",
                height=520,
            )

            msg = gr.Textbox(
                label="Ask a question",
                placeholder="Ask anything about your PDFs...",
                autofocus=True,
            )

            with gr.Row():
                send_btn = gr.Button(
                    "Send",
                    variant="primary",
                )

                clear_chat_btn = gr.Button(
                    "Clear Chat"
                )

    index_btn.click(
        handle_upload,
        inputs=file_upload,
        outputs=[
            indexed_list,
            status_box,
        ],
    )

    clear_btn.click(
        clear_all,
        outputs=[
            indexed_list,
            status_box,
            chatbot,
            file_upload,
        ],
    )

    msg.submit(
        respond,
        inputs=[
            msg,
            chatbot,
        ],
        outputs=[
            chatbot,
            msg,
        ],
    )

    send_btn.click(
        respond,
        inputs=[
            msg,
            chatbot,
        ],
        outputs=[
            chatbot,
            msg,
        ],
    )

    clear_chat_btn.click(
        lambda: WELCOME_MESSAGE,
        outputs=chatbot,
    )


if __name__ == "__main__":
    demo.launch(
        inbrowser=True,
    )