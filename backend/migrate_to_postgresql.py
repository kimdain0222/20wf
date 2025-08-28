#!/usr/bin/env python3
"""
SQLite에서 PostgreSQL로 데이터 마이그레이션 스크립트
"""

import sqlite3
import psycopg2
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 데이터베이스 설정
SQLITE_DB = "welfare_policies.db"
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'database': os.getenv('POSTGRES_DB', 'welfare_chatbot'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
    'port': os.getenv('POSTGRES_PORT', '5432')
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

def create_postgresql_schema(conn):
    """PostgreSQL 스키마 생성"""
    try:
        with open('database_schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
        
        cursor = conn.cursor()
        cursor.execute(schema)
        conn.commit()
        print("✅ PostgreSQL 스키마 생성 완료")
        return True
    except Exception as e:
        print(f"❌ 스키마 생성 실패: {e}")
        return False

def migrate_regions(sqlite_conn, pg_conn):
    """지역 데이터 마이그레이션"""
    try:
        sqlite_cursor = sqlite_conn.cursor()
        pg_cursor = pg_conn.cursor()
        
        # 지역 매핑
        region_mapping = {
            'seoul': '서울특별시',
            'incheon': '인천광역시',
            'gyeonggi': '경기도'
        }
        
        for old_code, new_name in region_mapping.items():
            pg_cursor.execute(
                "INSERT INTO regions (code, name, level) VALUES (%s, %s, %s) ON CONFLICT (code) DO NOTHING",
                (old_code, new_name, 1)
            )
        
        pg_conn.commit()
        print("✅ 지역 데이터 마이그레이션 완료")
        return True
    except Exception as e:
        print(f"❌ 지역 마이그레이션 실패: {e}")
        return False

def migrate_categories(sqlite_conn, pg_conn):
    """카테고리 데이터 마이그레이션"""
    try:
        pg_cursor = pg_conn.cursor()
        
        # 기본 카테고리들은 이미 스키마에서 생성됨
        print("✅ 카테고리 데이터 마이그레이션 완료")
        return True
    except Exception as e:
        print(f"❌ 카테고리 마이그레이션 실패: {e}")
        return False

def categorize_policy(title, conditions, benefits):
    """정책 제목과 내용을 기반으로 카테고리 분류"""
    text = f"{title} {conditions} {benefits}".lower()
    
    if any(keyword in text for keyword in ['주택', '월세', '전세', '임대', '거주']):
        return '주거지원'
    elif any(keyword in text for keyword in ['창업', '취업', '일자리', '사업', '근로']):
        return '취업지원'
    elif any(keyword in text for keyword in ['문화', '여가', '체육', '레저', '관광']):
        return '문화생활'
    elif any(keyword in text for keyword in ['교통', '버스', '지하철', '택시', '이동']):
        return '교통지원'
    elif any(keyword in text for keyword in ['저축', '적금', '예금', '금융']):
        return '저축지원'
    elif any(keyword in text for keyword in ['의료', '병원', '건강', '치료', '검진']):
        return '의료지원'
    elif any(keyword in text for keyword in ['학자금', '교육', '장학금', '등록금', '학비']):
        return '교육지원'
    else:
        return '기타지원'

def extract_age_range(age_range_str):
    """연령 범위 문자열에서 최소/최대 연령 추출"""
    if not age_range_str:
        return None, None
    
    try:
        age_ranges = json.loads(age_range_str)
        if not age_ranges:
            return None, None
        
        # 모든 연령 범위에서 최소/최대 찾기
        all_ages = []
        for age_range in age_ranges:
            if isinstance(age_range, str):
                # "20대", "30대" 형태 처리
                if '대' in age_range:
                    decade = int(age_range.replace('대', ''))
                    all_ages.extend([decade, decade + 9])
                else:
                    # 숫자만 있는 경우
                    try:
                        all_ages.append(int(age_range))
                    except:
                        pass
            elif isinstance(age_range, (int, float)):
                all_ages.append(int(age_range))
        
        if all_ages:
            return min(all_ages), max(all_ages)
        return None, None
    except:
        return None, None

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
                # 카테고리 분류
                category_name = categorize_policy(policy['title'], policy['conditions'], policy['benefits'])
                
                # 카테고리 ID 조회
                pg_cursor.execute("SELECT id FROM categories WHERE name = %s", (category_name,))
                category_result = pg_cursor.fetchone()
                category_id = category_result[0] if category_result else None
                
                # 지역 ID 조회
                region_mapping = {'seoul': '서울특별시', 'incheon': '인천광역시', 'gyeonggi': '경기도'}
                region_name = region_mapping.get(policy['region'], policy['region'])
                pg_cursor.execute("SELECT id FROM regions WHERE name = %s", (region_name,))
                region_result = pg_cursor.fetchone()
                region_id = region_result[0] if region_result else None
                
                # 연령 범위 추출
                age_min, age_max = extract_age_range(policy['age_range'])
                
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
        # 1. PostgreSQL 스키마 생성
        if not create_postgresql_schema(pg_conn):
            return
        
        # 2. 지역 데이터 마이그레이션
        if not migrate_regions(sqlite_conn, pg_conn):
            return
        
        # 3. 카테고리 데이터 마이그레이션
        if not migrate_categories(sqlite_conn, pg_conn):
            return
        
        # 4. 정책 데이터 마이그레이션
        if not migrate_policies(sqlite_conn, pg_conn):
            return
        
        # 5. 마이그레이션 검증
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
