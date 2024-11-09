from http.client import HTTPException
from handlers.helpers import extract_authorization_token_from_headers
from src.handlers.database_connection import get_db_connection
from src.handlers.request_models import TopicRequest


TOPIC_MIN_LEN_NAME = 7

def create_topic_handler(request: TopicRequest):
    topic_name, topic_description = request.name, request.description

    payload = extract_authorization_token_from_headers(request)
    moderator_email = payload['email']

    if not topic_name or (len(topic_name) < TOPIC_MIN_LEN_NAME):
        raise HTTPException(status_code=400, detail= f"Topic name should have minimum {TOPIC_MIN_LEN_NAME} characters.")

    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE name = %s", (topic_name,))
            existing_topic = cursor.fetchone()

            if existing_topic:
                raise HTTPException(status_code=400, detail="Topic already exists.")
            
            cursor.execute(
                "INSERT INTO topic (name, description) VALUES (%s, %s) RETURNING comment_id",
                (topic_name, topic_description, ))
            topic_id = cursor.fetchone()[0]
            
            connection.commit()

    return {"topic_id": topic_id}


def get_topic_handler(topic_id: str):
    if not topic_id:
        raise HTTPException(status_code=400, detail="Topic_id should not be empty.")
    
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
            return cursor.fetchone()

def get_topic_comments_handler(topic_id: str):
    if not topic_id:
        raise HTTPException(status_code=400, detail="Topic_id should not be empty.")
    
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM topic WHERE id = %s", (topic_id,))
            existing_topic = cursor.fetchone()

            if not existing_topic:
                raise HTTPException(status_code=400, detail="Topic does not exist.")
            
            cursor.execute("SELECT * FROM comment WHERE topic_id = %s", (topic_id,))
            return cursor.fetchall()