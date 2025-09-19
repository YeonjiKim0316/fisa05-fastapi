
from typing import Optional
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel # 여러개의 입력값을 class로 만들어서 강제하려고 할 때는 
 
app = FastAPI()

# get (조회), post (생성), put / patch (수정), delete (삭제)

# 데이터 모델, class 모델, ENTITY
# input과 output에 들어갈 class를 강제 - request / response 둘의 엔티티를 분리할 때 
class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    on_offer: Optional[bool] = False


# 변경을 하지말아야 하는 컬럼, 보안상 return 하면 안되는 컬럼을 가리기 위해
class UpdateItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None
    on_offer: Optional[bool] = False

# 새로 등록한 상품을 저장하기 위한 list를 함수 바깥에 정의해주겠습니다.
items = [
    Item(id=1, name="연필", description="절대 부러지지 않음", price=10.0),
    Item(id=2, name="공책", description="절대 찢어지지 않음", price=20.0, on_offer=True),
    Item(id=3, name="책갈피", description="형광색이라 눈에 잘 띔", price=30.0, on_offer=False),
]


# 중복을 허용하지 않고 싶어요 - 최종 결과는 새로 추가한 값만 출력되도록 바꾸고 싶어요.
@app.post("/items/", response_model=Item, summary="새 상품 추가", description="새 상품을 추가합니다. 아이템의 ID는 고유해야 하며, 중복을 허용하지 않습니다. 결과값으로 등록된 상품을 반환합니다.")
def create_item(item: Item): # 모델과 일치하지 않으면 FastAPI가 자동으로 오류 처리 / 데이터를 반환
    # 중복 체크 
    for exisiting_item in items:
        #  print(exisiting_item)
         if exisiting_item.id == item.id:
             raise HTTPException(status_code=400, detail="이미 있는 id를 입력했습니다.")
    items.append(item)
    return item

# 전체 목록 조회 - 모든 항목 반환
# @app.get("/items/")
# def read_items():
#     return items

# pagination: skip과 limit이라는 쿼리 매개변수를 사용하여 데이터를 건너뛰고 제한하는 방식으로 동작
#  /items/?skip=2&limit=5로 요청하면, 서버는 데이터를 10개 건너뛰고 그다음 5개를 반환하도록 설계
@app.get("/items/")
def read_items(skip: int = Query(0), limit: int = Query(10)):
    return items[skip : skip + limit]

# 특정 아이템 조회 - 경로 매개변수 사용
## 매개변수 사용
# 1. {변수명}으로 기본적인 경로 매개변수 사용 특정 아이템 조회 
@app.get("/items/{item_id}")
def read_item(item_id: int):
    for exisiting_item in items:
        if exisiting_item.id == item_id:
            return exisiting_item
    raise HTTPException(404, '없는 상품입니다')

# ▶ 사용 예시:
# GET /items/123
# → {"item_id": 123}
# 특정 아이템 수정
# put (모두를 갈아끼우기)
@app.put("/items/{item_id}")
def update_item(item_id: int, updated_item: Item): # 수정해야하는 item 번호, 변경할 내용
    # 전체 데이터 중에 일치하는 id와, 그 방번호를 찾아서 
    # 입력받은 정보를 방번호에 바꿔끼웁니다. 
    for idx, exisiting_item in enumerate(items):
        if exisiting_item.id == item_id:
            items[idx] = updated_item
            return updated_item
    # 없는 번호를 호출했다면 
    raise HTTPException(404, '없는 상품입니다')


# 특정 아이템 수정
# patch (일부만 갈아끼우기)  # {'name': '연필2', 'description':'안깎아도 되는 돌림연필'}
@app.patch("/items/{item_id}", response_model=UpdateItem)   
def patch_item(item_id: int, updated_fields: dict): # 수정해야하는 item 번호, 변경할 내용
    # 전체 데이터 중에 일치하는 id와, 그 방번호를 찾아서 
    # 입력받은 정보를 방번호에 바꿔끼웁니다. 
    for exisiting_item in items:
        if exisiting_item.id == item_id:
            # 업데이트될 필드와 일치하는 k의 v를 수정 
            for key, value in updated_fields.items():
                if hasattr(exisiting_item, key): 
                    setattr(exisiting_item, key, value)
                return exisiting_item
    # 없는 번호를 호출했다면 
    raise HTTPException(404, '없는 상품입니다')

# ▶ 사용 예시:
# GET /users/42/items/abc123
# → {"user_id": 42, "item_id": "abc123"}

# 삭제 - 개별 아이템 조회 -> 삭제 
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for idx, existing_item in enumerate(items):
        if existing_item.id == item_id:
            del items[idx]
            return {"message": f"{item_id}에 대한 삭제가 완료되었습니다."}
    raise HTTPException(404, "찾는 아이템이 없습니다")

# 3. 경로 매개변수 + 쿼리 매개변수 혼합
# quantity 라는 변수로 몇개를 살 건지 함께 전달
@app.get("/products/{product_id}")
def get_product(product_id: int, q: str = None, quantity: int = 0):
    return f'상품번호 {product_id} 품목 {q}를 {quantity}개 구매합니다.'


# ▶ 사용 예시:
# GET /products/10?q=shoes
# → {"product_id": 10, "query": "shoes"}


# 4. 경로 매개변수에서 값 제한하기 (enum, regex 등 가능)
from enum import Enum

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

# int, string, float, list 도 결국에는 파이썬이 사람들이 많이 쓰니까 만들어놓은 CLASS에 불과합니다.
@app.get("/models/{model_name}")
def get_model(model_name: ModelName):
    return {"model_name": model_name}

# ▶ 사용 예시:
# GET /models/resnet
# → {"model_name": "resnet"}

# GET /models/unknown
# → 422 Unprocessable Entity (잘못된 값)