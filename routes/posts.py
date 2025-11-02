from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
from database import get_db
from websocket_manager import manager
from models import Post, PostImage, Reply, PostReaction

router = APIRouter()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/posts/")
async def create_post(
    user_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    images: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    post = Post(user_id=user_id, title=title, description=description)
    db.add(post)
    db.commit()
    db.refresh(post)

    # Save images
    image_paths = []
    for img in images:
        file_path = os.path.join(UPLOAD_DIR, img.filename)
        with open(file_path, "wb") as f:
            f.write(await img.read())
        db_img = PostImage(post_id=post.id, image_path=file_path)
        db.add(db_img)
        image_paths.append(file_path)
    db.commit()
    db.refresh(post)

    # Broadcast new post to all connected WebSocket clients
    await manager.broadcast({
        "event": "new_post",
        "post": {
            "id": post.id,
            "user_id": post.user_id,
            "title": post.title,
            "description": post.description,
            "images": image_paths
        }
    })

    return {"message": "Post created", "post_id": post.id}


@router.get("/posts/")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(Post).all()
    result = []
    for post in posts:
        result.append({
            "id": post.id,
            "user_id": post.user_id,
            "title": post.title,
            "description": post.description,
            "images": [img.image_path for img in post.images],
            "replies": [{"user_id": r.user_id, "content": r.content} for r in post.replies]
        })
    return result


@router.post("/posts/{post_id}/reply")
async def reply_post(post_id: int, user_id: int = Form(...), content: str = Form(...), db: Session = Depends(get_db)):
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    reply = Reply(post_id=post_id, user_id=user_id, content=content)
    db.add(reply)
    db.commit()
    db.refresh(reply)

    # Broadcast new reply
    await manager.broadcast({
        "event": "new_reply",
        "reply": {
            "post_id": post_id,
            "user_id": user_id,
            "content": content
        }
    })

    return {"message": "Reply added"}


@router.post("/posts/{post_id}/react")
async def react_post(post_id: int, user_id: int = Form(...), is_like: bool = Form(...), db: Session = Depends(get_db)):
    reaction = db.query(PostReaction).filter(PostReaction.post_id == post_id, PostReaction.user_id == user_id).first()
    if reaction:
        reaction.is_like = is_like
    else:
        reaction = PostReaction(post_id=post_id, user_id=user_id, is_like=is_like)
        db.add(reaction)
    db.commit()
    db.refresh(reaction)

    # Broadcast reaction update
    await manager.broadcast({
        "event": "new_reaction",
        "reaction": {
            "post_id": post_id,
            "user_id": user_id,
            "is_like": is_like
        }
    })

    return {"message": "Reaction recorded"}
