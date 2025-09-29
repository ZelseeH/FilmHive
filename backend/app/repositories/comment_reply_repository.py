from app.extensions import db
from app.models.comment_reply import CommentReply
from app.models.comment import Comment
from app.models.rating import Rating
from sqlalchemy import and_
from sqlalchemy.orm import joinedload
from typing import List, Optional, Dict


class CommentReplyRepository:

    @staticmethod
    def create(
        id_main: int, comment_main_id: int, id_reply: int, text: str
    ) -> CommentReply:
        reply = CommentReply(
            id_main=id_main,
            comment_main_id=comment_main_id,
            id_reply=id_reply,
            text=text,
        )
        db.session.add(reply)
        db.session.flush()
        return reply

    @staticmethod
    def get_by_id(reply_id: int) -> Optional[CommentReply]:
        return CommentReply.query.get(reply_id)

    @staticmethod
    def update(reply_id: int, new_text: str) -> Optional[CommentReply]:
        reply = CommentReply.query.get(reply_id)
        if reply:
            reply.text = new_text.strip()
            return reply
        return None

    @staticmethod
    def get_by_comment(comment_id: int) -> List[CommentReply]:
        return (
            CommentReply.query.filter_by(comment_main_id=comment_id)
            .order_by(CommentReply.created_at.asc())
            .all()
        )

    @staticmethod
    def get_with_ratings(comment_id: int) -> List[Dict]:
        try:
            results = (
                db.session.query(CommentReply, Rating)
                .join(Comment, Comment.comment_id == CommentReply.comment_main_id)
                .outerjoin(
                    Rating,
                    and_(
                        Rating.user_id == CommentReply.id_reply,
                        Rating.movie_id == Comment.movie_id,
                    ),
                )
                .options(
                    joinedload(CommentReply.reply_user),
                    joinedload(CommentReply.main_user),
                )
                .filter(CommentReply.comment_main_id == comment_id)
                .order_by(CommentReply.created_at.asc())
                .all()
            )

            serialized_replies = []
            for reply, rating in results:
                reply_data = reply.serialize(include_users=True)
                reply_data["user_rating"] = rating.rating if rating else None
                serialized_replies.append(reply_data)

            return serialized_replies

        except Exception as e:
            replies = CommentReplyRepository.get_by_comment(comment_id)
            return [reply.serialize(include_users=True) for reply in replies]

    @staticmethod
    def get_participants(comment_id: int) -> List[int]:
        participants = (
            db.session.query(CommentReply.id_reply)
            .filter(CommentReply.comment_main_id == comment_id)
            .distinct()
            .all()
        )
        return [participant[0] for participant in participants]

    @staticmethod
    def get_participants_except(comment_id: int, exclude_user_id: int) -> List[int]:
        participants = (
            db.session.query(CommentReply.id_reply)
            .filter(
                and_(
                    CommentReply.comment_main_id == comment_id,
                    CommentReply.id_reply != exclude_user_id,
                )
            )
            .distinct()
            .all()
        )
        return [participant[0] for participant in participants]

    @staticmethod
    def delete(reply_id: int) -> bool:
        reply = CommentReply.query.get(reply_id)
        if reply:
            db.session.delete(reply)
            return True
        return False

    @staticmethod
    def delete_by_staff(reply_id: int) -> bool:
        """Staff może usuwać odpowiedzi bez sprawdzania uprawnień"""
        reply = CommentReply.query.get(reply_id)
        if reply:
            db.session.delete(reply)
            return True
        return False

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()
