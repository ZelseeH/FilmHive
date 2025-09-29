from app.repositories.notification_repository import NotificationRepository
from app.models.user import User
from typing import Dict, List, Optional
from flask import current_app


class NotificationService:

    @staticmethod
    def create_notification(
        user_id: int,
        from_user_id: int,
        comment_id: Optional[int] = None,
        reply_id: Optional[int] = None,
        message: str = "",
    ) -> Dict:
        """Tworzy nowe powiadomienie z walidacją samopowiadomień"""
        try:
            if user_id == from_user_id:
                current_app.logger.info(
                    f"🔍 NOTIFICATION: Skipping self-notification for user {user_id}"
                )
                return {
                    "success": True,
                    "message": "Self-notification skipped",
                    "skipped": True,
                }

            current_app.logger.info(
                f"🔍 NOTIFICATION: Creating notification user_id={user_id}, from_user_id={from_user_id}"
            )

            from_user = User.query.get(from_user_id)
            if not from_user:
                return {"success": False, "error": "From user not found"}

            to_user = User.query.get(user_id)
            if not to_user:
                return {"success": False, "error": "To user not found"}

            if (
                hasattr(to_user, "notifications_enabled")
                and not to_user.notifications_enabled
            ):
                current_app.logger.info(
                    f"🔍 NOTIFICATION: User {user_id} has notifications disabled"
                )
                return {
                    "success": True,
                    "message": "User has notifications disabled",
                    "disabled": True,
                }

            # BEZ notification_type - tylko relacje
            notification = NotificationRepository.create(
                user_id=user_id,
                from_user_id=from_user_id,
                comment_id=comment_id,
                reply_id=reply_id,
                message=message,
            )

            if notification:
                NotificationRepository.commit()
                current_app.logger.info(
                    f"🔍 NOTIFICATION: Successfully created notification ID={notification.notification_id}"
                )

                return {
                    "success": True,
                    "notification": (
                        notification.serialize(include_users=True, include_movie=True)
                        if hasattr(notification, "serialize")
                        else None
                    ),
                    "message": "Notification created successfully",
                }
            else:
                return {
                    "success": True,
                    "message": "Notification already exists (duplicate skipped)",
                    "duplicate": True,
                }

        except Exception as e:
            current_app.logger.error(f"Error creating notification: {e}")
            NotificationRepository.rollback()
            return {"success": False, "error": "Failed to create notification"}

    @staticmethod
    def create_comment_notification(
        comment_author_id: int,
        comment_id: int,
        target_user_id: int,
        from_username: str,
        movie_title: str,
    ) -> Dict:
        """Tworzy powiadomienie o nowym komentarzu - movie_title z relacji"""
        message = f"{from_username} skomentował film '{movie_title}'"

        return NotificationService.create_notification(
            user_id=target_user_id,
            from_user_id=comment_author_id,
            comment_id=comment_id,
            message=message,
        )

    @staticmethod
    def create_reply_notification(
        reply_author_id: int,
        comment_id: int,
        reply_id: int,
        target_user_id: int,
        from_username: str,
        movie_title: str,
    ) -> Dict:
        """Tworzy powiadomienie o odpowiedzi na komentarz"""
        message = f"{from_username} odpowiedział na Twój komentarz w '{movie_title}'"

        return NotificationService.create_notification(
            user_id=target_user_id,
            from_user_id=reply_author_id,
            comment_id=comment_id,
            reply_id=reply_id,
            message=message,
        )

    @staticmethod
    def get_user_notifications(
        user_id: int, limit: int = 50, include_movie: bool = True
    ) -> Dict:
        """Pobiera powiadomienia użytkownika z movie_id z relacji"""
        try:
            notifications = NotificationRepository.get_by_user(user_id, limit)

            return {
                "success": True,
                "data": {
                    "notifications": [
                        n.serialize(include_users=True, include_movie=include_movie)
                        for n in notifications
                    ],
                    "total_count": len(notifications),
                    "unread_count": len([n for n in notifications if not n.is_read]),
                },
            }

        except Exception as e:
            current_app.logger.error(f"Error getting notifications: {e}")
            return {
                "success": False,
                "error": "Wystąpił błąd podczas pobierania powiadomień",
            }

    @staticmethod
    def get_unread_notifications(user_id: int) -> Dict:
        """Pobiera nieprzeczytane powiadomienia"""
        try:
            notifications = NotificationRepository.get_unread_by_user(user_id)

            return {
                "success": True,
                "data": {
                    "notifications": [
                        n.serialize(include_users=True, include_movie=True)
                        for n in notifications
                    ],
                    "count": len(notifications),
                },
            }

        except Exception as e:
            current_app.logger.error(f"Error getting unread notifications: {e}")
            return {
                "success": False,
                "error": "Wystąpił błąd podczas pobierania powiadomień",
            }

    @staticmethod
    def get_by_comment(comment_id: int) -> List[Dict]:
        """Pobiera wszystkie powiadomienia związane z komentarzem"""
        try:
            notifications = NotificationRepository.get_by_comment(comment_id)
            return [
                n.serialize(include_users=True, include_movie=True)
                for n in notifications
            ]
        except Exception as e:
            current_app.logger.error(f"Error getting notifications by comment: {e}")
            return []

    @staticmethod
    def mark_notification_as_read(notification_id: int, user_id: int) -> Dict:
        """Oznacza powiadomienie jako przeczytane"""
        try:
            success = NotificationRepository.mark_as_read(notification_id, user_id)

            if success:
                NotificationRepository.commit()
                return {
                    "success": True,
                    "message": "Powiadomienie oznaczone jako przeczytane",
                }
            else:
                return {
                    "success": False,
                    "error": "Powiadomienie nie istnieje lub nie należy do użytkownika",
                }

        except Exception as e:
            current_app.logger.error(f"Error marking notification as read: {e}")
            NotificationRepository.rollback()
            return {
                "success": False,
                "error": "Wystąpił błąd podczas oznaczania powiadomienia",
            }

    @staticmethod
    def mark_all_as_read(user_id: int) -> Dict:
        """Oznacza wszystkie powiadomienia użytkownika jako przeczytane"""
        try:
            count = NotificationRepository.mark_all_as_read(user_id)
            NotificationRepository.commit()

            return {
                "success": True,
                "message": f"Oznaczono {count} powiadomień jako przeczytane",
                "marked_count": count,
            }

        except Exception as e:
            current_app.logger.error(f"Error marking all notifications as read: {e}")
            NotificationRepository.rollback()
            return {
                "success": False,
                "error": "Wystąpił błąd podczas oznaczania powiadomień",
            }

    @staticmethod
    def get_notification_stats(user_id: int) -> Dict:
        """Pobiera statystyki powiadomień użytkownika"""
        try:
            all_notifications = NotificationRepository.get_by_user(user_id)
            unread_notifications = NotificationRepository.get_unread_by_user(user_id)

            return {
                "success": True,
                "data": {
                    "total_count": len(all_notifications),
                    "unread_count": len(unread_notifications),
                    "read_count": len(all_notifications) - len(unread_notifications),
                },
            }

        except Exception as e:
            current_app.logger.error(f"Error getting notification stats: {e}")
            return {
                "success": False,
                "error": "Wystąpił błąd podczas pobierania statystyk",
            }

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Pobiera liczbę nieprzeczytanych powiadomień (prosty int)"""
        return NotificationRepository.get_unread_count(user_id)

    @staticmethod
    def bulk_create_notifications(notifications_data: List[Dict]) -> Dict:
        """Tworzy wiele powiadomień naraz z walidacją"""
        try:
            created_count = 0
            skipped_count = 0

            for notif_data in notifications_data:
                # Usuń niepotrzebne pola jeśli są
                notif_data.pop("notification_type", None)
                notif_data.pop("type", None)

                result = NotificationService.create_notification(**notif_data)
                if (
                    result.get("success")
                    and not result.get("skipped")
                    and not result.get("disabled")
                ):
                    created_count += 1
                elif result.get("skipped") or result.get("disabled"):
                    skipped_count += 1

            return {
                "success": True,
                "created_count": created_count,
                "skipped_count": skipped_count,
                "message": f"Created {created_count} notifications, skipped {skipped_count}",
            }

        except Exception as e:
            current_app.logger.error(f"Error bulk creating notifications: {e}")
            return {"success": False, "error": "Failed to create bulk notifications"}
