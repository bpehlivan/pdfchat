import shutil
from pathlib import Path
from pprint import pprint

from fastapi import UploadFile, HTTPException
from sqlmodel import Session

from app.models import PdfFile


async def save_upload_file(
    file_name: str,
    upload_file: UploadFile,
    db_session: Session,
    destination: Path = Path("static"),
) -> str:
    try:
        destination.mkdir(parents=True, exist_ok=True)

        file_extension = Path(upload_file.filename).suffix
        new_filename = f"{file_name}{file_extension}"

        file_path = destination / new_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        db_file = PdfFile(file_name=upload_file.filename, file_path=str(file_path))
        db_session.add(db_file)
        db_session.commit()
        db_session.refresh(db_file)

        return new_filename
    except Exception as e:
        pprint(e)
        db_session.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while saving the file: {str(e)}",
        )
