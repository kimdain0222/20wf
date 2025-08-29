# Python 3.9 이미지 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY . .

# 포트 노출
EXPOSE 5000

# 시작 명령어 - 환경 변수 디버그 포함
CMD ["/bin/bash", "-c", "cd /app/backend && echo '🔍 환경 변수 디버그 시작...' && python debug_env.py && echo '🔧 데이터베이스 초기화 시작...' && python init_db.py && echo '🌐 Flask 서버 시작...' && gunicorn app_postgresql_api:app --bind 0.0.0.0:5000 --workers 2"]
