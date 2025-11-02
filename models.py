from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    images = relationship("PostImage", back_populates="post")
    replies = relationship("Reply", back_populates="post")
    reactions = relationship("PostReaction", back_populates="post")

class PostImage(Base):
    __tablename__ = "post_images"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    image_path = Column(String)

    post = relationship("Post", back_populates="images")

class Reply(Base):
    __tablename__ = "replies"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="replies")
    user = relationship("User")

class PostReaction(Base):
    __tablename__ = "post_reactions"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    is_like = Column(Boolean)

    post = relationship("Post", back_populates="reactions")
