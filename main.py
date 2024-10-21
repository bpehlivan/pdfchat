import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, HTTPException, Depends
from langchain_core.load import load
from pydantic import BaseModel
from sqlmodel import Session

from app.database import create_db_and_tables, get_db_session, async_engine
from app.models import PdfFile
from app.utils import save_upload_file


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Create the database and tables when the app starts
    """
    await create_db_and_tables()
    try:
        yield
    finally:
        await async_engine.dispose()
        print("Application is shutting down...")


app = FastAPI(lifespan=lifespan)

@app.on_event("shutdown")
async def shutdown_event():
    print("Application is shutting down...")

@app.get("/hello")
async def hello_world():
    return {"hello": "world"}


@app.post("/pdf/upload")
async def pdf_upload(
    file: UploadFile,
    db_session: Session = Depends(get_db_session),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a PDF.",
        )

    file_uuid = str(uuid.uuid4())
    await save_upload_file(
        file_id=file_uuid,
        upload_file=file,
        db_session=db_session,
    )
    return {"pdf_id": file_uuid}


class ChatRequest(BaseModel):
    query: str


@app.post("/pdf/{pdf_id}/chat/")
async def pdf_chat(
    pdf_id: str,
    request: ChatRequest,
    db_session: Session = Depends(get_db_session),
):
    pdf_file = await db_session.get(PdfFile, pdf_id)
    if not pdf_file:
        raise HTTPException(status_code=404, detail="PDF not found")

    langchain = load(pdf_file.langchain)
    answer = langchain.run(request.query)

    return {"query": request.query, "answer": answer}

