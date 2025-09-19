from fastapi import FastAPI
# uvicorn app:app --reload
app = FastAPI()

## 함수를 하나만 만들어주세요. main -> hello라는 문자열을 리턴합니다. 
@app.get("/hello/") # / 
def main():
    return 'hello'
    