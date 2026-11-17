from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import IntegrityError
from database import engine, get_db
from sqlalchemy import select, text
from sqlalchemy.orm import Session
from schema import TokenResponse, UserCreate, UserLogin, UserRead
from models.user import User
from security import create_access_token, hash_password, read_access_token, verify_password
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI(title="StudyBuddy API")
bearer_scheme = HTTPBearer(auto_error=False)

@app.exception_handler(RequestValidationError)
async def handle_validation_error(request, exc):
    errors = []

    for error in exc.errors():
        errors.append({
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        })

    return JSONResponse(status_code=422, content={"detail": errors})

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

@app.post("/register", status_code=201, response_model=UserRead)
def register(data: UserCreate, db: Session = Depends(get_db)):
    if len(data.password.encode("utf-8")) > 72:
        raise HTTPException(
            status_code=422,
            detail="Пароль должен занимать не более 72 байт в UTF-8",
        )
    hashed = hash_password(data.password)

    user = User(
        name=data.name,
        email=data.email,
        password_hash=hashed,
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if (
            exc.orig.pgcode == "23505"
            and exc.orig.diag.constraint_name == "ix_users_email"
        ):
            raise HTTPException(
                status_code=409,
                detail="Этот email уже зарегистрирован",
            ) from exc
        raise

    db.refresh(user)
    return {"id": user.id, "name": user.name, "email": user.email}

@app.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    query = select(User).where(User.email == data.email)
    user = db.execute(query).scalar_one_or_none()

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверный email или пароль")

    access_token = create_access_token(user.id)
    return {"access_token": access_token, "token_type": "bearer"}
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=401,
        detail="Требуется действительный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized

    try:
        user_id = read_access_token(credentials.credentials)
    except (InvalidTokenError, ValueError) as exc:
        raise unauthorized from exc

    user = db.get(User, user_id)
    if user is None:
        raise unauthorized

    return user


@app.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}