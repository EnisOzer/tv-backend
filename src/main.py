from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.handlers.comment_handler import create_comment_handler
from src.handlers.request_models import CommentRequest, TopicRequest
from src.handlers.topic_handler import create_topic_handler, get_topic_handler, get_topic_comments_handler

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
def create_topic_handler():
    return {"Hello": "World"}

@app.post("/comment")
def read_root():
    return {"Hello": "World"}

@app.put("/vote")
def read_root():
    return {"Hello": "World"}
