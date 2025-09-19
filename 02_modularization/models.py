# 데이터 모델을 정의하는 코드들을 분리 (sqlalchemy를 통한) 
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# SQLAlchemy ORM을 사용하여 데이터베이스 모델을 정의하기 위한 기본 클래스
# declarative_base()를 사용하여 ORM 모델을 정의할 수 있는 기본 클래스 생성
Base = declarative_base()

# SQLAlchemy 모델 정의
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")  # 사용자 역할 (기본값: user)
