from typing import Union
from fastapi import FastAPI, Header, Request
from src.handlers.comment_handler import create_comment_handler, get_pending_comments_handler
from src.handlers.request_models import CommentRequest, TopicRequest
from src.handlers.topic_handler import create_topic_handler, get_topic_handler, get_topic_comments_handler

app = FastAPI()

@app.post("/topic")
def create_topic(request: TopicRequest, authorization: Union[str, None] = Header(default=None)):
    return create_topic_handler(request, authorization)

@app.post("/comment")
def create_comment(request: CommentRequest):
    return create_comment_handler(request)

@app.get("/topic/{topic_id}")
def get_topic(topic_id: str):
    return get_topic_handler(topic_id)

# Return comments that are approved by moderator
@app.get("/topic/{topic_id}/comment")
def get_topic_comments(topic_id: str):
    return get_topic_comments_handler(topic_id)

# Moderator endpoint to get unapproved comments
@app.get("/topic/{topic_id}/pending_comments")
def get_pending_comments(topic_id: str, request: Request):
    return get_pending_comments_handler(topic_id, request)