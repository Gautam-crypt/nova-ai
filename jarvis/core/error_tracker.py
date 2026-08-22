import traceback
from sqlalchemy.orm import Session
from jarvis.api.models import SystemError

class ErrorTracker:
    def __init__(self, db_conn: Session):
        self.db = db_conn
    
    def log(self, error: Exception, endpoint: str = "", user_id: str = ""):
        try:
            sys_error = SystemError(
                error_type=type(error).__name__,
                message=str(error),
                traceback=traceback.format_exc(),
                endpoint=endpoint,
                user_id=user_id
            )
            self.db.add(sys_error)
            self.db.commit()
            print(f"[ERROR_TRACKER] Logged: {type(error).__name__}: {str(error)[:100]}")
        except Exception as e:
            print(f"[ERROR_TRACKER] Failed to log error: {e}")
