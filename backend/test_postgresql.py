#!/usr/bin/env python3
"""
PostgreSQL 연결 테스트 스크립트
Railway 환경에서 사용
"""

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# PostgreSQL 설정 (Railway 환경 변수 사용)
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', os.getenv('PGHOST')),
    'database': os.getenv('POSTGRES_DB', os.getenv('PGDATABASE')),
    'user': os.getenv('POSTGRES_USER', os.getenv('PGUSER')),
    'password': os.getenv('POSTGRES_PASSWORD', os.getenv('PGPASSWORD')),
    'port': os.getenv('POSTGRES_PORT', os.getenv('PGPORT', '5432'))
}

def test_connection():
    """PostgreSQL 연결 테스트"""
    try:
        print("🔍 PostgreSQL 연결 정보:")
        print(f"   Host: {POSTGRES_CONFIG['host']}")
        print(f"   Database: {POSTGRES_CONFIG['database']}")
        print(f"   User: {POSTGRES_CONFIG['user']}")
        print(f"   Port: {POSTGRES_CONFIG['port']}")
        print(f"   Password: {'*' * len(POSTGRES_CONFIG['password']) if POSTGRES_CONFIG['password'] else 'None'}")
        
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        print("✅ PostgreSQL 연결 성공!")
        
        # 서버 정보 확인
        cursor.execute("SELECT version()")
        version = cursor.fetchone()
        print(f"📊 PostgreSQL 버전: {version['version']}")
        
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'policies'
            );
        """)
        table_exists = cursor.fetchone()
        print(f"📊 policies 테이블 존재: {table_exists['exists']}")
        
        if table_exists['exists']:
            # 정책 수 확인
            cursor.execute("SELECT COUNT(*) as count FROM policies")
            result = cursor.fetchone()
            print(f"📊 총 정책 수: {result['count']}개")
            
            # 지역별 정책 수 확인
            cursor.execute('''
                SELECT r.name, COUNT(*) as count
                FROM policies p
                LEFT JOIN regions r ON p.region_id = r.id
                GROUP BY r.name
                ORDER BY count DESC
            ''')
            regions = cursor.fetchall()
            print("📊 지역별 정책 수:")
            for region in regions:
                print(f"   {region['name']}: {region['count']}개")
            
            # 카테고리별 정책 수 확인
            cursor.execute('''
                SELECT c.name, COUNT(*) as count
                FROM policies p
                LEFT JOIN categories c ON p.category_id = c.id
                GROUP BY c.name
                ORDER BY count DESC
            ''')
            categories = cursor.fetchall()
            print("📊 카테고리별 정책 수:")
            for category in categories:
                print(f"   {category['name']}: {category['count']}개")
        else:
            print("⚠️ policies 테이블이 존재하지 않습니다. 데이터베이스 초기화가 필요합니다.")
        
        conn.close()
        print("✅ 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
        print("🔍 환경 변수 확인:")
        print(f"   POSTGRES_HOST: {os.getenv('POSTGRES_HOST')}")
        print(f"   PGHOST: {os.getenv('PGHOST')}")
        print(f"   POSTGRES_DB: {os.getenv('POSTGRES_DB')}")
        print(f"   PGDATABASE: {os.getenv('PGDATABASE')}")
        print(f"   POSTGRES_USER: {os.getenv('POSTGRES_USER')}")
        print(f"   PGUSER: {os.getenv('PGUSER')}")
        print(f"   POSTGRES_PASSWORD: {'*' * len(os.getenv('POSTGRES_PASSWORD', '')) if os.getenv('POSTGRES_PASSWORD') else 'None'}")
        print(f"   PGPASSWORD: {'*' * len(os.getenv('PGPASSWORD', '')) if os.getenv('PGPASSWORD') else 'None'}")

if __name__ == "__main__":
    test_connection()

