from fastapi import FastAPI, HTTPException, Depends, Request, Form
# jinja 형식으로 작성된 html 파일을 렌더링해주기 위한 모듈
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import joblib
import numpy as np
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import logging
from models import Base, IrisPrediction  # ORM 모델 가져오기
########################
from fastapi.staticfiles import StaticFiles # 정적파일 경로 관리
import mlflow.pyfunc

model_name='iris-classification'
model_version = 3
model_uri = f"models:/{model_name}/{model_version}"


# 로깅 설정
logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

# 환경 변수 로드
load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

# 머신러닝 모델 로드
# # 모델 로드 - mlflow의 uri를 맨 위에 작성
mlflow.set_tracking_uri("http://localhost:5000")

prod_model_uri = 'models:/iris-classification-prod@champion'
model = mlflow.sklearn.load_model(prod_model_uri)
# model = mlflow.pyfunc.load_model(model_uri)
# model = joblib.load("iris_model.joblib")

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI()

##################  정적인 파일들을 관리하는 별도의 폴더에 대한 정보 작성
app.mount('/static', StaticFiles(directory='static'), name='static')

# 데이터베이스 연결 설정
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine

# 템플릿 경로 선언
templates = Jinja2Templates(directory="templates", auto_reload=True)

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

# 사용자가 값을 입력하는 화면에 대한 엔드포인트
@app.get("/")
def read_form(request:Request):
    return templates.TemplateResponse("input_form.html", {"request":request})

# 예측 및 데이터베이스 저장 엔드포인트 정의
@app.post("/predict")
def predict(request: Request,     
            sepal_length: float = Form(...), # elipsis : Form() , Query(), Path()처럼 입력값에 ...을 작성해 두면 필수요소로 여김 - ...으로 required를 약속처럼 채워넣습니다.
            sepal_width: float = Form(...),
            petal_length: float = Form(...),
            petal_width: float = Form(...),
            db: Session = Depends(get_db)):
    try:
        features = np.array([[sepal_length, sepal_width,
                petal_length, petal_width]])
        prediction = model.predict(features)
        prediction = int(prediction[0]) 
        new_pred = IrisPrediction(
            sepal_length=sepal_length, 
            sepal_width=sepal_width,
            petal_length=petal_length, 
            petal_width=petal_width,
            prediction=prediction
        )

        db.add(new_pred)
        db.commit()
        db.refresh(new_pred)
        return templates.TemplateResponse("result.html", {"request": request, 'sepal_length': sepal_length,
                                                           "sepal_width": sepal_width,
                                                           "petal_length": petal_length, 
                                                           "petal_width": petal_width, 
                                                           "prediction": prediction }) # json 객체로 전달할 수 있게 기본 자료형으로 변환 
    except:
        raise HTTPException(500, "server error")
