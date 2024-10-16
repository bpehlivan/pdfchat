import shutil
from pathlib import Path
from pprint import pprint

import PyPDF2
from fastapi import UploadFile, HTTPException
from langchain import hub
from langchain.chains.retrieval import create_retrieval_chain
from langchain.vectorstores import Qdrant
from langchain_core.load import dumpd
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlmodel import Session

from app.models import PdfFile
from settings import settings


async def save_upload_file(
    file_id: str,
    upload_file: UploadFile,
    db_session: Session,
    destination: Path = Path("static"),
) -> PdfFile:
    try:
        destination.mkdir(parents=True, exist_ok=True)

        file_extension = Path(upload_file.filename).suffix
        new_filename = f"{file_id}{file_extension}"

        file_path = destination / new_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        chain = process_pdf_for_chat(upload_file.file, file_id=file_id)
        chain_dict = dumpd(chain)

        db_file = PdfFile(
            file_name=upload_file.filename,
            file_path=str(file_path),
            langchain=chain_dict,
        )
        db_session.add(db_file)
        await db_session.commit()
        await db_session.refresh(db_file)

        return db_file
    except Exception as e:
        pprint(e)
        await db_session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while saving the file: {str(e)}",
        )


def create_embeddings_for_text(text: str, collection_name: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_text(text)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        api_key=settings.GOOGLE_API_KEY,
    )
    vectorstore = Qdrant.from_texts(
        texts=chunks,
        embedding=embeddings,
        url=f"http://{settings.qdrant_host}:{settings.qdrant_port}",
        collection_name=collection_name,
    )

    return vectorstore

def extract_text_from_pdf(file) -> str:
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    return text


def setup_retrieval_chain(vectorstore):
    ## See full prompt at https://smith.langchain.com/hub/langchain-ai/retrieval-qa-chat
    prompt = hub.pull("langchain-ai/retrieval-qa-chat")

    retriever = vectorstore.as_retriever()
    retrieval_chain = create_retrieval_chain(retriever, prompt)

    return retrieval_chain

def process_pdf_for_chat(file, file_id: str):
    text = extract_text_from_pdf(file)
    vector_store = create_embeddings_for_text(text, collection_name=file_id)
    return setup_retrieval_chain(vector_store)
