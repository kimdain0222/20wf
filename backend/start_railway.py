#!/usr/bin/env python3
"""
Railway 환경 전용 서버 시작 스크립트
"""

import os
import sys
import time
import traceback
import subprocess

def check_environment():
    """환경 변수 확인"""
    print("🔍 환경 변수 확인 중...")
    
    # 필수 환경 변수들
    required_vars = ['DATABASE_URL']
    optional_vars = ['POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'OPENAI_API_KEY']
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print(f"❌ 필수 환경 변수 누락: {missing_required}")
        print("💡 Railway 대시보드에서 환경 변수를 설정해주세요.")
        return False
    
    if missing_optional:
        print(f"⚠️ 선택적 환경 변수 누락: {missing_optional}")
    
    print("✅ 환경 변수 설정 완료")
    return True

def test_database_connection():
    """데이터베이스 연결 테스트"""
    try:
        print("🔌 데이터베이스 연결 테스트 중...")
        
        # 간단한 연결 테스트
        import psycopg2
        from dotenv import load_dotenv
        
        load_dotenv()
        
        # PostgreSQL 설정 구성
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            conn = psycopg2.connect(database_url)
            conn.close()
            print("✅ PostgreSQL 연결 성공!")
            return True
        else:
            print("❌ DATABASE_URL이 설정되지 않았습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 데이터베이스 연결 테스트 실패: {e}")
        return False

def check_dependencies():
    """필수 패키지 확인"""
    try:
        print("📦 필수 패키지 확인 중...")
        
        required_packages = [
            'flask', 'psycopg2', 'gunicorn', 'openai', 'python-dotenv'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ 누락된 패키지: {missing_packages}")
            print("💡 pip install -r requirements_postgresql.txt를 실행해주세요.")
            return False
        
        print("✅ 모든 필수 패키지가 설치되어 있습니다.")
        return True
        
    except Exception as e:
        print(f"❌ 패키지 확인 실패: {e}")
        return False

def start_server():
    """서버 시작"""
    try:
        port = os.getenv('PORT', '5000')
        print(f"🌐 서버 시작 중... (포트: {port})")
        
        # Gunicorn 설정
        cmd = [
            "gunicorn",
            "app_postgresql_api:app",
            "--bind", f"0.0.0.0:{port}",
            "--workers", "2",
            "--timeout", "120",
            "--log-level", "info",
            "--preload",
            "--access-logfile", "-",
            "--error-logfile", "-"
        ]
        
        print(f"🔧 실행 명령어: {' '.join(cmd)}")
        
        # 서버 시작
        subprocess.run(cmd, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 서버 시작 실패: {e}")
        return False
    except KeyboardInterrupt:
        print("🛑 서버가 중단되었습니다.")
        return True
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        traceback.print_exc()
        return False

def main():
    """메인 함수"""
    print("🚀 Railway 서버 시작 스크립트 실행...")
    print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
    print(f"🐍 Python 버전: {sys.version}")
    
    # 1. 환경 변수 확인
    if not check_environment():
        print("❌ 환경 변수 문제로 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # 2. 패키지 확인
    if not check_dependencies():
        print("❌ 패키지 문제로 서버를 시작할 수 없습니다.")
        sys.exit(1)
    
    # 3. 데이터베이스 연결 테스트
    if not test_database_connection():
        print("⚠️ 데이터베이스 연결에 문제가 있지만 서버를 시작합니다.")
        print("💡 서버 시작 후 데이터베이스 초기화가 자동으로 실행됩니다.")
    
    # 4. 서버 시작
    print("🎯 서버 시작 준비 완료!")
    if not start_server():
        print("❌ 서버 시작에 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()
