from fastapi import FastAPI

app = FastAPI(title="StudyBuddy API")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/")
async def root():
    return {"message": "StudyBuddy API is running"}