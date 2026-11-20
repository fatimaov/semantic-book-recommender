import logging
from typing import Any

from ..extensions import db
from ..models.search_event import SearchEvent


logger = logging.getLogger(__name__)


class SearchEventService:
    """Persist search analytics without allowing logging failures to escape."""

    def __init__(self, session: Any | None = None) -> None:
        self.session = session if session is not None else db.session

    def log_search(self, query: str, category: str, emotion: str) -> bool:
        try:
            event = SearchEvent(query=query, category=category, emotion=emotion)
            self.session.add(event)
            self.session.commit()
            return True
        except Exception:
            try:
                self.session.rollback()
            except Exception:
                logger.exception("Could not roll back a failed search event write.")
            logger.exception("Could not persist search event.")
            return False
