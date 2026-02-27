from __future__ import annotations

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from application.auth_use_cases import (
    ConfirmPasswordResetUseCase,
    RefreshTokenUseCase,
    RequestPasswordResetUseCase,
    SignInUseCase,
    SignUpUseCase,
)
from application.chat_use_cases import AddMessageUseCase, CreateChatUseCase, DeleteChatUseCase, GetChatUseCase, ListChatsUseCase, RenameChatUseCase
from application.ir_use_cases import BuildAssistantRetrievalMessageUseCase, EvaluateUseCase, IndexDatasetUseCase, SearchUseCase, UpsertGroundTruthUseCase
from domain.exceptions import UnauthorizedError
from infrastructure.config import Settings, get_settings
from infrastructure.datasets.beir_local_provider import BeirLocalDatasetProvider
from infrastructure.db.session import db_session
from infrastructure.email.dev_notifier import DevLogNotifier
from infrastructure.encoders.classical import SbertEncoder
from infrastructure.encoders.quantum import PennyLaneQuantumEncoder
from infrastructure.metrics.sklearn_metrics import SklearnMetricsAdapter
from infrastructure.repositories.sqlalchemy_repositories import (
    SqlAlchemyChatRepository,
    SqlAlchemyDatasetSnapshotRepository,
    SqlAlchemyDocumentRepository,
    SqlAlchemyGroundTruthRepository,
    SqlAlchemyPasswordResetRepository,
    SqlAlchemyUserRepository,
)
from infrastructure.security.adapters import BcryptPasswordHasher, JoseJwtProvider, Sha256ResetTokenGenerator

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


@dataclass(slots=True)
class Services:
    settings: Settings
    users: SqlAlchemyUserRepository
    chats: SqlAlchemyChatRepository
    documents: SqlAlchemyDocumentRepository
    dataset_snapshots: SqlAlchemyDatasetSnapshotRepository
    ground_truths: SqlAlchemyGroundTruthRepository
    sign_up: SignUpUseCase
    sign_in: SignInUseCase
    request_reset: RequestPasswordResetUseCase
    confirm_reset: ConfirmPasswordResetUseCase
    refresh: RefreshTokenUseCase
    create_chat: CreateChatUseCase
    list_chats: ListChatsUseCase
    get_chat: GetChatUseCase
    add_message: AddMessageUseCase
    rename_chat: RenameChatUseCase
    delete_chat: DeleteChatUseCase
    index_dataset: IndexDatasetUseCase
    search: SearchUseCase
    upsert_ground_truth: UpsertGroundTruthUseCase
    evaluate: EvaluateUseCase
    build_assistant_message: BuildAssistantRetrievalMessageUseCase
    jwt: JoseJwtProvider


def build_services(session: Session, settings: Settings) -> Services:
    users = SqlAlchemyUserRepository(session)
    resets = SqlAlchemyPasswordResetRepository(session)
    chats = SqlAlchemyChatRepository(session)
    docs = SqlAlchemyDocumentRepository(session)
    dataset_snaps = SqlAlchemyDatasetSnapshotRepository(session)
    gts = SqlAlchemyGroundTruthRepository(session)

    hasher = BcryptPasswordHasher()
    jwt = JoseJwtProvider(settings)
    notifier = DevLogNotifier()
    reset_tokens = Sha256ResetTokenGenerator()
    embedding_encoder = SbertEncoder(settings.classical_model_name, settings.embedding_dim)
    quantum_encoder = PennyLaneQuantumEncoder(settings.quantum_n_qubits)
    datasets = BeirLocalDatasetProvider()
    metrics = SklearnMetricsAdapter()

    search_uc = SearchUseCase(docs, embedding_encoder, quantum_encoder)
    return Services(
        settings=settings,
        users=users,
        chats=chats,
        documents=docs,
        ground_truths=gts,
        sign_up=SignUpUseCase(users, hasher),
        sign_in=SignInUseCase(users, hasher, jwt),
        request_reset=RequestPasswordResetUseCase(users, resets, reset_tokens, notifier, settings.password_reset_expire_minutes),
        confirm_reset=ConfirmPasswordResetUseCase(users, resets, reset_tokens, hasher),
        refresh=RefreshTokenUseCase(jwt),
        create_chat=CreateChatUseCase(chats),
        list_chats=ListChatsUseCase(chats),
        get_chat=GetChatUseCase(chats),
        add_message=AddMessageUseCase(chats),
        rename_chat=RenameChatUseCase(chats),
        delete_chat=DeleteChatUseCase(chats),
        index_dataset=IndexDatasetUseCase(datasets, docs, embedding_encoder, quantum_encoder, dataset_snaps, gts),
        search=search_uc,
        upsert_ground_truth=UpsertGroundTruthUseCase(gts),
        evaluate=EvaluateUseCase(gts, search_uc, metrics),
        build_assistant_message=BuildAssistantRetrievalMessageUseCase(),
        dataset_snapshots=dataset_snaps,
        jwt=jwt,
    )


def get_services(session: Session = Depends(db_session), settings: Settings = Depends(get_settings)) -> Services:
    return build_services(session, settings)


def get_current_user_id(
    token: str | None = Depends(oauth2_scheme),
    services: Services = Depends(get_services),
) -> int:
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        claims = services.jwt.decode_token(token)
    except UnauthorizedError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    if claims.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    sub = claims.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")
    return int(sub)
