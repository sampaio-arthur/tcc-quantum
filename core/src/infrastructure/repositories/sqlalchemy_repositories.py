from __future__ import annotations

from datetime import UTC, datetime
from math import sqrt

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from domain.entities import Chat, ChatMessage, Document, GroundTruth, MessageRole, SearchResult, User
from domain.ports import ChatRepositoryPort, DocumentRepositoryPort, GroundTruthRepositoryPort, PasswordResetRepositoryPort, UserRepositoryPort
from infrastructure.db.models import ChatMessageModel, ChatModel, DocumentModel, GroundTruthModel, PasswordResetModel, UserModel


def _cosine_score(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sqrt(sum(x * x for x in a)) or 1.0
    nb = sqrt(sum(y * y for y in b)) or 1.0
    return float(dot / (na * nb))


class SqlAlchemyUserRepository(UserRepositoryPort):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user: User) -> User:
        model = UserModel(
            email=user.email.lower().strip(),
            password_hash=user.password_hash,
            name=user.name,
            is_active=user.is_active,
            is_admin=user.is_admin,
        )
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            name=model.name,
            is_active=model.is_active,
            is_admin=model.is_admin,
            created_at=model.created_at,
        )

    def get_by_email(self, email: str) -> User | None:
        model = self.session.scalar(select(UserModel).where(UserModel.email == email.lower().strip()))
        if not model:
            return None
        return User(model.id, model.email, model.password_hash, model.name, model.is_active, model.is_admin, model.created_at)

    def get_by_id(self, user_id: int) -> User | None:
        model = self.session.get(UserModel, user_id)
        if not model:
            return None
        return User(model.id, model.email, model.password_hash, model.name, model.is_active, model.is_admin, model.created_at)

    def update_password_hash(self, user_id: int, password_hash: str) -> None:
        model = self.session.get(UserModel, user_id)
        if not model:
            return
        model.password_hash = password_hash
        self.session.commit()


class SqlAlchemyPasswordResetRepository(PasswordResetRepositoryPort):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, user_id: int, token_hash: str, expires_at: datetime) -> None:
        self.session.add(PasswordResetModel(user_id=user_id, token_hash=token_hash, expires_at=expires_at))
        self.session.commit()

    def consume_valid(self, token_hash: str, now: datetime) -> int | None:
        stmt = (
            select(PasswordResetModel)
            .where(
                and_(
                    PasswordResetModel.token_hash == token_hash,
                    PasswordResetModel.used_at.is_(None),
                    PasswordResetModel.expires_at > now,
                )
            )
            .order_by(PasswordResetModel.created_at.desc())
        )
        model = self.session.scalar(stmt)
        if not model:
            return None
        model.used_at = now
        user_id = model.user_id
        self.session.commit()
        return user_id


