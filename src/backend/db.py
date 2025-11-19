from datetime import datetime
from pathlib import Path
from typing import Dict, List

from sqlalchemy import (
    Column,
    DateTime,
    Index,
    Integer,
    String,
    create_engine,
    func,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

Base = declarative_base()


class IndexedDocument(Base):
    __tablename__ = "indexed_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(String, unique=True, nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    filename = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_document_id", "document_id"),
    )


class Database:

    def __init__(self, db_path: str = "data/indexed_documents.db"):
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = db_path
        self.engine = create_engine(
            f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
        )

        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def _get_session(self) -> Session:
        return self.SessionLocal()

    def add_documents(
        self, user_id: str, document_ids: List[str], filename: str
    ) -> None:
        if not document_ids:
            return

        session = self._get_session()
        try:
            documents = [
                IndexedDocument(document_id=doc_id, user_id=user_id, filename=filename)
                for doc_id in document_ids
            ]
            session.add_all(documents)
            try:
                session.commit()
            except IntegrityError:
                session.rollback()
                for doc_id in document_ids:
                    try:
                        document = IndexedDocument(
                            document_id=doc_id, user_id=user_id, filename=filename
                        )
                        session.add(document)
                        session.commit()
                    except IntegrityError:
                        session.rollback()
                        continue
        finally:
            session.close()

    def get_user_files(self, user_id: str) -> List[Dict[str, any]]:
        session = self._get_session()
        try:
            results = (
                session.query(
                    IndexedDocument.filename,
                    func.count(IndexedDocument.id).label("count"),
                )
                .filter(IndexedDocument.user_id == user_id)
                .group_by(IndexedDocument.filename)
                .order_by(IndexedDocument.filename)
                .all()
            )
            return [{"filename": row.filename, "count": row.count} for row in results]
        finally:
            session.close()

    def get_user_document_ids(self, user_id: str) -> List[str]:
        session = self._get_session()
        try:
            results = (
                session.query(IndexedDocument.document_id)
                .filter(IndexedDocument.user_id == user_id)
                .all()
            )
            return [row.document_id for row in results]
        finally:
            session.close()

    def delete_user_documents(self, user_id: str) -> int:
        session = self._get_session()
        try:
            deleted_count = (
                session.query(IndexedDocument)
                .filter(IndexedDocument.user_id == user_id)
                .delete()
            )
            session.commit()
            return deleted_count
        finally:
            session.close()

    def delete_document_ids(self, document_ids: List[str]) -> int:
        if not document_ids:
            return 0

        session = self._get_session()
        try:
            deleted_count = (
                session.query(IndexedDocument)
                .filter(IndexedDocument.document_id.in_(document_ids))
                .delete(synchronize_session=False)
            )
            session.commit()
            return deleted_count
        finally:
            session.close()

    def get_user_document_count(self, user_id: str) -> int:
        session = self._get_session()
        try:
            count = (
                session.query(func.count(IndexedDocument.id))
                .filter(IndexedDocument.user_id == user_id)
                .scalar()
            )
            return count or 0
        finally:
            session.close()

    def close(self):
        if self.engine:
            self.engine.dispose()
