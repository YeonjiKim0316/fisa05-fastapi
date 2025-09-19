# endpoint와 관련있는 코드들만 분리
# depends_example.py
from fastapi import FastAPI
from db import engine
from models import Base
from routers import auths, users

# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 생성
app = FastAPI() 

# 라우터 등록  # /auths 를 prefix로 달도록 
app.include_router(auths.auth_router)
app.include_router(users.user_router, prefix="/users", tags=["user info"])