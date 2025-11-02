from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PostImageSchema(BaseModel):
    image_path: str

    class Config:
        orm_mode = True

class ReplySchema(BaseModel):
    user_id: int
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class PostSchema(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    created_at: datetime
    images: List[PostImageSchema] = []
    replies: List[ReplySchema] = []

    class Config:
        orm_mode = True
