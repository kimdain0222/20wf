#!/usr/bin/env python3
"""
통합 서버 시작 스크립트
데이터베이스 초기화 후 Flask 서버를 시작합니다.
"""

import os
import sys
import subprocess
import time
import traceback

def main():
    print("🚀 통합 서버 시작 스크립트 실행...")
    print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
    print(f"📁 파일 목록: {os.listdir('.')}")
    
    # 1. 데이터베이스 초기화 시도
    print("🔧 데이터베이스 초기화 시작...")
    try:
        from init_db import initialize_database
        success = initialize_database()
        
        if success:
            print("✅ 데이터베이스 초기화 성공!")
        else:
            print("❌ 데이터베이스 초기화 실패!")
            print("⚠️ 서버를 시작하지만 데이터베이스 연결에 문제가 있을 수 있습니다.")
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 중 오류 발생: {e}")
        print("⚠️ 서버를 시작하지만 데이터베이스 연결에 문제가 있을 수 있습니다.")
        traceback.print_exc()
    
    # 2. Flask 서버 시작
    print("🌐 Flask 서버 시작...")
    print("🔄 gunicorn으로 서버를 시작합니다...")
    
    # 환경 변수 확인
    port = os.getenv('PORT', '5000')
    print(f"📡 서버 포트: {port}")
    
    # gunicorn 명령어 실행
    cmd = [
        "gunicorn", 
        "app_postgresql_api:app", 
        "--bind", f"0.0.0.0:{port}", 
        "--workers", "2",
        "--timeout", "120",
        "--log-level", "info"
    ]
    
    print(f"🔧 실행 명령어: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ gunicorn 실행 실패: {e}")
        print("🔍 오류 상세 정보:")
        traceback.print_exc()
        sys.exit(1)
    except KeyboardInterrupt:
        print("🛑 서버가 중단되었습니다.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
