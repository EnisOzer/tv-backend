import datetime
from enum import Enum
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

class SessionIdsActivityRequest(BaseModel):
    session_id: str
    topic_id: str
@dataclass
class VoteType(str, Enum):
    VOTE_UP = "VOTE_UP"
    VOTE_DOWN = "VOTE_DOWN"
    SKIPPED = "SKIPPED"
@dataclass   
class VoteRequest(BaseModel):
    comment_id: str
    session_id: str
    vote_type: VoteType