from pathlib import PureWindowsPath
from zipfile import BadZipFile, ZipFile

from fastapi import HTTPException, UploadFile


MAX_FILE_BYTES = 10 * 1024 * 1024

SIGNATURES = {
    ".pdf": b"%PDF-",
    ".png": b"\x89PNG\r\n\x1a\n",
    ".jpg": b"\xff\xd8\xff",
}

OFFICE_DOCUMENTS = {
    ".docx": "word/document.xml",
    ".pptx": "ppt/presentation.xml",
}


def check_material_file(file: UploadFile) -> tuple[str, int]:
    name = PureWindowsPath(file.filename or "").name
    suffix = PureWindowsPath(name).suffix.lower()

    if not name or not name.isprintable():
        raise HTTPException(status_code=422, detail="Некорректное имя файла")

    size = file.file.seek(0, 2)
    file.file.seek(0)
    if size > MAX_FILE_BYTES:
        raise HTTPException(status_code=413, detail="Файл превышает 10 МиБ")

    if suffix in SIGNATURES:
        prefix = file.file.read(8)
        valid = prefix.startswith(SIGNATURES[suffix])
    elif suffix in OFFICE_DOCUMENTS:
        try:
            with ZipFile(file.file) as archive:
                entries = set(archive.namelist())
                valid = "[Content_Types].xml" in entries and OFFICE_DOCUMENTS[suffix] in entries
        except BadZipFile:
            valid = False
    else:
        valid = False

    if not valid:
        raise HTTPException(status_code=415, detail="Допустимы PDF, DOCX, PPTX, PNG и JPG")

    file.file.seek(0)
    return name, size