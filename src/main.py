from fastapi.middleware.cors import CORSMiddleware
from typing import Union
from fastapi import FastAPI, Header, Request
from src.handlers.comment_handler import create_comment_handler, get_pending_comments_handler
from src.handlers.request_models import CommentRequest, SessionIdsActivityRequest, SessionIdsTopicsRequest, TopicRequest, VoteRequest
from src.handlers.session_activity_handler import get_session_ids_activity_handler, get_session_ids_topics_handler, vote_handler
from src.handlers.topic_handler import create_topic_handler, get_all_topic_handler, get_topic_comments_summary_handler, get_topic_handler, get_topic_comments_handler

app = FastAPI()


# Specify allowed origins
origins = [
    "http://localhost",  # Allow requests from localhost
    "http://localhost:8000",
    "https://example.com",  # Add your specific domains
    "*",  # WARNING: Allowing all origins - use carefully
]

# Apply the CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies or other credentials to be sent
    allow_methods=["*"],     # Allow all HTTP methods (e.g., GET, POST)
    allow_headers=["*"],     # Allow all headers
)

@app.post("/topic")
def create_topic(request: TopicRequest, authorization: Union[str, None] = Header(default=None)):
    return create_topic_handler(request, authorization)

@app.get("/topic")
def get_all_topics():
    return get_all_topic_handler()

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

@app.get("/topic/{topic_id}/comments_summary")
def get_topic_comments_summary(topic_id: str):
    summary: str = get_topic_comments_summary_handler(topic_id)
    return {"summary": summary}

# Moderator endpoint to get unapproved comments
@app.get("/topic/{topic_id}/pending_comments")
def get_pending_comments(topic_id: str, request: Request):
    return get_pending_comments_handler(topic_id, request)

@app.get("/get_session_ids_topics")
def get_session_ids_topics(request: SessionIdsTopicsRequest):
    return get_session_ids_topics_handler(request)

@app.get("/get_session_ids_activity")
def get_session_ids_activity(request: SessionIdsActivityRequest):
    return get_session_ids_activity_handler(request)

@app.put("/vote")
def vote(request: VoteRequest):
    return vote_handler(request)
