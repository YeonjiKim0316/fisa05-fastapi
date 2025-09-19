# endpoint와 관련있는 코드들만 분리
# depends_example.py
from fastapi import FastAPI, Depends, HTTPException, status
from db import get_db, engine
from models import User, Base
from schema import UserCreate
from sqlalchemy.orm import Session

## 두명의 user를 만드는데 
# 1명은 alice, role: admin,
# 1명은 jjangu, role: user 가 되도록 작성

# jjangu의 이름을 bob으로 바꿔주세요. -> put 
# jjangu의 email을 abc@abc.com으로 바꿔주세요. -> patch 
# admin 이라는 메서드를 alice / jjangu 둘로 호출해보세요.


# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 생성
app = FastAPI() 

# 인증 토큰 검증 함수
@app.get('/validate/')
def get_current_user(token: str, db: Session = Depends(get_db)):
    """
    인증 토큰을 검증하고 사용자 정보를 반환하는 함수.
    - 실제로는 토큰을 디코딩하거나 데이터베이스에서 사용자 정보를 조회해야 함.
    """
    user = db.query(User).filter(User.name == token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# 권한 확인 함수
def get_admin_user(current_user: User = Depends(get_current_user)):
    """
    현재 사용자가 관리자 권한을 가지고 있는지 확인하는 함수.
    - 관리자 권한이 없으면 HTTP 403 에러를 반환.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user

# 사용자 생성 엔드포인트
@app.post("/users/")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    새로운 사용자를 생성하는 엔드포인트.
    - `Depends(get_db)`를 사용하여 데이터베이스 세션을 주입받습니다.
    """
    # 이메일 중복 확인
    existing_user = db.query(User).filter(User.email == user.email).first()
    print(existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 새로운 사용자 생성
    new_user = User(name=user.name, email=user.email, role=user.role)
    print('new_user', new_user)
    db.add(new_user) # "insert into users values "
    db.commit()
    db.refresh(new_user)  # 새로 추가된 사용자 정보 갱신
    return {"id": new_user.id, "name": new_user.name, "email": new_user.email, "role": new_user.role}

# 사용자 목록 조회 엔드포인트
@app.get("/users/")
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    사용자 목록을 조회하는 엔드포인트.
    - `Depends(get_db)`를 사용하여 데이터베이스 세션을 주입받습니다.
    - `skip`과 `limit`을 사용하여 페이징 처리.
    """
    users = db.query(User).offset(skip).limit(limit).all() # [] 
    return users

# 사용자를 db에서 삭제하는 메서드
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    # db에서 사용자 id와 일치하는 id가 있는지 조회한다
    existing_user = db.query(User).filter(User.id == user_id).first() # user 리스트 안에 값이 들어있지 않고 객체 자체로 값을 가져옵니다.   
    if existing_user:
        # 있으면 해당 user의 정보를 삭제한다
        db.delete(existing_user)
        db.commit()
        # 정보가 잘 삭제되었습니다.
        return {"message": "정보가 잘 삭제되었습니다."}
 
    # 없으면 400번대 에러를 반환하고 
    raise HTTPException(status_code=400, detail="찾는 사용자가 없습니다")

# 사용자의 모든 정보를 수정하는 엔드포인트 
@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    # 사용자id로 db에 사용자정보가 존재하는지 확인 
    existing_user = db.query(User).filter(User.id == user_id).first() # 리스트 안에 값이 들어있지 않고 객체 자체로 값을 가져옵니다.   
    if existing_user:
        # 입력받은 전체 정보로 해당 id에 대한 user 인스턴스를 변경
        existing_user.id = user_id # 원래값 그대로 user_id는 유지
        existing_user.name = user.name 
        existing_user.email = user.email 
        existing_user.role = user.role 
        db.commit()
        db.refresh(existing_user)
        # 변경된 내용을 사용자에게 return
        return existing_user
    # 없는 id를 호출했다면
    raise HTTPException(404, '없는 사용자입니다')

# 사용자의 특정 정보를 수정하는 엔드포인트 
@app.patch("/users/{user_id}")
def update_user(user_id: int, updated_fields: dict, db: Session = Depends(get_db)):
    # 사용자id로 db에 사용자정보가 존재하는지 확인 
    existing_user = db.query(User).filter(User.id == user_id).first() # 리스트 안에 값이 들어있지 않고 객체 자체로 값을 가져옵니다.   
    if existing_user:
        # 입력받은 전체 정보로 해당 id에 대한 user 인스턴스를 변경
        for key, value in updated_fields.items():
            if hasattr(existing_user, key): 
                setattr(existing_user, key, value)
        db.commit()
        db.refresh(existing_user)
        return existing_user
    # 없는 id를 호출했다면
    raise HTTPException(404, '없는 사용자입니다')

# 사용자의 id를 받아서 해당 id의 사용자정보만 조회하는 엔드포인트
@app.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user_id).first() # 리스트 안에 값이 들어있지 않고 객체 자체로 값을 가져옵니다.   
    if existing_user:
        return existing_user
        # 없는 id를 호출했다면
    raise HTTPException(404, '없는 사용자입니다')

# 사용자 프로필 조회 엔드포인트
# http://127.0.0.1:8000/profile?token=alice
@app.get("/profile")
def read_profile(current_user: User = Depends(get_current_user)):
    """
    현재 사용자의 프로필 정보를 반환하는 엔드포인트.
    - 모든 인증된 사용자가 접근 가능.
    """
    return {"id": current_user.id, "name": current_user.name, "email": current_user.email, "role": current_user.role}

# 관리자 전용 엔드포인트
@app.get("/admin")
def read_admin_data(admin_user: User = Depends(get_admin_user)):
    """
    관리자만 접근할 수 있는 엔드포인트.
    - 관리자 권한이 없는 사용자는 HTTP 403 에러를 반환.
    """
    return {"message": f"Welcome, {admin_user.name}! You have admin access."}