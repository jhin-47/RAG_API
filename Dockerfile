FROM ubuntu:24.04

# 환경 변수 설정
ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONUNBUFFERED="1"
ENV LC_ALL="ko_KR.UTF-8"

# apt 한국 미러로 변경
RUN sed -i 's@archive.ubuntu.com@kr.archive.ubuntu.com@g' /etc/apt/sources.list

# apt 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    locales \ 
    && rm -rf /var/lib/apt/lists/*

# UTF-8로 언어 변경
RUN locale-gen ko_KR.UTF-8

# 가상환경 생성 (PEP 668 대응, Ubuntu 24.04의 업데이트)
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 파이썬 패키지 설치
WORKDIR /
COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# 디렉토리, 코드 가져오기
COPY ./api /api
COPY ./database /database
COPY ./run_production.py /run_production.py

# 환경변수 로드 후 실행
WORKDIR /
CMD ["python3", "run_production.py"]