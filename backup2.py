from fastapi import FastAPI , HTTPException, File, UploadFile, Form,  Depends
from app.schemas import PostCreate, PostResponse
from app.db import Post , get_async_session , create_db_and_tables
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os 
import uuid
import tempfile
import asyncio
import base64





@asynccontextmanager
async def lifespan (app: FastAPI):
     await create_db_and_tables()
     yield
 
app = FastAPI(lifespan=lifespan)



@app.post('/upload')
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(''),
    session: AsyncSession = Depends(get_async_session)
):
    
    
    try:
        contents = await file.read()
        encoded = base64.b64encode(contents).decode('utf-8')
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename or '')[1]) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(contents)   
    
        upload_result = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: imagekit.upload_file(
                file = encoded,
                file_name = file.filename,
                options = UploadFileRequestOptions(
                    use_unique_file_name= True,
                    tags=['backend-upload']
                
                )
            )
        )
        
        
        
        if upload_result.response_metadata.http_status_code == 200:
            
            file_type = "unknown"
            if file.content_type and file.content_type.startswith('video/'):
                file_type = "video"
            elif file.content_type and file.content_type.startswith('image/'):
                file_type = "image"
            
            post = Post(
                caption = caption,
                url = upload_result.url,
                file_type = file_type,
                file_name = upload_result.name
            )
           
            session.add(post)
            await session.commit()
            await session.refresh(post)
            return post
    
    except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
            file.file.close()



@app.get('/feed')
async def get_feed(
    session: AsyncSession = Depends(get_async_session)
):
     
     result = await session.execute (select(Post).order_by(Post.created_at.desc()))
     posts = [row[0] for row in result.all()]
     
     
     post_data = []
     for post in posts:
         post_data.append(
             {
                 
                 'id': str(post.id),
                 'caption': post.caption,
                 'url': post.url,
                 'file_type': post.file_type,
                 'file_name': post.file_name,
                 'created_at':post.created_at.isoformat()
             }
         )
         return {'posts': post_data}
