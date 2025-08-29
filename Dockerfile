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

# 데이터베이스 초기화 스크립트 실행 권한 부여
RUN chmod +x backend/init_db.py
RUN chmod +x backend/start_server.py

# 포트 노출
EXPOSE 5000

# 시작 스크립트 생성
RUN echo '#!/bin/bash\n\
echo "🚀 Docker 컨테이너 시작..."\n\
cd /app/backend\n\
echo "🔧 데이터베이스 초기화 시작..."\n\
python init_db.py\n\
if [ $? -eq 0 ]; then\n\
    echo "✅ 데이터베이스 초기화 성공!"\n\
else\n\
    echo "❌ 데이터베이스 초기화 실패!"\n\
fi\n\
echo "🌐 Flask 서버 시작..."\n\
gunicorn app_postgresql_api:app --bind 0.0.0.0:5000 --workers 2\n\
' > /app/start.sh

RUN chmod +x /app/start.sh

# 시작 명령어
CMD ["/app/start.sh"]
