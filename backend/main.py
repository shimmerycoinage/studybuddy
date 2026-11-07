from fastapi import FastAPI, Depends
from sqlalchemy import text
from database import engine, get_db
from sqlalchemy.orm import Session

app = FastAPI(title="StudyBuddy API")

@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint с проверкой БД"""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/")
async def root():
    return {"message": "StudyBuddy API is running"}