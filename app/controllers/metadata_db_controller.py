from pathlib import Path
from typing import Iterable

from loguru import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.models.metadata.metadata_db import AuxMetadataEntry, Base
from app.utils.app_info import AppInfo


class MetadataDbController:
    def __init__(self, db: Path | str) -> None:
        self.engine = create_engine(f"sqlite+pysqlite:///{db}")
        self.Session = sessionmaker(bind=self.engine, expire_on_commit=False)


class AuxMetadataController(MetadataDbController):
    def __init__(self) -> None:
        super().__init__(AppInfo().aux_metadata_db)
        Base.metadata.create_all(self.engine)

    @staticmethod
    def get(session: Session, item_path: Path | str) -> AuxMetadataEntry | None:
        """Get an aux metadata entry by the key path.

        :param session: The database session.
        :type session: Session
        :param item_path: The key path.
        :type item_path: Path | str
        :return: The aux metadata entry if found, otherwise None.
        :rtype: AuxMetadataEntry | None
        """
        if isinstance(item_path, Path):
            item_path = str(item_path)

        return (
            session.query(AuxMetadataEntry)
            .filter(AuxMetadataEntry.path == item_path)
            .first()
        )

    @staticmethod
    def get_or_create(session: Session, item_path: Path | str) -> AuxMetadataEntry:
        """Get or create an aux metadata entry by the key path.

        :param session: The database session.
        :type session: Session
        :param item_path: The key path.
        :type item_path: Path | str
        :return: The aux metadata entry.
        :rtype: AuxMetadataEntry
        """

        if isinstance(item_path, Path):
            item_path = str(item_path)

        entry = AuxMetadataController.get(session, item_path)

        if entry is None:
            entry = AuxMetadataEntry(path=item_path)
            try:
                with session.begin_nested():
                    session.add(entry)
                    session.flush()
            except Exception as e:
                session.rollback()
                logger.exception(f"Failed to create new aux metadata entry: {e}")
                raise e

        return entry

    @staticmethod
    def get_value_equals(
        session: Session, key: str, value: str
    ) -> list[AuxMetadataEntry]:
        """Get aux metadata entries where the key equals the value.

        :param session: The database session.
        :type session: Session
        :param key: The key to search for.
        :type key: str
        :param value: The value to search for.
        :type value: str
        :return: A list of aux metadata entries.
        :rtype: list[AuxMetadataEntry
        """
        return (
            session.query(AuxMetadataEntry)
            .filter(getattr(AuxMetadataEntry, key) == value)
            .all()
        )

    @staticmethod
    def query(session: Session, query: str) -> list[AuxMetadataEntry]:
        """Query the aux metadata entries.

        :param session: The database session.
        :type session: Session
        :param query: The query string.
        :type query: str
        :return: A list of aux metadata entries.
        :rtype: list[AuxMetadataEntry]
        """
        result = session.execute(text(query)).all()
        return [AuxMetadataEntry(**row._mapping) for row in result]

    @staticmethod
    def add(
        session: Session, item: AuxMetadataEntry | Iterable[AuxMetadataEntry]
    ) -> None:
        """Add an aux metadata entry or entries to the database.

        :param session: The database session.
        :type session: Session
        :param item: The aux metadata entry or entries to add.
        :type item: AuxMetadataEntry | Iterable[AuxMetadataEntry]
        """
        if isinstance(item, AuxMetadataEntry):
            session.add(item)
        else:
            session.add_all(item)
        session.commit()

    def reset(self) -> None:
        """Reset the database by dropping all tables and recreating them."""
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
