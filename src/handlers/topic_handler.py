from src.handlers.helpers import extract_authorization_token_from_headers
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import TopicRequest
from fastapi import HTTPException
import datetime
from typing import Optional, Union

TOPIC_MIN_LEN_TITLE = 3

def create_topic_handler(request: TopicRequest, authorization: Union[str, None]):
    topic_title, topic_description = request.title, request.description
    
    if not topic_title or (len(topic_title) < TOPIC_MIN_LEN_TITLE):
        raise HTTPException(status_code=400, detail= f"Topic title should have minimum {TOPIC_MIN_LEN_TITLE} characters.")

    payload = extract_authorization_token_from_headers(authorization)
    moderator_email = payload['email']

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE title = %s", (topic_title,))
            existing_topic = cursor.fetchone()

            if existing_topic:
                raise HTTPException(status_code=400, detail="Topic already exists.")
            
            time_created = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO topic (title, description, created_at, moderator_email) VALUES (%s, %s, %s, %s) RETURNING id",
                (topic_title, topic_description, time_created, moderator_email))
            topic_id = cursor.fetchone()[0]
            
            connection.commit()

    return {
            "topic_id": topic_id,
            "title": topic_title,
            "description": topic_description,
            "commentCount": 0,
            "created_at": time_created,
            "completed": False,
            }


def get_topic_handler(topic_id: str):
    if not topic_id:
        raise HTTPException(status_code=400, detail="Topic_id should not be empty.")
    
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
            topic = cursor.fetchone()
            topic_id, topic_title, topic_description, comment_count, created_at, completed, moderator_email = topic
            return {
                "topic_id": topic_id,
                "title": topic_title,
                "description": topic_description,
                "comment_count": comment_count,
                "created_at" : created_at,
                "completed": completed,
                "moderator_email": moderator_email
            }

def get_all_topic_handler():
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic")
            topics = cursor.fetchall()

            if not topics:
                raise HTTPException(status_code=404, detail="No topics found")

            result = []
            for topic in topics:
                topic_id, topic_title, topic_description, comment_count, created_at, completed, moderator_email = topic
                result.append({
                    "topic_id": topic_id,
                    "title": topic_title,
                    "description": topic_description,
                    "comment_count": comment_count,
                    "created_at": created_at,
                    "completed": completed,
                    "moderator_email": moderator_email
                })
                
            return result
        
def get_topic_comments_handler(topic_id: str):
    if not topic_id:
        raise HTTPException(status_code=400, detail="Topic_id should not be empty.")
    
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
            existing_topic = cursor.fetchone()

            if not existing_topic:
                raise HTTPException(status_code=400, detail="Topic does not exist.")
            
            cursor.execute("""
                SELECT 
                    c.id,
                    c.session_id,
                    c.topic_id,
                    c.content,
                    c.created_at,
                    COUNT(CASE WHEN v.vote_type = 'VOTE_UP' THEN 1 END) AS up_votes,
                    COUNT(CASE WHEN v.vote_type = 'VOTE_DOWN' THEN 1 END) AS down_votes,
                    COUNT(CASE WHEN v.vote_type = 'SKIPPED' THEN 1 END) AS skipped_votes
                FROM comment c
                LEFT JOIN vote v ON c.id = v.comment_id
                WHERE c.topic_id = %s AND c.approved = FALSE
                GROUP BY c.id, c.session_id, c.topic_id
            """, (topic_id,))
            
            # Format the response as a list of dictionaries
            comments = cursor.fetchall()
            formatted_comments = [
                {
                    "comment_id": comment[0],
                    "session_id": comment[1],
                    "topic_id": comment[2],
                    "content": comment[3],
                    "created_at": comment[4],
                    "up_votes": comment[5],
                    "down_votes": comment[6],
                    "skipped_times": comment[7]
                }
                for comment in comments
            ]
            
            return formatted_comments