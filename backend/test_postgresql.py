#!/usr/bin/env python3
"""
PostgreSQL 연결 테스트 스크립트
"""

import psycopg2
import psycopg2.extras

# PostgreSQL 설정
POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'welfare_chatbot',
    'user': 'postgres',
    'password': input('PostgreSQL 비밀번호를 입력하세요: '),
    'port': '5432'
}

def test_connection():
    """PostgreSQL 연결 테스트"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        print("✅ PostgreSQL 연결 성공!")
        
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
        
        conn.close()
        print("✅ 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 연결 실패: {e}")

if __name__ == "__main__":
    test_connection()

