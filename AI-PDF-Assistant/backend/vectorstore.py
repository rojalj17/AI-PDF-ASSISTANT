"""
Persistent ChromaDB vector store.

Unlike InMemoryVectorStore, this survives app restarts: embeddings are
written to disk under config.CHROMA_DIR and reloaded automatically.
Supports multiple PDFs in one collection, filtered by "source" metadata.
"""

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

from backend import config

_embeddings = OllamaEmbeddings(model=config.EMBED_MODEL)
_vector_store = None


def get_vector_store() -> Chroma:
    """Lazily create (or reload) the persistent Chroma collection."""
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name=config.COLLECTION_NAME,
            embedding_function=_embeddings,
            persist_directory=config.CHROMA_DIR,
        )
    return _vector_store


def index_documents(chunks):
    """Embed and persist a list of chunked Documents."""
    store = get_vector_store()
    store.add_documents(chunks)


def search(query: str, k: int = None, sources: list = None):
    """Similarity search, optionally restricted to a subset of source files."""
    store = get_vector_store()
    k = k or config.TOP_K
    filter_dict = {"source": {"$in": sources}} if sources else None
    return store.similarity_search(query, k=k, filter=filter_dict)


def list_indexed_sources() -> list:
    """Return the sorted list of distinct filenames currently indexed."""
    store = get_vector_store()
    try:
        data = store.get()
        metadatas = data.get("metadatas", []) or []
        sources = sorted({m.get("source") for m in metadatas if m and m.get("source")})
        return sources
    except Exception:
        return []


def clear_collection():
    """Delete every embedded chunk from the collection (does not delete PDFs on disk)."""
    store = get_vector_store()
    try:
        ids = store.get().get("ids", [])
        if ids:
            store.delete(ids=ids)
    except Exception:
        pass