class SqlAlchemyChatRepository(ChatRepositoryPort):
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_chat(self, chat: Chat) -> Chat:
        model = ChatModel(user_id=chat.user_id, title=chat.title)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return Chat(model.id, model.user_id, model.title, model.created_at, model.updated_at, model.deleted_at)

    def list_chats(self, user_id: int, offset: int, limit: int) -> list[Chat]:
        stmt = (
            select(ChatModel)
            .where(ChatModel.user_id == user_id, ChatModel.deleted_at.is_(None))
            .order_by(ChatModel.updated_at.desc(), ChatModel.id.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.scalars(stmt).all()
        return [Chat(r.id, r.user_id, r.title, r.created_at, r.updated_at, r.deleted_at) for r in rows]

    def get_chat(self, user_id: int, chat_id: int) -> Chat | None:
        row = self.session.scalar(select(ChatModel).where(ChatModel.id == chat_id, ChatModel.user_id == user_id, ChatModel.deleted_at.is_(None)))
        if not row:
            return None
        return Chat(row.id, row.user_id, row.title, row.created_at, row.updated_at, row.deleted_at)

    def rename_chat(self, user_id: int, chat_id: int, title: str) -> Chat | None:
        row = self.session.scalar(select(ChatModel).where(ChatModel.id == chat_id, ChatModel.user_id == user_id, ChatModel.deleted_at.is_(None)))
        if not row:
            return None
        row.title = title or row.title
        self.session.commit()
        self.session.refresh(row)
        return Chat(row.id, row.user_id, row.title, row.created_at, row.updated_at, row.deleted_at)

    def soft_delete_chat(self, user_id: int, chat_id: int) -> bool:
        row = self.session.scalar(select(ChatModel).where(ChatModel.id == chat_id, ChatModel.user_id == user_id, ChatModel.deleted_at.is_(None)))
        if not row:
            return False
        row.deleted_at = datetime.now(UTC)
        self.session.commit()
        return True

    def create_message(self, message: ChatMessage) -> ChatMessage:
        model = ChatMessageModel(chat_id=message.chat_id, role=message.role.value, content=message.content)
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        chat = self.session.get(ChatModel, message.chat_id)
        if chat:
            chat.updated_at = datetime.now(UTC)
            self.session.commit()
        return ChatMessage(model.id, model.chat_id, MessageRole(model.role), model.content, model.created_at)

    def list_messages(self, user_id: int, chat_id: int, offset: int, limit: int) -> list[ChatMessage]:
        if not self.session.scalar(select(ChatModel.id).where(ChatModel.id == chat_id, ChatModel.user_id == user_id, ChatModel.deleted_at.is_(None))):
            return []
        stmt = select(ChatMessageModel).where(ChatMessageModel.chat_id == chat_id).order_by(ChatMessageModel.id.asc()).offset(offset).limit(limit)
        rows = self.session.scalars(stmt).all()
        return [ChatMessage(r.id, r.chat_id, MessageRole(r.role), r.content, r.created_at) for r in rows]


class SqlAlchemyDocumentRepository(DocumentRepositoryPort):
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert_documents(self, documents: list[Document]) -> int:
        count = 0
        for item in documents:
            row = self.session.scalar(select(DocumentModel).where(DocumentModel.dataset == item.dataset, DocumentModel.doc_id == item.doc_id))
            if row is None:
                row = DocumentModel(dataset=item.dataset, doc_id=item.doc_id, text=item.text)
                self.session.add(row)
            row.text = item.text
            row.metadata_json = item.metadata
            row.embedding_vector = item.embedding_vector
            row.quantum_vector = item.quantum_vector
            count += 1
        self.session.commit()
        return count

    def count_by_dataset(self, dataset: str) -> int:
        return len(self.list_document_ids(dataset))

    def list_document_ids(self, dataset: str) -> list[str]:
        return list(self.session.scalars(select(DocumentModel.doc_id).where(DocumentModel.dataset == dataset)))

    def search_by_embedding(self, dataset: str, query_vector: list[float], top_k: int) -> list[SearchResult]:
        return self._search(dataset, query_vector, top_k, field="embedding_vector")

    def search_by_quantum(self, dataset: str, query_vector: list[float], top_k: int) -> list[SearchResult]:
        return self._search(dataset, query_vector, top_k, field="quantum_vector")

    def _search(self, dataset: str, query_vector: list[float], top_k: int, field: str) -> list[SearchResult]:
        dialect = self.session.bind.dialect.name if self.session.bind else ""
        column = getattr(DocumentModel, field)
        if dialect == "postgresql" and hasattr(column, "cosine_distance"):
            stmt = (
                select(DocumentModel, (1 - column.cosine_distance(query_vector)).label("score"))
                .where(DocumentModel.dataset == dataset)
                .order_by(column.cosine_distance(query_vector))
                .limit(top_k)
            )
            rows = self.session.execute(stmt).all()
            return [
                SearchResult(doc_id=row.DocumentModel.doc_id, text=row.DocumentModel.text, score=float(row.score), metadata=row.DocumentModel.metadata_json or {})
                for row in rows
            ]
        rows = self.session.scalars(select(DocumentModel).where(DocumentModel.dataset == dataset)).all()
        scored = []
        for row in rows:
            vec = getattr(row, field)
            if vec is None:
                continue
            scored.append(
                SearchResult(
                    doc_id=row.doc_id,
                    text=row.text,
                    score=_cosine_score(query_vector, vec),
                    metadata=row.metadata_json or {},
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]


class SqlAlchemyGroundTruthRepository(GroundTruthRepositoryPort):
    def __init__(self, session: Session) -> None:
        self.session = session

    def upsert(self, item: GroundTruth) -> GroundTruth:
        row = self.session.scalar(select(GroundTruthModel).where(GroundTruthModel.dataset == item.dataset, GroundTruthModel.query_id == item.query_id))
        if row is None:
            row = GroundTruthModel(dataset=item.dataset, query_id=item.query_id)
            self.session.add(row)
        row.query_text = item.query_text
        row.relevant_doc_ids = item.relevant_doc_ids
        row.user_id = item.user_id
        self.session.commit()
        self.session.refresh(row)
        return GroundTruth(row.query_id, row.query_text, list(row.relevant_doc_ids or []), row.dataset, row.user_id, row.created_at)

    def get(self, dataset: str, query_id: str) -> GroundTruth | None:
        row = self.session.scalar(select(GroundTruthModel).where(GroundTruthModel.dataset == dataset, GroundTruthModel.query_id == query_id))
        if not row:
            return None
        return GroundTruth(row.query_id, row.query_text, list(row.relevant_doc_ids or []), row.dataset, row.user_id, row.created_at)

    def list_by_dataset(self, dataset: str) -> list[GroundTruth]:
        rows = self.session.scalars(select(GroundTruthModel).where(GroundTruthModel.dataset == dataset).order_by(GroundTruthModel.id.asc())).all()
        return [GroundTruth(r.query_id, r.query_text, list(r.relevant_doc_ids or []), r.dataset, r.user_id, r.created_at) for r in rows]

    def delete(self, dataset: str, query_id: str) -> bool:
        row = self.session.scalar(select(GroundTruthModel).where(GroundTruthModel.dataset == dataset, GroundTruthModel.query_id == query_id))
        if row is None:
            return False
        self.session.delete(row)
        self.session.commit()
        return True
