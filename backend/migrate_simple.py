#!/usr/bin/env python3
"""
간단한 SQLite → PostgreSQL 마이그레이션 스크립트
"""

import sqlite3
import psycopg2
import json
import os

# 데이터베이스 설정
SQLITE_DB = "welfare_policies.db"
POSTGRES_CONFIG = {
    'host': 'localhost',
    'database': 'welfare_chatbot',
    'user': 'postgres',
    'password': input('PostgreSQL 비밀번호를 입력하세요: '),  # 사용자 입력
    'port': '5432'
}

def connect_sqlite():
    """SQLite 연결"""
    try:
        conn = sqlite3.connect(SQLITE_DB)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"SQLite 연결 실패: {e}")
        return None

def connect_postgresql():
    """PostgreSQL 연결"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        print(f"PostgreSQL 연결 실패: {e}")
        return None

def migrate_policies(sqlite_conn, pg_conn):
    """정책 데이터 마이그레이션"""
    try:
        sqlite_cursor = sqlite_conn.cursor()
        pg_cursor = pg_conn.cursor()
        
        # SQLite에서 정책 데이터 조회
        sqlite_cursor.execute('''
            SELECT id, title, url, region, age_range, application_period, 
                   conditions, benefits, created_at, updated_at
            FROM welfare_policies
        ''')
        
        policies = sqlite_cursor.fetchall()
        print(f"📊 총 {len(policies)}개 정책 마이그레이션 시작...")
        
        for i, policy in enumerate(policies, 1):
            try:
                # 지역 ID 조회
                region_mapping = {'seoul': 'Seoul', 'incheon': 'Incheon', 'gyeonggi': 'Gyeonggi'}
                region_name = region_mapping.get(policy['region'], policy['region'])
                pg_cursor.execute("SELECT id FROM regions WHERE name = %s", (region_name,))
                region_result = pg_cursor.fetchone()
                region_id = region_result[0] if region_result else None
                
                # 카테고리 ID (기본값: Other Support)
                pg_cursor.execute("SELECT id FROM categories WHERE name = %s", ('Other Support',))
                category_result = pg_cursor.fetchone()
                category_id = category_result[0] if category_result else None
                
                # 연령 범위 추출
                age_min, age_max = None, None
                if policy['age_range']:
                    try:
                        age_ranges = json.loads(policy['age_range'])
                        if age_ranges:
                            all_ages = []
                            for age_range in age_ranges:
                                if isinstance(age_range, str) and '대' in age_range:
                                    decade = int(age_range.replace('대', ''))
                                    all_ages.extend([decade, decade + 9])
                                elif isinstance(age_range, (int, float)):
                                    all_ages.append(int(age_range))
                            if all_ages:
                                age_min, age_max = min(all_ages), max(all_ages)
                    except:
                        pass
                
                # PostgreSQL에 정책 삽입
                pg_cursor.execute('''
                    INSERT INTO policies (
                        title, description, url, region_id, category_id,
                        age_min, age_max, conditions, benefits, application_period,
                        created_at, updated_at, status
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                ''', (
                    policy['title'],
                    policy['title'],  # description은 title로 임시 설정
                    policy['url'],
                    region_id,
                    category_id,
                    age_min,
                    age_max,
                    policy['conditions'],
                    policy['benefits'],
                    policy['application_period'],
                    policy['created_at'],
                    policy['updated_at'],
                    'active'
                ))
                
                if i % 10 == 0:
                    print(f"📝 {i}/{len(policies)} 정책 처리 완료")
                    
            except Exception as e:
                print(f"❌ 정책 {policy['id']} 마이그레이션 실패: {e}")
                continue
        
        pg_conn.commit()
        print("✅ 정책 데이터 마이그레이션 완료")
        return True
        
    except Exception as e:
        print(f"❌ 정책 마이그레이션 실패: {e}")
        return False

def verify_migration(sqlite_conn, pg_conn):
    """마이그레이션 검증"""
    try:
        sqlite_cursor = sqlite_conn.cursor()
        pg_cursor = pg_conn.cursor()
        
        # 정책 수 비교
        sqlite_cursor.execute("SELECT COUNT(*) FROM welfare_policies")
        sqlite_count = sqlite_cursor.fetchone()[0]
        
        pg_cursor.execute("SELECT COUNT(*) FROM policies")
        pg_count = pg_cursor.fetchone()[0]
        
        print(f"📊 마이그레이션 검증:")
        print(f"   SQLite: {sqlite_count}개 정책")
        print(f"   PostgreSQL: {pg_count}개 정책")
        
        if sqlite_count == pg_count:
            print("✅ 마이그레이션 성공!")
            return True
        else:
            print("❌ 마이그레이션 실패: 정책 수가 일치하지 않습니다.")
            return False
            
    except Exception as e:
        print(f"❌ 검증 실패: {e}")
        return False

def main():
    """메인 마이그레이션 함수"""
    print("🚀 SQLite → PostgreSQL 마이그레이션 시작")
    print("=" * 60)
    
    # 데이터베이스 연결
    sqlite_conn = connect_sqlite()
    pg_conn = connect_postgresql()
    
    if not sqlite_conn or not pg_conn:
        print("❌ 데이터베이스 연결 실패")
        return
    
    try:
        # 정책 데이터 마이그레이션
        if not migrate_policies(sqlite_conn, pg_conn):
            return
        
        # 마이그레이션 검증
        if not verify_migration(sqlite_conn, pg_conn):
            return
        
        print("\n🎉 마이그레이션 완료!")
        print("이제 PostgreSQL을 사용할 수 있습니다.")
        
    except Exception as e:
        print(f"❌ 마이그레이션 중 오류 발생: {e}")
    
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    main()
