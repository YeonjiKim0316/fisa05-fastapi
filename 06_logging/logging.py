import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# 로깅 기본 설정
# 1. 포맷터 정의: 로그 메시지 포맷을 지정
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 2. 콘솔 핸들러: 콘솔(터미널)에 로그 출력
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(logging.INFO) # INFO 레벨 이상만 출력

# 3. 파일 핸들러: 파일에 로그 기록
file_handler = logging.FileHandler('fastapi_app.log')
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.WARNING) # WARNING 레벨 이상만 기록

# 4. 로거 객체 생성 및 핸들러 추가
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # 로거의 최소 레벨 설정 (DEBUG 레벨부터 모두 처리)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# FastAPI 앱 인스턴스
app = FastAPI()

@app.get("/")
def read_root():
    logger.debug("Debug 로그: 루트 경로에 접근했습니다.")
    logger.info("Info 로그: 사용자 요청을 처리 중입니다.")
    logger.warning("Warning 로그: 중요한 경고가 발생했습니다.")
    logger.error("Error 로그: 심각한 에러가 발생했습니다!")
    logger.critical("Critical 로그: 치명적인 문제가 발생했습니다!")
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int):
    logger.info(f"Item ID: {item_id} 요청이 들어왔습니다.")
    if item_id > 100:
        logger.warning(f"Item ID {item_id}가 100을 초과했습니다. 비정상적인 접근일 수 있습니다.")
        return JSONResponse(status_code=400, content={"message": "Item ID too large"})
    return {"item_id": item_id}