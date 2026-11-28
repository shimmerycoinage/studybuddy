from fastapi import FastAPI, Depends, HTTPException, Query, Response
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert
from database import engine, get_db
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session, aliased
from schema import (
    TokenResponse,
    UserCreate,
    UserLogin,
    UserRead,
    GroupCreate,
    GroupCreated,
    GroupListItem,
    GroupJoin,
    GroupDetail,
    QuestionCreate,
    QuestionRead,
    AnswerCreate,
    AnswerRead,
)
from models import Answer, Group, GroupMembership, Question, User
from security import create_access_token, hash_password, read_access_token, verify_password
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import secrets
from fastapi.middleware.cors import CORSMiddleware
from typing import Literal

app = FastAPI(title="StudyBuddy API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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

@app.post("/groups", response_model=GroupCreated, status_code=201)
def create_group(
    data: GroupCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = Group(
        name=data.name,
        description=data.description,
        invite_code=secrets.token_urlsafe(12),
    )

    try:
        db.add(group)
        db.flush()

        owner = GroupMembership(
            group_id=group.id,
            user_id=user.id,
            role="owner",
        )
        db.add(owner)

        result = GroupCreated(
            id=group.id,
            name=group.name,
            description=group.description,
            invite_code=group.invite_code,
            member_count=1,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        if exc.orig.diag.constraint_name == "groups_invite_code_key":
            raise HTTPException(
                status_code=503,
                detail="Не удалось подобрать код приглашения. Повтори создание группы.",
            ) from exc
        raise

    return result

@app.get("/groups", response_model=list[GroupListItem])
def list_my_groups(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    my_group_ids = select(GroupMembership.group_id).where(
        GroupMembership.user_id == user.id
    )

    query = (
        select(
            Group.id,
            Group.name,
            Group.description,
            func.count(GroupMembership.user_id).label("member_count"),
        )
        .join(GroupMembership, GroupMembership.group_id == Group.id)
        .where(Group.id.in_(my_group_ids))
        .group_by(Group.id, Group.name, Group.description)
        .order_by(Group.id)
    )

    return db.execute(query).mappings().all()

@app.post("/groups/join", status_code=201)
def join_group(
    data: GroupJoin,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, int]:
    group_query = select(Group.id).where(Group.invite_code == data.invite_code)
    group_id = db.execute(group_query).scalar_one_or_none()

    if group_id is None:
        raise HTTPException(status_code=404, detail="Группа с таким кодом не найдена")

    join_query = (
        insert(GroupMembership)
        .values(group_id=group_id, user_id=user.id, role="member")
        .on_conflict_do_nothing(index_elements=["group_id", "user_id"])
        .returning(GroupMembership.group_id)
    )
    joined_group_id = db.execute(join_query).scalar_one_or_none()

    if joined_group_id is None:
        raise HTTPException(status_code=409, detail="Ты уже состоишь в этой группе")

    db.commit()
    return {"group_id": joined_group_id}

@app.get("/groups/{group_id}", response_model=GroupDetail)
def get_group_detail(
    group_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    my_membership = aliased(GroupMembership)

    query = (
        select(
            Group.id,
            Group.name,
            Group.description,
            func.count(GroupMembership.user_id).label("member_count"),
            my_membership.role.label("my_role"),
        )
        .select_from(Group)
        .join(GroupMembership, GroupMembership.group_id == Group.id)
        .join(my_membership, my_membership.group_id == Group.id)
        .where(Group.id == group_id, my_membership.user_id == user.id)
        .group_by(Group.id, Group.name, Group.description, my_membership.role)
    )

    group = db.execute(query).mappings().one_or_none()
    if group is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    return group

@app.delete("/groups/{group_id}/membership", status_code=204, response_class=Response)
def leave_group(
    group_id: int,
    new_owner_id: int | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.get(Group, group_id, with_for_update=True)
    membership = db.get(GroupMembership, (group_id, user.id))

    if group is None or membership is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    if membership.role == "owner":
        if new_owner_id is None:
            raise HTTPException(
                status_code=409,
                detail="Чтобы выйти, выбери нового владельца из участников группы",
            )

        successor = db.get(GroupMembership, (group_id, new_owner_id))
        if successor is None or successor.role != "member":
            raise HTTPException(
                status_code=422,
                detail="Выбери другого участника этой группы",
            )

        successor.role = "owner"

    elif new_owner_id is not None:
        raise HTTPException(
            status_code=403,
            detail="Только владелец может передать права",
        )

    db.delete(membership)
    db.commit()
    return Response(status_code=204)

@app.delete("/groups/{group_id}/members/{user_id}", status_code=204, response_class=Response)
def remove_group_member(
    group_id: int,
    user_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.get(Group, group_id, with_for_update=True)
    my_membership = db.get(GroupMembership, (group_id, user.id))

    if group is None or my_membership is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    if my_membership.role != "owner":
        raise HTTPException(status_code=403, detail="Только владелец может удалять участников")

    if user_id == user.id:
        raise HTTPException(status_code=409, detail="Для выхода передай права новому владельцу")

    target = db.get(GroupMembership, (group_id, user_id))
    if target is None:
        raise HTTPException(status_code=404, detail="Участник не найден в группе")

    db.delete(target)
    db.commit()
    return Response(status_code=204)

@app.post("/groups/{group_id}/questions", status_code=201, response_model=QuestionRead)
def create_question(
    group_id: int,
    data: QuestionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    group = db.get(Group, group_id, with_for_update=True)
    membership = db.get(GroupMembership, (group_id, user.id))

    if group is None or membership is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    question = Question(
        group_id=group_id,
        author_id=user.id,
        body=data.body,
    )

    db.add(question)
    db.commit()
    db.refresh(question)
    return question

@app.get("/groups/{group_id}/questions", response_model=list[QuestionRead])
def list_group_questions(
    group_id: int,
    status: Literal["all", "unanswered", "resolved"] = "all",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    membership = db.get(GroupMembership, (group_id, user.id))
    if membership is None:
        raise HTTPException(status_code=404, detail="Группа не найдена")

    query = select(Question).where(Question.group_id == group_id)

    if status == "unanswered":
        has_answer = (
            select(Answer.id)
            .where(Answer.question_id == Question.id)
            .exists()
        )
        query = query.where(~has_answer)
    elif status == "resolved":
        query = query.where(Question.is_resolved.is_(True))

    offset = (page - 1) * page_size
    query = (
        query.order_by(Question.created_at.desc(), Question.id.desc())
        .offset(offset)
        .limit(page_size)
    )

    return db.scalars(query).all()

def get_accessible_question_id(question_id: int, user_id: int, db: Session, *, for_update: bool = False) -> int:
    query = (
        select(Question.id)
        .join(GroupMembership, GroupMembership.group_id == Question.group_id)
        .where(Question.id == question_id, GroupMembership.user_id == user_id)
        .with_for_update(read=not for_update)
    )
    target_question_id = db.scalar(query)

    if target_question_id is None:
        raise HTTPException(status_code=404, detail="Вопрос не найден")

    return target_question_id

@app.post("/questions/{question_id}/answers", status_code=201, response_model=AnswerRead)
def create_answer(
    question_id: int,
    data: AnswerCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_question_id = get_accessible_question_id(question_id, user.id, db)

    answer = Answer(
        question_id=target_question_id,
        author_id=user.id,
        body=data.body,
    )
    db.add(answer)
    db.flush()

    result = AnswerRead(
        id=answer.id,
        question_id=answer.question_id,
        body=answer.body,
        author_id=answer.author_id,
        author_name=user.name,
        created_at=answer.created_at,
    )
    db.commit()
    return result

@app.get("/questions/{question_id}/answers", response_model=list[AnswerRead])
def list_question_answers(
    question_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_question_id = get_accessible_question_id(question_id, user.id, db)

    query = (
        select(
            Answer.id,
            Answer.question_id,
            Answer.body,
            Answer.author_id,
            User.name.label("author_name"),
            Answer.created_at,
        )
        .select_from(Answer)
        .join(User, User.id == Answer.author_id)
        .where(Answer.question_id == target_question_id)
        .order_by(Answer.created_at.asc(), Answer.id.asc())
    )

    return db.execute(query).mappings().all()

@app.patch("/questions/{question_id}/resolve", response_model=QuestionRead)
def resolve_question(
    question_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    target_question_id = get_accessible_question_id(
        question_id, user.id, db, for_update=True
    )
    question = db.get(Question, target_question_id)

    if question.author_id != user.id:
        raise HTTPException(
            status_code=403,
            detail="Только автор вопроса может отметить его решённым",
        )

    question.is_resolved = True
    db.commit()
    db.refresh(question)
    return question