from http.client import HTTPException

from fastapi import Request
from handlers.helpers import extract_authorization_token_from_headers
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import CommentRequest


def create_comment_handler(request: CommentRequest):
    topic_id = request.topic_id
    user_session_id  = request.creator_id 
    content = request.content

    if not topic_id or not user_session_id  or not content:
        raise HTTPException(status_code=400, detail=f"All fields must be provided.")

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
            existing_topic = cursor.fetchone()

            if not existing_topic:
                raise HTTPException(status_code=400, detail="Topic already exists.")
            
            cursor.execute(
                "INSERT INTO comment (topic_id, user_session_id, content) VALUES (%s, %s, %s) RETURNING comment_id",
                (topic_id, user_session_id , content))
            comment_id = cursor.fetchone()[0]
            
            connection.commit()

    return {"comment_id": comment_id}

def get_unapproved_comments(request: Request):
    payload = extract_authorization_token_from_headers(request)
    email = payload['email']

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id AS comment_id, 0 as up_votes, 0 as down_votes, \
                    0 as skipped_times, c.content as content, c.approved as approved, \
                    c.topic_id as topic_id, c.created_at \
                FROM comment c JOIN topic t ON c.topic_id = t.id \
                WHERE t.moderator_email = %s AND c.approved = false", (email, ))
            comments = cursor.fetchall()
            
            return comments
