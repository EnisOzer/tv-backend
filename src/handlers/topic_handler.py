from http.client import HTTPException
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import TopicRequest
import datetime

TOPIC_MIN_LEN_TITLE = 3

def create_topic_handler(request: TopicRequest):
    topic_title, topic_description = request.title, request.description
    
    if not topic_title or (len(topic_title) < TOPIC_MIN_LEN_TITLE):
        raise HTTPException(status_code=400, detail= f"Topic title should have minimum {TOPIC_MIN_LEN_TITLE} characters.")

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE title = %s", (topic_title,))
            existing_topic = cursor.fetchone()

            if existing_topic:
                raise HTTPException(status_code=400, detail="Topic already exists.")
            
            time_created = datetime.datetime.now()
            cursor.execute(
                "INSERT INTO topic (title, description, created_at) VALUES (%s, %s, %s) RETURNING id",
                (topic_title, topic_description, time_created))
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
            topic_id, topic_title, topic_description, comment_count, created_at, completed = topic
            return {
                "topic_id": topic_id,
                "title": topic_title,
                "description": topic_description,
                "comment_count": comment_count,
                "created_at" : created_at,
                "completed": completed,
            }

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
                    c.session_id,
                    c.topic_id,
                    COUNT(CASE WHEN v.voted_up = TRUE THEN 1 END) AS up_votes,
                    COUNT(CASE WHEN v.voted_up = FALSE THEN 1 END) AS down_votes
                FROM comment c
                LEFT JOIN vote v ON c.id = v.comment_id
                WHERE c.topic_id = %s
                GROUP BY c.id, c.session_id, c.topic_id
            """, (topic_id,))
            
            # Format the response as a list of dictionaries
            comments = cursor.fetchall()
            formatted_comments = [
                {
                    "session_id": comment[0],
                    "down_votes": comment[3],
                    "up_votes": comment[2],
                    "topic_id": comment[1]
                }
                for comment in comments
            ]
            
            return formatted_comments