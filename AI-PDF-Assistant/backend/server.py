"""
AI PDF Assistant - FastAPI backend.

Replaces the old Gradio UI (app.py) with a small JSON API that a custom
static frontend (see static/) talks to. Reuses the existing pdf_loader,
vectorstore, and llm modules untouched.

Run with:
    python server.py
or:
    uvicorn server:app --host 0.0.0.0 --port 8000

The server binds to 0.0.0.0 so it's reachable over your LAN or through a
tunnel (ngrok / Cloudflare Tunnel) if you deploy the frontend elsewhere and
point it at this machine. See README.md for deployment notes.
"""

import os

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend import config

from backend import llm
from backend import pdf_loader
from backend import vectorstore

app = FastAPI(title=config.APP_TITLE)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_TMP_DIR = os.path.join(config.BASE_DIR, "data", "uploads_tmp")
os.makedirs(UPLOAD_TMP_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    return {"status": "ok", "title": config.APP_TITLE}


@app.get("/api/sources")
def get_sources():
    return {"sources": vectorstore.list_indexed_sources()}


@app.post("/api/upload")
async def upload_pdfs(files: list[UploadFile] = File(...)):
    results = []
    for upload in files:
        if not upload.filename.lower().endswith(".pdf"):
            results.append({"filename": upload.filename, "ok": False, "error": "Not a PDF file."})
            continue

        tmp_path = os.path.join(UPLOAD_TMP_DIR, upload.filename)
        try:
            data = await upload.read()
            with open(tmp_path, "wb") as f:
                f.write(data)

            chunks = pdf_loader.process_pdf(tmp_path)
            vectorstore.index_documents(chunks)
            results.append({"filename": upload.filename, "ok": True, "chunks": len(chunks)})
        except Exception as e:
            results.append({"filename": upload.filename, "ok": False, "error": str(e)})
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return {"results": results, "sources": vectorstore.list_indexed_sources()}


@app.delete("/api/sources")
def clear_sources():
    vectorstore.clear_collection()
    return {"sources": vectorstore.list_indexed_sources()}


@app.post("/api/chat")
def chat(req: ChatRequest):
    message = (req.message or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message is empty.")

    sources = vectorstore.list_indexed_sources()
    if not sources:
        def empty_stream():
            yield "Please upload and index a PDF first."
        return StreamingResponse(empty_stream(), media_type="text/plain")

    docs = vectorstore.search(message)
    if not docs:
        def no_info_stream():
            yield "I don't have that information."
        return StreamingResponse(no_info_stream(), media_type="text/plain")

    def token_stream():
        for token in llm.stream_answer(message, docs):
            yield token

    return StreamingResponse(token_stream(), media_type="text/plain")


# ---------------------------------------------------------------------------
# Static frontend (optional)
# ---------------------------------------------------------------------------
# backend/ and frontend/ are separate modules — the frontend can be deployed
# on its own (Netlify, Vercel, etc.) and just needs BACKEND_URL pointed at
# wherever this API is running. Serving it here too is a convenience for
# local development: `python server.py` then open http://localhost:8000.
FRONTEND_DIR = os.path.join(os.path.dirname(config.BASE_DIR), "frontend")
if os.path.isdir(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
else:
    print(f"[server] Note: frontend/ not found at {FRONTEND_DIR} — API-only mode.")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=config.APP_PORT, reload=False)
