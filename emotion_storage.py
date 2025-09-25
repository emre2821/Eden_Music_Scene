"""Persistence layer for emotion tags."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sqlalchemy import Column, Float, MetaData, String, Table, Text, create_engine, delete, select, update
from sqlalchemy.engine import Engine


metadata = MetaData()


tags_table = Table(
    "emotion_tags",
    metadata,
    Column("id", String(64), primary_key=True),
    Column("track_id", String(255), nullable=False),
    Column("emotion", String(255), nullable=False),
    Column("intensity", Float, nullable=True),
    Column("notes", Text, nullable=True),
    Column("user_id", String(255), nullable=True),
)


@dataclass
class DatabaseTagStore:
    """SQL-backed persistence for emotion tags."""

    database_url: Optional[str] = None

    def __post_init__(self) -> None:
        self._engine: Engine = create_engine(self.database_url or "sqlite:///emotion_tags.db", future=True)
        metadata.create_all(self._engine)

    def close(self) -> None:
        """Dispose of the underlying engine."""

        self._engine.dispose()

    # ------------------------------------------------------------------
    # CRUD operations
    # ------------------------------------------------------------------
    def list_tags(self) -> List[Dict[str, Any]]:
        """Return all stored tags ordered by identifier."""

        with self._engine.begin() as conn:
            result = conn.execute(select(tags_table).order_by(tags_table.c.id))
            rows = result.mappings().all()
        return [self._row_to_payload(row) for row in rows]

    def get_tag(self, tag_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a single tag by identifier."""

        with self._engine.begin() as conn:
            row = conn.execute(
                select(tags_table).where(tags_table.c.id == tag_id)
            ).mappings().first()
        return self._row_to_payload(row) if row else None

    def upsert_tag(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Insert or update a tag and return the persisted representation."""

        cleaned = self._prepare_for_storage(payload)
        with self._engine.begin() as conn:
            existing = conn.execute(
                select(tags_table.c.id).where(tags_table.c.id == cleaned["id"])
            ).scalar_one_or_none()
            if existing:
                conn.execute(
                    update(tags_table)
                    .where(tags_table.c.id == cleaned["id"])
                    .values(**cleaned)
                )
            else:
                conn.execute(tags_table.insert().values(**cleaned))

            row = conn.execute(
                select(tags_table).where(tags_table.c.id == cleaned["id"])
            ).mappings().first()
        if not row:
            raise RuntimeError("Failed to persist tag")
        return self._row_to_payload(row)

    def clear(self) -> None:
        """Remove all stored tags."""

        with self._engine.begin() as conn:
            conn.execute(delete(tags_table))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _prepare_for_storage(payload: Dict[str, Any]) -> Dict[str, Any]:
        allowed = {"id", "track_id", "emotion", "intensity", "notes", "user_id"}
        cleaned = {key: payload.get(key) for key in allowed if key in payload}
        return cleaned

    @staticmethod
    def _row_to_payload(row: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if row is None:
            return {}
        payload = {k: v for k, v in row.items() if v is not None}
        return payload
