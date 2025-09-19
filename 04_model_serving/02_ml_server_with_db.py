from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import joblib
import numpy as np
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import logging
from models import Base, IrisPrediction  # ORM 모델 가져오기

# 로깅 설정
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# 환경 변수 로드

# 머신러닝 모델 로드

# FastAPI 애플리케이션 인스턴스 생성

# 데이터베이스 연결 설정

# 테이블 생성

# 입력 데이터 스키마 정의
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# 데이터베이스 세션 종속성 정의
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 예측 및 데이터베이스 저장 엔드포인트 정의
@app.post("/predict")
