# 여러군데에서 사용되는, utilization을 위한 함수들을 분리
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
# SQLAlchemy 기본 설정
DATABASE_URL = "sqlite:///./test.db"  # SQLite 데이터베이스 URL

# SQLAlchemy 엔진 생성
# SQLite 데이터베이스를 사용하며, check_same_thread=False로 설정하여 멀티스레드에서 사용할 수 있도록 함
# SQLite는 기본적으로 멀티스레드에서 사용할 수 없으므로, FastAPI에서 사용하기 위해 이 설정으로 해결
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 세션은 데이터베이스의 작업(쿼리 실행, 트랜잭션 등)을 수행하는 단위
# 세션을 사용하여 데이터베이스와 상호작용
# sessionmaker: SQLAlchemy의 세션을 생성하는 팩토리 함수
# autoflush=False: 세션이 자동으로 플러시(변경 내용을 db 반영)를 사용하지 않음
                # 임서 저장. 변경 사항이 데이터베이스에 기록은 되나 롤백이 가능한 상태 유지   
# autocommit=False: 최종 저장. 자동 커밋을 사용하지 않음
# bind=engine: SQLAlchemy 엔진과 연결
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 데이터베이스 세션 종속성 정의
def get_db():
    """
    데이터베이스 세션을 생성하고 반환하는 종속성 함수.
    요청이 끝나면 세션을 닫습니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
