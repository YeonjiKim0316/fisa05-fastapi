from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np
import mlflow.pyfunc

model_name='iris-classification'
model_version = 1
model_uri = f"models:/{model_name}/{model_version}"

# 모델 로드
model = mlflow.pyfunc.load_model(model_uri)



# {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}