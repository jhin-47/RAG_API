from dotenv import load_dotenv, dotenv_values


env_path = ".env"

load_dotenv(env_path)  # .env 파일에서 환경변수 로드함


config = dotenv_values(".env")
print("---- ENVIRONMENT VARIABLES ----")
if len(config) == 0:
    print("> No environment variables found")
for k, v in config.items():
    print(f"{k}: {v}")
print("-------------------------------")
