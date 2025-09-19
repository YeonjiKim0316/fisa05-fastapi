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
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# 머신러닝 모델 로드
model = joblib.load("iris_model.joblib")

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

# 데이터베이스 연결 설정
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 테이블 생성
Base.metadata.create_all(bind=engine)

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
def predict(data: IrisInput, db: Session = Depends(get_db)):
    try:
        features = np.array([[data.sepal_length, data.sepal_width,
                data.petal_length, data.petal_width]])
        prediction = model.predict(features)

        new_pred = IrisPrediction(
            sepal_length=data.sepal_length, 
            sepal_width=data.sepal_width,
            petal_length=data.petal_length, 
            petal_width=data.petal_width,
            prediction=prediction
        )

        db.add(new_pred)
        db.commit()
        db.refresh(new_pred)
        return new_pred # json 객체로 전달할 수 있게 기본 자료형으로 변환 
    except:
        raise HTTPException(500, "server error")
