#!/usr/bin/env python3
"""
Railway 배포 전 로컬 테스트 스크립트
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def test_environment():
    """환경 변수 테스트"""
    print("🔍 환경 변수 테스트...")
    
    required_vars = ['DATABASE_URL']
    optional_vars = ['OPENAI_API_KEY']
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 설정됨")
        else:
            print(f"❌ {var}: 누락됨")
            return False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: 설정됨")
        else:
            print(f"⚠️ {var}: 누락됨 (선택사항)")
    
    return True

def test_database_connection():
    """데이터베이스 연결 테스트"""
    print("🔌 데이터베이스 연결 테스트...")
    
    try:
        import psycopg2
        import urllib.parse
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL이 설정되지 않았습니다.")
            return False
        
        # URL 디코딩 추가
        decoded_url = urllib.parse.unquote(database_url)
        
        conn = psycopg2.connect(decoded_url)
        cursor = conn.cursor()
        
        # 간단한 쿼리 테스트
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL 연결 성공: {version[0]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False

def test_flask_app():
    """Flask 앱 테스트"""
    print("🌐 Flask 앱 테스트...")
    
    try:
        # Flask 앱 임포트
        from app_postgresql_api import app
        
        # 테스트 클라이언트 생성
        with app.test_client() as client:
            # 홈페이지 테스트
            response = client.get('/')
            if response.status_code == 200:
                print("✅ 홈페이지 엔드포인트 정상")
            else:
                print(f"❌ 홈페이지 엔드포인트 오류: {response.status_code}")
                return False
            
            # 헬스체크 테스트
            response = client.get('/api/health')
            if response.status_code == 200:
                print("✅ 헬스체크 엔드포인트 정상")
            else:
                print(f"❌ 헬스체크 엔드포인트 오류: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Flask 앱 테스트 실패: {e}")
        return False

def test_database_initialization():
    """데이터베이스 초기화 테스트"""
    print("🔧 데이터베이스 초기화 테스트...")
    
    try:
        from app_postgresql_api import initialize_database
        
        success = initialize_database()
        if success:
            print("✅ 데이터베이스 초기화 성공")
        else:
            print("❌ 데이터베이스 초기화 실패")
        
        return success
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 테스트 실패: {e}")
        return False

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print("📡 API 엔드포인트 테스트...")
    
    try:
        from app_postgresql_api import app
        
        with app.test_client() as client:
            # 정책 목록 조회
            response = client.get('/api/policies?limit=5')
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"✅ 정책 목록 조회 성공: {len(data.get('policies', []))}개")
                else:
                    print(f"❌ 정책 목록 조회 실패: {data.get('error')}")
                    return False
            else:
                print(f"❌ 정책 목록 조회 오류: {response.status_code}")
                return False
            
            # 지역 목록 조회
            response = client.get('/api/regions')
            if response.status_code == 200:
                data = response.get_json()
                if data.get('success'):
                    print(f"✅ 지역 목록 조회 성공: {len(data.get('regions', []))}개")
                else:
                    print(f"❌ 지역 목록 조회 실패: {data.get('error')}")
                    return False
            else:
                print(f"❌ 지역 목록 조회 오류: {response.status_code}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API 엔드포인트 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("🧪 Railway 배포 전 테스트 시작...")
    print("=" * 50)
    
    tests = [
        ("환경 변수", test_environment),
        ("데이터베이스 연결", test_database_connection),
        ("Flask 앱", test_flask_app),
        ("데이터베이스 초기화", test_database_initialization),
        ("API 엔드포인트", test_api_endpoints)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} 테스트 중...")
        try:
            if test_func():
                print(f"✅ {test_name} 테스트 통과")
                passed += 1
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 오류: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 테스트 결과: {passed}/{total} 통과")
    
    if passed == total:
        print("🎉 모든 테스트가 통과했습니다! Railway 배포 준비 완료!")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 문제를 해결한 후 다시 시도해주세요.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
