#!/bin/bash

# Railway PostgreSQL 배포 스크립트

echo "🚀 Railway PostgreSQL 배포 시작..."

# 1. 연결 테스트
echo "🔍 PostgreSQL 연결 테스트 중..."
python test_connection.py

if [ $? -eq 0 ]; then
    echo "✅ 연결 테스트 성공!"
else
    echo "❌ 연결 테스트 실패!"
    echo "💡 Railway 대시보드에서 환경 변수를 확인하세요."
    exit 1
fi

# 2. 데이터베이스 초기화
echo "🔧 데이터베이스 초기화 중..."
python init_db.py

if [ $? -eq 0 ]; then
    echo "✅ 데이터베이스 초기화 성공!"
else
    echo "❌ 데이터베이스 초기화 실패!"
    exit 1
fi

# 3. 서버 시작
echo "🌐 Flask 서버 시작 중..."
python start_server.py

echo "✅ 배포 완료!"
