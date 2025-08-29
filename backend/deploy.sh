#!/bin/bash

echo "🚀 배포 스크립트 시작..."

# 데이터베이스 초기화
echo "🔧 데이터베이스 초기화 시작..."
python init_db.py

# 초기화 결과 확인
if [ $? -eq 0 ]; then
    echo "✅ 데이터베이스 초기화 성공!"
else
    echo "❌ 데이터베이스 초기화 실패!"
    exit 1
fi

# Flask 서버 시작
echo "🌐 Flask 서버 시작..."
gunicorn app_postgresql_api:app --bind 0.0.0.0:$PORT --workers 2
