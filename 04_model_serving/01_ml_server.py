from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
# import mlflow.pyfunc

# model_name='iris-classification'
# model_version = 1
# model_uri = f"models:/{model_name}/{model_version}"

# # 모델 로드
# model = mlflow.pyfunc.load_model(model_uri)
model = joblib.load("iris_model.joblib")

app = FastAPI()

# 입력데이터 구조를 정의하는 데이터모델
class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

# 실제 추론 함수 
@app.post("/predict")
def predict(data: IrisInput):
    features = np.array([[data.sepal_length, data.sepal_width,
            data.petal_length, data.petal_width]])
    prediction = model.predict(features)
    return int(prediction[0]) # json 객체로 전달할 수 있게 기본 자료형으로 변환 

# {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}