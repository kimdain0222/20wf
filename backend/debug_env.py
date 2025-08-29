#!/usr/bin/env python3
"""
환경 변수 디버그 스크립트
Railway에서 설정된 환경 변수를 확인합니다.
"""

import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

print("🔍 환경 변수 디버그 시작...")
print(f"📁 현재 작업 디렉토리: {os.getcwd()}")

# PostgreSQL 관련 환경 변수들
postgres_vars = [
    'PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGPORT',
    'POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_PORT'
]

print("\n📡 PostgreSQL 환경 변수:")
for var in postgres_vars:
    value = os.getenv(var)
    if value:
        # 비밀번호는 일부만 표시
        if 'PASSWORD' in var:
            display_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
        else:
            display_value = value
        print(f"  {var}: {display_value}")
    else:
        print(f"  {var}: None")

# 모든 환경 변수 출력 (디버그용)
print("\n🌍 모든 환경 변수:")
for key, value in os.environ.items():
    if 'PASSWORD' in key:
        display_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else '***'
    else:
        display_value = value
    print(f"  {key}: {display_value}")

print("\n✅ 환경 변수 디버그 완료!")
