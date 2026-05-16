import uuid
from typing import Optional
from loguru import logger


class SessionManager:
    def __init__(self):
        self._sessions: dict[str, dict] = {}
        logger.info("SessionManager initialized")

    def get_or_create(self, session_id: Optional[str] = None) -> dict:
        if session_id and session_id in self._sessions:
            logger.debug(f"Session found: {session_id[:8]}...")
            return self._sessions[session_id]
        new_id = str(uuid.uuid4())
        self._sessions[new_id] = {
            "streak_count": 0,
            "streak_sum": 0,
            "last_quiz": None,
        }
        logger.info(f"New session created: {new_id[:8]}...")
        return self._sessions[new_id]

    def get_session_id(self, session_id: Optional[str] = None) -> str:
        for sid in self._sessions:
            if sid == session_id:
                logger.debug(f"Existing session resolved: {sid[:8]}...")
                return sid
        new_id = str(uuid.uuid4())
        self._sessions[new_id] = {
            "streak_count": 0,
            "streak_sum": 0,
            "last_quiz": None,
        }
        logger.info(f"New session created via resolve: {new_id[:8]}...")
        return new_id

    def __getitem__(self, session_id: str) -> dict:
        session = self._sessions.get(session_id)
        if session is None:
            logger.error(f"Session not found: {session_id[:8]}...")
            raise KeyError(session_id)
        return session

    def __contains__(self, session_id: str) -> bool:
        found = session_id in self._sessions
        if not found:
            logger.debug(f"Session check miss: {session_id[:8]}...")
        return found


sessions = SessionManager()
