from fastapi import FastAPI
from src.handlers.comment_handler import create_comment_handler
from src.handlers.request_models import CommentRequest, TopicRequest
from src.handlers.topic_handler import create_topic_handler, get_topic_handler, get_topic_comments_handler

app = FastAPI()

@app.post("/topic")
def create_topic(request: TopicRequest):
    return create_topic_handler(request)

@app.post("/comment")
def read_root(request: CommentRequest):
    return create_comment_handler(request)

@app.get("/topic/{topic_id}")
def read_root(topic_id: str):
    return get_topic_handler(topic_id)

@app.get("/topic/{topic_id}/comments")
def read_root(topic_id: str):
    return get_topic_comments_handler(topic_id)
