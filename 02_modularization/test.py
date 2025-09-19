from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# 템플릿 디렉토리 설정
templates = Jinja2Templates(directory="templates")

# SQLAlchemy 기본 설정
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy 모델 정의
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String, default="user")

# 데이터베이스 초기화
Base.metadata.create_all(bind=engine)

# FastAPI 애플리케이션 생성
app = FastAPI()

# 데이터베이스 세션 종속성 정의
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 인증 토큰 검증 함수
def get_current_user(token: str, db: Session = Depends(get_db)):
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
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )
    return current_user

# --- 웹 페이지 라우트 ---

# 메인 페이지 라우트 (GET 요청)
# 사용자를 생성하는 폼과 목록을 보여줍니다.
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).all()
    return templates.TemplateResponse("index.html", {"request": request, "users": users})

# 사용자 생성 라우트 (POST 요청)
# 폼을 통해 제출된 데이터를 처리하여 새 사용자를 생성하고 메인 페이지로 리디렉션합니다.
@app.post("/users/", response_class=HTMLResponse)
def create_user_from_form(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    role: str = Form("user"),
    db: Session = Depends(get_db)
):
    try:
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = User(name=name, email=email, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        users = db.query(User).all()
        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "users": users,
                "success_message": f"사용자 '{name}'이(가) 성공적으로 생성되었습니다!"
            }
        )
    except HTTPException as e:
        users = db.query(User).all()
        return templates.TemplateResponse(
            "home.html",
            {
                "request": request,
                "users": users,
                "error_message": e.detail
            }
        )

# 사용자 프로필 라우트 (GET 요청)
# 인증 토큰으로 사용자를 확인하고 프로필 페이지를 보여줍니다.
@app.get("/profile", response_class=HTMLResponse)
def read_profile(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": current_user})

# 관리자 전용 라우트 (GET 요청)
# 관리자 권한이 있는 사용자에게만 관리자 페이지를 보여줍니다.
@app.get("/admin", response_class=HTMLResponse)
def read_admin_data(request: Request, admin_user: User = Depends(get_admin_user)):
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "message": f"안녕하세요, {admin_user.name}님! 관리자 페이지에 오신 것을 환영합니다."}
    )