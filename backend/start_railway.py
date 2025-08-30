#!/usr/bin/env python3
"""
Railway 환경 전용 서버 시작 스크립트
"""

import os
import sys
import time
import traceback

def check_environment():
    """환경 변수 확인"""
    print("🔍 환경 변수 확인 중...")
    
    required_vars = ['DATABASE_URL', 'PGPASSWORD', 'POSTGRES_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ 누락된 환경 변수: {missing_vars}")
        print("💡 Railway 대시보드에서 환경 변수를 설정해주세요.")
        return False
    
    print("✅ 필수 환경 변수가 모두 설정되어 있습니다.")
    return True

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        print("🔌 데이터베이스 연결 테스트 중...")
        from test_connection import main as test_connection
        test_connection()
        return True
    except Exception as e:
        print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
        return False

def start_server():
    """서버 시작"""
    try:
        import subprocess
        
        port = os.getenv('PORT', '5000')
        print(f"🌐 서버 시작 중... (포트: {port})")
        
        cmd = [
            "gunicorn",
            "app_postgresql_api:app",
            "--bind", f"0.0.0.0:{port}",
            "--workers", "2",
            "--timeout", "120",
            "--log-level", "info",
            "--preload"
        ]
        
        print(f"🔧 실행 명령어: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 서버 시작 실패: {e}")
        return False
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    print("🚀 Railway 서버 시작 스크립트 실행...")
    print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
    
    # 1. 환경 변수 확인
    if not check_environment():
        print("❌ 환경 변수 문제로 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # 2. 데이터베이스 연결 테스트
    if not test_database_connection():
        print("⚠️ 데이터베이스 연결에 문제가 있지만 서버를 시작합니다.")
    
    # 3. 서버 시작
    if not start_server():
        print("❌ 서버 시작에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
