#!/usr/bin/env python3
"""
통합 서버 시작 스크립트
데이터베이스 초기화 후 Flask 서버를 시작합니다.
"""

import os
import sys
import subprocess
import time
from init_db import initialize_database

def main():
    print("🚀 통합 서버 시작 스크립트 실행...")
    print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
    print(f"📁 파일 목록: {os.listdir('.')}")
    
    # 1. 데이터베이스 초기화
    print("🔧 데이터베이스 초기화 시작...")
    success = initialize_database()
    
    if success:
        print("✅ 데이터베이스 초기화 성공!")
    else:
        print("❌ 데이터베이스 초기화 실패!")
        print("⚠️ 서버를 시작하지만 데이터베이스 연결에 문제가 있을 수 있습니다.")
    
    # 2. Flask 서버 시작
    print("🌐 Flask 서버 시작...")
    print("🔄 gunicorn으로 서버를 시작합니다...")
    
    # gunicorn 명령어 실행
    cmd = [
        "gunicorn", 
        "app_postgresql_api:app", 
        "--bind", "0.0.0.0:5000", 
        "--workers", "2"
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ gunicorn 실행 실패: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 서버가 중단되었습니다.")
        sys.exit(0)

if __name__ == '__main__':
    main()
