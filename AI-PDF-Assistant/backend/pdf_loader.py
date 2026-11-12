"""
Handles everything related to getting a PDF from "uploaded by the user"
to "a list of chunked LangChain Document objects ready to embed".

Each chunk carries metadata:
    - source: the original filename (used for citations)
    - page:   1-indexed page number (used for citations)
"""

import os
import shutil

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend import config


def save_uploaded_pdf(file_path: str) -> str:
    """Copy an uploaded PDF (e.g. Gradio's temp path) into the persistent PDF_DIR."""
    filename = os.path.basename(file_path)
    dest_path = os.path.join(config.PDF_DIR, filename)

    if os.path.abspath(file_path) != os.path.abspath(dest_path):
        shutil.copy(file_path, dest_path)

    return dest_path


def load_pdf(path: str):
    """Load a PDF into one Document per page, with clean source/page metadata."""
    loader = PyMuPDFLoader(path)
    documents = loader.load()

    filename = os.path.basename(path)
    for doc in documents:
        doc.metadata["source"] = filename
        # PyMuPDFLoader's "page" metadata is 0-indexed; make it human-friendly.
        doc.metadata["page"] = doc.metadata.get("page", 0) + 1

    return documents


def split_documents(documents):
    """Split page-level documents into overlapping chunks for embedding."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
        add_start_index=True,
    )
    return splitter.split_documents(documents)


def process_pdf(file_path: str):
    """Full pipeline: save -> load -> split. Returns chunked Document list."""
    saved_path = save_uploaded_pdf(file_path)
    documents = load_pdf(saved_path)
    chunks = split_documents(documents)
    return chunks
