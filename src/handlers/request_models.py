from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class TopicRequest(BaseModel):
    title: str
    description: str

@dataclass
class CommentRequest(BaseModel):
    topic_id: str
    content: str
    session_id: str

@dataclass
class TopicResponse(BaseModel):
    id: str
    name: str
    creator_id: str
