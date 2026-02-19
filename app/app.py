from fastapi import FastAPI , HTTPException
from app.schemas import PostCreate, PostResponse
from app.db import Post , get_async_session , create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
 
@asynccontextmanager
async def lifespan (app: FastAPI):
     await create_db_and_tables()
     yield
 
app = FastAPI(lifespan=lifespan)


text_posts = {1:{'title': 'New Post','content': 'cool test post'},
              2:{"title": "New Post", "content": "cool test post"},
              3:{"title": "Evening Update", "content": "just finished coding"},
              4:{"title": "Morning Thoughts", "content": "coffee is brewing"},
              5:{"title": "Tech News", "content": "new AI model released today"},
              6:{"title": "Personal Note", "content": "went for a long walk"},
              7:{"title": "Recipe", "content": "tried making pasta from scratch"},
              8:{"title": "Book Review", "content": "just finished reading Dune"},
              9:{"title": "Work Log", "content": "fixed the login bug finally"},
              10:{"title": "Random Thought", "content": "why is the sky blue though"},
              11:{"title": "Weekend Plan", "content": "going to the beach tomorrow"}
              }


@app.get("/posts")
def get_all_posts(limit: int):
    if limit :
        return list(text_posts.values())[:limit]
    return text_posts  

@app.get("/posts/{id}")
def get_posts(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    return text_posts[id] 

@app.post('/posts')
def create_post(post: PostCreate) -> PostResponse:
    new_post = {"title": post.title, "content": post.content}
    text_posts[max(text_posts.keys())+1]= new_post
    return PostResponse(**new_post)

@app.delete("/posts/{id}")
def delete_post(id:int):
    if id not in text_posts:
        raise HTTPException(status_code=404, detail="Post not found")
    del text_posts[id]
