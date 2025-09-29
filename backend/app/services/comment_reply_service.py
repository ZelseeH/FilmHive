from app.repositories.comment_reply_repository import CommentReplyRepository
from app.repositories.notification_repository import NotificationRepository
from app.services.notification_service import NotificationService
from app.models.comment import Comment
from app.models.user import User
from typing import Dict, List
from flask import current_app
import app.services.user_service as user_service_module


class CommentReplyService:

    @staticmethod
    def create_reply(comment_id: int, reply_user_id: int, text: str) -> Dict:
        try:
            main_comment = Comment.query.get(comment_id)
            if not main_comment:
                raise ValueError("Komentarz nie istnieje")

            main_user_id = main_comment.user_id

            if not text or text.strip() == "":
                raise ValueError("Treść odpowiedzi nie może być pusta")

            reply = CommentReplyRepository.create(
                id_main=main_user_id,
                comment_main_id=comment_id,
                id_reply=reply_user_id,
                text=text.strip(),
            )

            # NAJPIERW COMMIT ODPOWIEDZI
            CommentReplyRepository.commit()

            # POTEM PRÓBUJ WYSŁAĆ POWIADOMIENIA (nie blokuj jeśli się nie uda)
            try:
                CommentReplyService._send_notifications(reply)
            except Exception as notification_error:
                current_app.logger.warning(
                    f"Failed to send notifications: {notification_error}"
                )
                # Kontynuuj - odpowiedź została już zapisana

            return {
                "success": True,
                "reply": reply.serialize(include_users=True),
                "message": "Odpowiedź została dodana",
            }

        except ValueError as e:
            CommentReplyRepository.rollback()
            return {"success": False, "error": str(e)}
        except Exception as e:
            current_app.logger.error(f"Error creating reply: {e}")
            CommentReplyRepository.rollback()
            return {
                "success": False,
                "error": "Wystąpił błąd podczas dodawania odpowiedzi",
            }

    @staticmethod
    def get_thread(comment_id: int) -> Dict:
        try:
            main_comment = Comment.query.get(comment_id)
            if not main_comment:
                return {"success": False, "error": "Komentarz nie istnieje"}

            replies = CommentReplyRepository.get_with_ratings(comment_id)

            return {
                "success": True,
                "data": {
                    "main_comment": main_comment.serialize(
                        include_user=True, include_rating=True
                    ),
                    "replies": replies,
                    "replies_count": len(replies),
                },
            }

        except Exception as e:
            current_app.logger.error(f"Error getting thread: {e}")
            return {"success": False, "error": "Wystąpił błąd podczas pobierania wątku"}

    @staticmethod
    def delete_reply(reply_id: int, user_id: int) -> Dict:
        try:
            current_app.logger.info(
                f"🔍 SERVICE: delete_reply called with reply_id={reply_id}, user_id={user_id}"
            )

            reply = CommentReplyRepository.get_by_id(reply_id)
            current_app.logger.info(f"🔍 SERVICE: Found reply={reply}")

            if not reply:
                current_app.logger.warning(f"🔍 SERVICE: Reply {reply_id} not found")
                return {"success": False, "error": "Odpowiedź nie istnieje"}

            current_app.logger.info(
                f"🔍 SERVICE: Reply owner ID (id_reply)={reply.id_reply}, requesting user ID={user_id}"
            )

            if reply.id_reply != user_id:
                current_app.logger.warning(
                    f"🔍 SERVICE: Permission denied - reply_owner={reply.id_reply}, user={user_id}"
                )
                return {
                    "success": False,
                    "error": "Nie masz uprawnień do usunięcia tej odpowiedzi",
                }

            current_app.logger.info(f"🔍 SERVICE: Calling repository delete")
            success = CommentReplyRepository.delete(reply_id)

            if not success:
                current_app.logger.error("🔍 SERVICE: Repository delete failed")
                return {"success": False, "error": "Nie udało się usunąć odpowiedzi"}

            current_app.logger.info("🔍 SERVICE: Committing changes")
            CommentReplyRepository.commit()
            current_app.logger.info("🔍 SERVICE: Delete successful")

            return {"success": True, "message": "Odpowiedź została usunięta"}

        except Exception as e:
            current_app.logger.error(f"🔍 SERVICE: Exception in delete_reply: {e}")
            import traceback

            current_app.logger.error(f"🔍 SERVICE: Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": "Wystąpił błąd podczas usuwania odpowiedzi",
            }

    @staticmethod
    def delete_reply_by_staff(reply_id: int, staff_user_id: int) -> Dict:
        """Staff może usuwać wszystkie odpowiedzi bez sprawdzania uprawnień"""
        try:
            current_app.logger.info(
                f"🔍 SERVICE: delete_reply_by_staff called with reply_id={reply_id}, staff_id={staff_user_id}"
            )

            reply = CommentReplyRepository.get_by_id(reply_id)
            if not reply:
                return {"success": False, "error": "Odpowiedź nie istnieje"}

            success = CommentReplyRepository.delete_by_staff(reply_id)
            if not success:
                return {"success": False, "error": "Nie udało się usunąć odpowiedzi"}

            CommentReplyRepository.commit()
            return {
                "success": True,
                "message": "Odpowiedź została usunięta przez staff",
            }

        except Exception as e:
            current_app.logger.error(
                f"🔍 SERVICE: Exception in delete_reply_by_staff: {e}"
            )
            return {
                "success": False,
                "error": "Wystąpił błąd podczas usuwania odpowiedzi",
            }

    @staticmethod
    def update_reply(reply_id: int, user_id: int, new_text: str) -> Dict:
        try:
            current_app.logger.info(
                f"🔍 SERVICE: update_reply called with reply_id={reply_id}, user_id={user_id}, new_text='{new_text}'"
            )

            reply = CommentReplyRepository.get_by_id(reply_id)
            current_app.logger.info(f"🔍 SERVICE: Found reply={reply}")

            if not reply:
                current_app.logger.warning(f"🔍 SERVICE: Reply {reply_id} not found")
                return {"success": False, "error": "Odpowiedź nie istnieje"}

            current_app.logger.info(
                f"🔍 SERVICE: Reply owner ID (id_reply)={reply.id_reply}, requesting user ID={user_id}"
            )

            if reply.id_reply != user_id:
                current_app.logger.warning(
                    f"🔍 SERVICE: Permission denied - reply_owner={reply.id_reply}, user={user_id}"
                )
                return {
                    "success": False,
                    "error": "Nie masz uprawnień do edycji tej odpowiedzi",
                }

            if not new_text or new_text.strip() == "":
                current_app.logger.warning("🔍 SERVICE: Empty text")
                return {
                    "success": False,
                    "error": "Treść odpowiedzi nie może być pusta",
                }

            current_app.logger.info(f"🔍 SERVICE: Calling repository update")
            updated_reply = CommentReplyRepository.update(reply_id, new_text.strip())

            if not updated_reply:
                current_app.logger.error("🔍 SERVICE: Repository update failed")
                return {
                    "success": False,
                    "error": "Nie udało się zaktualizować odpowiedzi",
                }

            current_app.logger.info("🔍 SERVICE: Committing changes")
            CommentReplyRepository.commit()
            current_app.logger.info("🔍 SERVICE: Update successful")

            return {
                "success": True,
                "reply": updated_reply.serialize(include_users=True),
                "message": "Odpowiedź została zaktualizowana",
            }

        except Exception as e:
            current_app.logger.error(f"🔍 SERVICE: Exception in update_reply: {e}")
            import traceback

            current_app.logger.error(f"🔍 SERVICE: Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "error": "Wystąpił błąd podczas aktualizacji odpowiedzi",
            }

    @staticmethod
    def update_reply_by_staff(reply_id: int, staff_user_id: int, new_text: str) -> Dict:
        """Staff może edytować wszystkie odpowiedzi bez sprawdzania uprawnień"""
        try:
            current_app.logger.info(
                f"🔍 SERVICE: update_reply_by_staff called with reply_id={reply_id}, staff_id={staff_user_id}"
            )

            reply = CommentReplyRepository.get_by_id(reply_id)
            if not reply:
                return {"success": False, "error": "Odpowiedź nie istnieje"}

            if not new_text or new_text.strip() == "":
                return {
                    "success": False,
                    "error": "Treść odpowiedzi nie może być pusta",
                }

            updated_reply = CommentReplyRepository.update(reply_id, new_text.strip())
            if not updated_reply:
                return {
                    "success": False,
                    "error": "Nie udało się zaktualizować odpowiedzi",
                }

            CommentReplyRepository.commit()
            return {
                "success": True,
                "reply": updated_reply.serialize(include_users=True),
                "message": "Odpowiedź została zaktualizowana przez staff",
            }

        except Exception as e:
            current_app.logger.error(
                f"🔍 SERVICE: Exception in update_reply_by_staff: {e}"
            )
            return {
                "success": False,
                "error": "Wystąpił błąd podczas aktualizacji odpowiedzi",
            }

    @staticmethod
    def _send_notifications(reply):
        """Wysyła powiadomienia - NIE BLOKUJE tworzenia odpowiedzi w przypadku błędów"""
        try:
            comment_id = reply.comment_main_id
            reply_user_id = reply.id_reply
            main_user_id = reply.id_main

            current_app.logger.info(
                f"🔍 SENDING NOTIFICATIONS: reply_user={reply_user_id}, main_user={main_user_id}"
            )

            reply_user = User.query.get(reply_user_id)
            if not reply_user:
                current_app.logger.warning(
                    f"🔍 NOTIFICATION: Reply user {reply_user_id} not found"
                )
                return

            # Powiadomienie dla autora głównego komentarza
            # NotificationService sam zdecyduje czy wysłać (pominie jeśli user_id == from_user_id)
            try:
                result = NotificationService.create_notification(
                    user_id=main_user_id,
                    from_user_id=reply_user_id,
                    comment_id=comment_id,
                    reply_id=reply.reply_id,
                    message=f"{reply_user.username} odpowiedział na Twój komentarz",
                    # USUŃ: type="reply"
                )

                if result.get("skipped"):
                    current_app.logger.info(
                        f"🔍 NOTIFICATION: Self-reply notification skipped for user {main_user_id}"
                    )
            except Exception as e:
                current_app.logger.warning(
                    f"🔍 NOTIFICATION: Failed to notify main user: {e}"
                )

            # Powiadomienia dla innych uczestników wątku
            try:
                participants = CommentReplyRepository.get_participants(comment_id)

                for participant_id in participants:
                    if (
                        participant_id != reply_user_id
                        and participant_id != main_user_id
                    ):
                        try:
                            participant = User.query.get(participant_id)
                            if participant:
                                result = NotificationService.create_notification(
                                    user_id=participant_id,
                                    from_user_id=reply_user_id,
                                    comment_id=comment_id,
                                    reply_id=reply.reply_id,
                                    message=f"{reply_user.username} dodał nową odpowiedź w wątku",
                                    # USUŃ: type="thread_reply"
                                )

                                if result.get("skipped"):
                                    current_app.logger.info(
                                        f"🔍 NOTIFICATION: Notification skipped for participant {participant_id}"
                                    )
                        except Exception as e:
                            current_app.logger.warning(
                                f"🔍 NOTIFICATION: Failed to notify participant {participant_id}: {e}"
                            )

            except Exception as e:
                current_app.logger.warning(
                    f"🔍 NOTIFICATION: Failed to get participants: {e}"
                )

        except Exception as e:
            current_app.logger.error(
                f"🔍 NOTIFICATION: Critical error in _send_notifications: {e}"
            )
            # NIE RZUCAJ BŁĘDU - pozwól odpowiedzi zostać zapisanej
