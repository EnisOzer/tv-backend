from typing import Any, List

from fastapi import HTTPException, Request
from src.ai.tv_ai_api import Comment, checkHatefulComment, clusterComments
from src.handlers.helpers import extract_authorization_token_from_headers
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import CommentRequest
import datetime

def create_comment_handler(request: CommentRequest):
    topic_id = request.topic_id
    session_id  = request.session_id 
    content = request.content

    if not topic_id or not session_id  or not content:
        raise HTTPException(status_code=400, detail=f"All fields must be provided.")
    
    if checkHatefulComment(content):
        raise HTTPException(status_code=400, detail=f"Comment can't be posted because it expresses hateful speach")

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
            existing_topic = cursor.fetchone()

            if not existing_topic:
                raise HTTPException(status_code=400, detail="Topic does not exist.")
            
            time_created = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO comment (topic_id, session_id, content, created_at) VALUES (%s, %s, %s, %s) RETURNING id",
                (topic_id, session_id , content, time_created))
            comment_id = cursor.fetchone()[0]
            
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
    payload = extract_authorization_token_from_headers(request.headers.get('authorization'))
    email = payload['email']

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT c.id AS comment_id, 0 as up_votes, 0 as down_votes, \
                    0 as skipped_times, c.content, c.approved, \
                    c.topic_id, c.created_at, c.session_id \
                FROM comment c JOIN topic t ON c.topic_id = t.id \
                WHERE t.moderator_email = %s AND t.id = %s AND c.approved = false",
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
            
    return clusterComments([c.comment for c in comments])
