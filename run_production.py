import uvicorn
# from dotenv import load_dotenv

if __name__ == "__main__":
    # load_dotenv(".env")  
    # NOTE: 환경변수는 별도로 설정해야 함

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=80,
        reload=False  # 개발 중 코드 변경 시 자동 재시작
    )