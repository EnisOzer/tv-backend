import logging
from typing import Any, List

from fastapi import HTTPException, Request
from src.ai.tv_ai_api import Comment, checkHatefulComment, clusterComments
from src.handlers.helpers import extract_authorization_token_from_headers
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import CommentRequest
import datetime

logger = logging.getLogger(__name__)

def create_comment_handler(request: CommentRequest):
    topic_id = request.topic_id
    session_id  = request.session_id 
    content = request.content

    if not topic_id or not session_id  or not content:
        logger.error("All fields must be provided for create comment method.",)
        raise HTTPException(status_code=400, detail=f"All fields must be provided.")
    
    if checkHatefulComment(content):
        raise HTTPException(status_code=400, detail=f"Comment can't be posted because it expresses hateful speach")

    logger.info("Creating comment(topic_id, session_id,content): %s %s %s",
                topic_id, session_id, content)
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
            existing_topic = cursor.fetchone()

            if not existing_topic:
                logger.error("Topic %s does not exist",topic_id)
                raise HTTPException(status_code=400, detail="Topic does not exist.")
            
            time_created = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO comment (topic_id, session_id, content, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (topic_id, session_id , content, time_created))
            comment_id = cursor.fetchone()[0]
            
            cursor.execute(
                "UPDATE topic SET comment_count = comment_count + 1 WHERE id = %s",
                (topic_id,)
            )

            connection.commit()

    return {
            "id": comment_id,
            "topic_id": topic_id,
            "session_id": session_id,
            "content": content,
            "approved": False,
            "rejected": False,
            "created_at": time_created
            }

def get_pending_comments_handler(topic_id: str, request: Request):
    logger.info("Getting pending comments for topic_id: %s", topic_id)
    payload = extract_authorization_token_from_headers(request.headers.get('authorization'))
    email = payload['email']

    if not email:
        raise HTTPException(status_code=401, detail="JWT token is missing moderator's email")

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id AS comment_id, 0 as up_votes, 0 as down_votes, \
                    0 as skipped_times, c.content, c.approved, \
                    c.topic_id, c.created_at, c.session_id \
                FROM comment c JOIN topic t ON c.topic_id = t.id \
                WHERE t.moderator_email = %s \
                    AND t.id = %s \
                    AND c.approved = FALSE \
                    AND c.rejected = FALSE",
                (email, topic_id))
            commentsList: List[List[Any]] = cursor.fetchall()

            comments = [
                Comment(
                    comment_id = row[0],
                    comment=row[4],
                    topic_id = row[6],
                    session_id= row[8],
                    up_votes= row[1],
                    down_votes= row[2],
                    skipped_times = row[3],
                    timestamp = row[7],
                )
                for row in commentsList
            ]
            
            return clusterComments(comments)

def approve_comment_handler(comment_id: str, request: Request):
    return change_approved_status_of_comment(comment_id, approved = True, request = request)

def reject_comment_handler(comment_id: str, request: Request):
    return change_approved_status_of_comment(comment_id, approved = False, request = request)

def change_approved_status_of_comment(comment_id: str, approved: bool, request: Request):
    # Check whether moderator sent bearer token
    payload = extract_authorization_token_from_headers(request.headers.get("Authorization"))
    moderator_email: str = payload['email']

    if not moderator_email:
        raise HTTPException(status_code=401, detail="JWT token is missing moderator's email")
    
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.approved, c.rejected \
                FROM comment c JOIN topic t ON c.topic_id = t.id \
                WHERE t.moderator_email = %s AND c.id = %s",
                (moderator_email, comment_id))
            
            row = cursor.fetchone()

            if not row:
                raise HTTPException(status_code=400, detail="Comment with given id is not found")
            
            c_approved, c_rejected = row

            if c_approved:
                raise HTTPException(status_code=400, detail="Comment is already approved")
            
            if c_rejected:
                raise HTTPException(status_code=400, detail="Comment is already rejected")

            cursor.execute(
                "UPDATE comment SET approved = %s, rejected = %s WHERE id = %s",
                (approved, not approved, comment_id)
            )
            
            connection.commit()
            return {}
