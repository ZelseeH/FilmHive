from app.extensions import db
from app.models.notification import Notification
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from flask import current_app


class NotificationRepository:

    @staticmethod
    def create(
        user_id: int,
        from_user_id: int,
        comment_id: int,
        message: str,
        reply_id: Optional[int] = None,
    ) -> Optional[Notification]:
        """Tworzy nowe powiadomienie z walidacją duplikatów"""
        try:
            current_app.logger.info(
                f"🔍 REPO: Creating notification for user {user_id} from {from_user_id}"
            )

            # Sprawdź duplikaty BEZ notification_type
            existing = Notification.query.filter_by(
                user_id=user_id,
                from_user_id=from_user_id,
                comment_id=comment_id,
                reply_id=reply_id,
            ).first()

            if existing:
                current_app.logger.info(
                    f"🔍 REPO: Duplicate notification exists, skipping"
                )
                return None

            # Tworz BEZ notification_type
            notification = Notification(
                user_id=user_id,
                from_user_id=from_user_id,
                comment_id=comment_id,
                reply_id=reply_id,
                message=message,
                is_read=False,
            )

            db.session.add(notification)
            db.session.flush()
            db.session.refresh(notification)

            current_app.logger.info(
                f"🔍 REPO: Notification created with ID {notification.notification_id}"
            )
            return notification

        except IntegrityError as e:
            current_app.logger.warning(
                f"IntegrityError during notification create: {e}"
            )
            db.session.rollback()
            return None
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {e}")
            db.session.rollback()
            return None

    @staticmethod
    def get_by_user(user_id: int, limit: int = 50) -> List[Notification]:
        """Pobiera powiadomienia użytkownika"""
        return (
            Notification.query.filter_by(user_id=user_id)
            .order_by(Notification.created_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_comment(comment_id: int) -> List[Notification]:
        """Pobiera wszystkie powiadomienia związane z komentarzem"""
        return (
            Notification.query.filter_by(comment_id=comment_id)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def get_unread_by_user(user_id: int) -> List[Notification]:
        """Pobiera nieprzeczytane powiadomienia"""
        return (
            Notification.query.filter_by(user_id=user_id, is_read=False)
            .order_by(Notification.created_at.desc())
            .all()
        )

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Pobiera liczbę nieprzeczytanych powiadomień"""
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Oznacza powiadomienie jako przeczytane"""
        notification = Notification.query.filter_by(
            notification_id=notification_id,
            user_id=user_id,
        ).first()

        if notification:
            notification.is_read = True
            return True
        return False

    @staticmethod
    def mark_all_as_read(user_id: int) -> int:
        """Oznacza wszystkie powiadomienia jako przeczytane"""
        count = Notification.query.filter_by(user_id=user_id, is_read=False).update(
            {Notification.is_read: True}
        )
        return count

    @staticmethod
    def get_by_id(notification_id: int) -> Optional[Notification]:
        """Pobiera powiadomienie po ID"""
        return Notification.query.filter_by(notification_id=notification_id).first()

    @staticmethod
    def commit():
        """Zapisuje zmiany do bazy"""
        try:
            db.session.commit()
            current_app.logger.info("🔍 REPO: Committed successfully")
        except Exception as e:
            current_app.logger.error(f"🔍 REPO: Commit failed: {e}")
            db.session.rollback()
            raise

    @staticmethod
    def rollback():
        """Wycofuje zmiany"""
        try:
            db.session.rollback()
            current_app.logger.info("🔍 REPO: Rollback successful")
        except Exception as e:
            current_app.logger.error(f"🔍 REPO: Rollback failed: {e}")
