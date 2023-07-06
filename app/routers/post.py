from fastapi import FastAPI, Response, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.get('/posts', response_model=List[schemas.PostResponse])
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute("""
    #    SELECT *
    #    FROM posts
    # """)
    # posts = cursor.fetchall()
    
    posts = db.query(models.Post).all()
    return posts

@router.post('/posts', status_code=201, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)): # Store all data in body as python dictionary named payLoad
    # cursor.execute("""
    #    INSERT INTO posts (title, content, published) VALUES(%s, %s, %s) 
    #    RETURNING * 
    # """, (post.title, post.content, post.published)) # %s Represents variable
    
    # new_post = cursor.fetchone()
    # conn.commit()'

    new_post = models.Post(
        **post.dict()
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.get('/posts/{id}', response_model=schemas.PostResponse) 
def  get_post(id: int, db: Session = Depends(get_db)): # automatically convert to integer if possible
    # cursor.execute("""
    #    SELECT * 
    #    FROM posts
    #    WHERE posts.id = %s
    # """, (id,))

    # one_post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if post is None:
        raise HTTPException(status_code=404, detail=f'post with id: {id} was not found')
    return post

@router.delete('/posts/{id}', status_code=204)
def delete_post(id: int, db: Session = Depends(get_db)):
    # cursor.execute("""
    #    DELETE
    #    FROM posts
    #    WHERE posts.id = %s
    #    RETURNING *
    # """, (id,))

    # deleted_post = cursor.fetchone()
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() is None:
        raise HTTPException(status_code=404, 
                            detail=f"post with id: {id} does not exist")

    post.delete(synchronize_session=False)
    db.commit()
    
    return Response(status_code=204)

@router.put('/posts/{id}', response_model=schemas.PostResponse)
def update_post(id: int, updated_post: schemas.PostUpdate, db: Session = Depends(get_db)):
    # cursor.execute("""
    #    UPDATE posts
    #    SET title = %s, content = %s, published = %s
    #    WHERE id = %s
    #    RETURNING *
    # """, (post.title, post.content, post.published, id))

    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id)

    post = post_query.first()

    if post is None:
        raise HTTPException(status_code=404,
                            detail=f'post with id: {id} does not exist')
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    
    return post_query.first()