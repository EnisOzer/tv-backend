from enum import Enum
from typing import List
from pydantic import BaseModel
from dataclasses import dataclass
import datetime

class TopicResponse(BaseModel):
    topic_id: str
    title: str
    description: str
    comment_count: int
    created_at: datetime.datetime
    completed: bool

class CommentResponse(BaseModel):
    comment_id: str
    session_id: str
    topic_id: str
    content: str
    created_at: datetime.datetime
    up_votes: int
    down_votes: int
    skipped_times: int

class ActivityTopicResponse(BaseModel):
    session_id: str
    topic_id: str
    commentIDsUpVoted: List[str]
    commentIDsDownVoted: List[str]
    commentIDsSkipped: List[str]
