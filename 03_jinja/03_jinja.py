from fastapi import FastAPI, Request
# jinja 형식으로 작성된 html 파일을 렌더링해주기 위한 모듈
from fastapi.templating import Jinja2Templates
from typing import Optional
from pydantic import BaseModel # 여러개의 입력값을 class로 만들어서 강제하려고 할 때는 
 

# html을 파일을 변경할 때 바로 변경사항 반영하도록 auto_reload=True
templates = Jinja2Templates(directory='templates', auto_reload=True)
# html 파일들의 경로 templates 안에 작성해줍니다.
app = FastAPI()

# 데이터 모델, class 모델, ENTITY
# input과 output에 들어갈 class를 강제 - request / response 둘의 엔티티를 분리할 때 
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    on_offer: Optional[bool] = False


@app.get("/info")
def user_info(request: Request):
    user_data = {
        "name": "홍길동",
        "username": "hong",
        "role": "user",
        "tasks": ["공지사항", "설정", "로그아웃"],
        "price": 12345.6789
    }
  
    return templates.TemplateResponse("userinfo.html", {"request": request, "user": user_data })
    

items = [
    Item(id=1, name="연필", description="절대 부러지지 않음", price=10.0),
    Item(id=2, name="공책", description="절대 찢어지지 않음", price=20.0, on_offer=True),
    Item(id=3, name="책갈피", description="형광색이라 눈에 잘 띔", price=30.0, on_offer=False),
]

### items 객체를 test.html에 전달해서 각 객체안에 있는 모든 값을 출력하는 함수 item_info()를 만들어주시고. /items 라는 엔드포인트로 호출하도록 만듭니다.
@app.get("/items/")
def item_info(request:Request):
    return templates.TemplateResponse("test.html", {"request":request, "items": items})