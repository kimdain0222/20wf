#!/usr/bin/env python3
"""
Railway PostgreSQL 연결 테스트 및 진단 스크립트
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

def check_environment_variables():
    """환경 변수 확인"""
    print("🔍 환경 변수 확인 중...")
    
    # Railway PostgreSQL 환경 변수들
    railway_vars = [
        'DATABASE_URL',
        'PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD', 'PGPORT',
        'POSTGRES_HOST', 'POSTGRES_DB', 'POSTGRES_USER', 'POSTGRES_PASSWORD', 'POSTGRES_PORT'
    ]
    
    found_vars = {}
    for var in railway_vars:
        value = os.getenv(var)
        if value:
            if 'PASSWORD' in var:
                found_vars[var] = '*' * len(value)
            else:
                found_vars[var] = value
        else:
            found_vars[var] = None
    
    print("📋 환경 변수 상태:")
    for var, value in found_vars.items():
        status = "✅" if value else "❌"
        print(f"   {status} {var}: {value}")
    
    return found_vars

def parse_database_url(database_url):
    """DATABASE_URL 파싱"""
    if not database_url:
        return None
    
    try:
        # postgresql://user:password@host:port/database 형식 파싱
        if database_url.startswith('postgresql://'):
            parts = database_url.replace('postgresql://', '').split('@')
            if len(parts) == 2:
                user_pass = parts[0].split(':')
                host_port_db = parts[1].split('/')
                
                if len(user_pass) >= 2 and len(host_port_db) >= 2:
                    user = user_pass[0]
                    password = user_pass[1]
                    host_port = host_port_db[0].split(':')
                    host = host_port[0]
                    port = host_port[1] if len(host_port) > 1 else '5432'
                    database = host_port_db[1]
                    
                    return {
                        'host': host,
                        'database': database,
                        'user': user,
                        'password': password,
                        'port': port
                    }
    except Exception as e:
        print(f"⚠️ DATABASE_URL 파싱 실패: {e}")
    
    return None

def get_postgres_config():
    """PostgreSQL 설정 구성"""
    print("🔧 PostgreSQL 설정 구성 중...")
    
    # 1. DATABASE_URL에서 파싱 시도
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        config = parse_database_url(database_url)
        if config:
            print("✅ DATABASE_URL에서 설정을 파싱했습니다.")
            return config
    
    # 2. 개별 환경 변수 사용
    config = {
        'host': os.getenv('POSTGRES_HOST', os.getenv('PGHOST')),
        'database': os.getenv('POSTGRES_DB', os.getenv('PGDATABASE')),
        'user': os.getenv('POSTGRES_USER', os.getenv('PGUSER')),
        'password': os.getenv('POSTGRES_PASSWORD', os.getenv('PGPASSWORD')),
        'port': os.getenv('POSTGRES_PORT', os.getenv('PGPORT', '5432'))
    }
    
    print("✅ 개별 환경 변수에서 설정을 구성했습니다.")
    return config

def test_connection(config):
    """PostgreSQL 연결 테스트"""
    print("🔌 PostgreSQL 연결 테스트 중...")
    
    print("📋 연결 설정:")
    print(f"   Host: {config['host']}")
    print(f"   Database: {config['database']}")
    print(f"   User: {config['user']}")
    print(f"   Port: {config['port']}")
    print(f"   Password: {'*' * len(config['password']) if config['password'] else 'None'}")
    
    try:
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        
        print("✅ PostgreSQL 연결 성공!")
        
        # 서버 정보 확인
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL 버전: {version[0]}")
        
        # 현재 데이터베이스 확인
        cursor.execute("SELECT current_database()")
        current_db = cursor.fetchone()
        print(f"📊 현재 데이터베이스: {current_db[0]}")
        
        # 테이블 목록 확인
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"📊 테이블 목록 ({len(tables)}개):")
        for table in tables:
            print(f"   - {table[0]}")
        
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ 연결 실패 (OperationalError): {e}")
        return False
    except psycopg2.AuthenticationFailed as e:
        print(f"❌ 인증 실패 (AuthenticationFailed): {e}")
        return False
    except Exception as e:
        print(f"❌ 연결 실패 (기타): {e}")
        return False

def main():
    """메인 함수"""
    print("🚀 Railway PostgreSQL 연결 테스트 시작...")
    print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
    
    # 1. 환경 변수 확인
    env_vars = check_environment_variables()
    
    # 2. PostgreSQL 설정 구성
    config = get_postgres_config()
    
    # 3. 연결 테스트
    success = test_connection(config)
    
    if success:
        print("✅ 모든 테스트가 성공했습니다!")
        sys.exit(0)
    else:
        print("❌ 연결 테스트가 실패했습니다.")
        print("💡 해결 방법:")
        print("   1. Railway 대시보드에서 PostgreSQL 서비스가 실행 중인지 확인")
        print("   2. 환경 변수가 올바르게 설정되었는지 확인")
        print("   3. PostgreSQL 서비스의 연결 정보를 다시 확인")
        sys.exit(1)

if __name__ == "__main__":
    main()
