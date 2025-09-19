from fastapi import FastAPI, Response, Request
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

# FastAPI는 기본적으로 세션 기능을 내장하고 있지 않아 SessionMiddleware를 사용해야 합니다. 세션 미들웨어를 추가합니다.
# 'secret_key'는 세션 쿠키를 암호화하는 데 사용됩니다.
# 실제 환경에서는 이 키를 환경 변수로 관리해야 합니다.
app.add_middleware(SessionMiddleware, secret_key="fisaai")

@app.get("/set-cookie")
def set_cookie(response: Response):
    response.set_cookie(key="session_id", value="abc123")
    return {"message": "쿠키 설정됨"}

@app.get("/get-cookie")
def get_cookie(request: Request):
    session_id = request.cookies.get("session_id")
    return {"session_id": session_id}

@app.get("/set-session")
def set_session(request: Request):
    # request.session 딕셔너리를 사용하여 세션에 데이터를 저장합니다.
    request.session["username"] = "fastapi_user"
    return {"message": "세션에 데이터가 저장되었습니다."}

@app.get("/get-session")
def get_session(request: Request):
    # request.session.get() 메서드로 세션 데이터를 가져옵니다.
    username = request.session.get("username", None)
    return {"username": username}

@app.get("/clear-session")
def clear_session(request: Request):
    # request.session.clear()를 사용하여 모든 세션 데이터를 삭제합니다.
    request.session.clear()
    return {"message": "세션 데이터가 삭제되었습니다."}