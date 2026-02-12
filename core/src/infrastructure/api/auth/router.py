from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from infrastructure.api.auth.schemas import Token, UserCreate, UserOut
from infrastructure.api.auth.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    verify_password,
)
from infrastructure.api.auth.security import get_current_user
from infrastructure.persistence.database import get_db
from infrastructure.persistence.models import User

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail='Email already registered')

    if len(payload.password.encode('utf-8')) > 72:
        raise HTTPException(status_code=400, detail='Password too long (max 72 bytes)')

    password_hash = get_password_hash(payload.password)
    if not verify_password(payload.password, password_hash):
        raise HTTPException(status_code=500, detail='Password hashing failed')

    user = User(email=payload.email, password_hash=password_hash)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = create_access_token(str(user.id))
    return Token(access_token=token)


@router.get('/me', response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user
