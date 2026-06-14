"""Base repository with shared database session."""

from sqlalchemy.orm import Session


class BaseRepository:
    """Common repository base class."""

    def __init__(self, db: Session) -> None:
        self.db = db
