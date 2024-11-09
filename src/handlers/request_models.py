from pydantic import BaseModel
from dataclasses import dataclass

@dataclass
class TopicRequest(BaseModel):
    name: str
    description: str

@dataclass
class CommentRequest(BaseModel):
    topic_id: str
    content: str
    creator_id: str

@dataclass
class TopicResponse(BaseModel):
    id: str
    name: str
    creator_id: str
