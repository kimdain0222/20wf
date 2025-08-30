#!/usr/bin/env python3
"""
데이터베이스 초기화 스크립트
Railway에서 별도로 실행하여 데이터베이스를 초기화합니다.
"""

import os
import sys
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

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
    # 1. DATABASE_URL에서 파싱 시도
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        config = parse_database_url(database_url)
        if config:
            print("✅ DATABASE_URL에서 설정을 파싱했습니다.")
            return config
    
    # 2. 개별 환경 변수 사용 (fallback)
    config = {
        'host': os.getenv('POSTGRES_HOST', os.getenv('PGHOST')),
        'database': os.getenv('POSTGRES_DB', os.getenv('PGDATABASE')),
        'user': os.getenv('POSTGRES_USER', os.getenv('PGUSER')),
        'password': os.getenv('POSTGRES_PASSWORD', os.getenv('PGPASSWORD')),
        'port': os.getenv('POSTGRES_PORT', os.getenv('PGPORT', '5432'))
    }
    
    print("✅ 개별 환경 변수에서 설정을 구성했습니다.")
    return config

# PostgreSQL 설정 (Railway 환경 변수 사용)
POSTGRES_CONFIG = get_postgres_config()

def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")
        return None

def migrate_crawled_data(conn):
    """크롤링된 정책 데이터 마이그레이션"""
    try:
        cursor = conn.cursor()
        
        # 지역별 JSON 파일들
        json_files = [
            ('crawling/seoul.json', '서울특별시'),
            ('crawling/incheon.json', '인천광역시'),
            ('crawling/gyeonggi.json', '경기도')
        ]
        
        total_policies = 0
        
        for json_file, region_name in json_files:
            if not os.path.exists(json_file):
                print(f"⚠️ 파일 없음: {json_file}")
                continue
                
            print(f"📁 {region_name} 데이터 마이그레이션 중...")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                policies = json.load(f)
            
            # 지역 ID 조회
            cursor.execute("SELECT id FROM regions WHERE name = %s", (region_name,))
            region_result = cursor.fetchone()
            if not region_result:
                print(f"⚠️ 지역 정보 없음: {region_name}")
                continue
                
            region_id = region_result[0]
            
            # 카테고리 매핑 (기본값: 기타지원)
            cursor.execute("SELECT id FROM categories WHERE name = 'Other Support'")
            default_category_id = cursor.fetchone()[0]
            
            for policy in policies:
                try:
                    # 연령 범위 처리
                    age_min = min(policy.get('age_range', [0])) if policy.get('age_range') else None
                    age_max = max(policy.get('age_range', [100])) if policy.get('age_range') else None
                    
                    # 정책 삽입
                    cursor.execute('''
                        INSERT INTO policies (
                            title, description, url, region_id, category_id,
                            age_min, age_max, conditions, benefits, application_period,
                            status, priority, created_at, updated_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ''', (
                        policy.get('title', ''),
                        policy.get('description', ''),
                        policy.get('url', ''),
                        region_id,
                        default_category_id,
                        age_min,
                        age_max,
                        policy.get('conditions', ''),
                        policy.get('benefits', ''),
                        policy.get('application_period', ''),
                        'active',
                        0,
                        datetime.now(),
                        datetime.now()
                    ))
                    
                    total_policies += 1
                    
                except Exception as e:
                    print(f"⚠️ 정책 삽입 실패: {policy.get('title', 'Unknown')} - {e}")
                    continue
            
            print(f"✅ {region_name}: {len(policies)}개 정책 처리 완료")
        
        print(f"✅ 총 {total_policies}개 정책 마이그레이션 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 데이터 마이그레이션 실패: {e}")
        return False

def initialize_database():
    """데이터베이스 초기화 및 마이그레이션"""
    try:
        print("🔧 데이터베이스 초기화 시작...")
        print(f"📡 PostgreSQL 설정: {POSTGRES_CONFIG}")
        
        conn = get_db_connection()
        if not conn:
            print("❌ 데이터베이스 연결 실패")
            return False
        
        cursor = conn.cursor()
        
        # 테이블 존재 여부 확인
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'policies'
            );
        """)
        
        table_exists = cursor.fetchone()[0]
        
        if not table_exists:
            print("📊 테이블 생성 중...")
            # 스키마 파일 읽기
            with open('database_schema.sql', 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            cursor.execute(schema_sql)
            
            print("📊 기본 데이터 삽입 중...")
            # 기본 데이터 삽입
            with open('insert_data.sql', 'r', encoding='utf-8') as f:
                insert_sql = f.read()
            
            cursor.execute(insert_sql)
            
            print("📊 크롤링 데이터 마이그레이션 중...")
            # 크롤링 데이터 마이그레이션
            migrate_crawled_data(conn)
            
            conn.commit()
            print("✅ 데이터베이스 초기화 완료!")
        else:
            print("✅ 데이터베이스가 이미 초기화되어 있습니다.")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

if __name__ == '__main__':
    print("🚀 데이터베이스 초기화 스크립트 시작...")
    print(f"📁 현재 작업 디렉토리: {os.getcwd()}")
    print(f"📁 파일 목록: {os.listdir('.')}")
    
    success = initialize_database()
    if success:
        print("✅ 데이터베이스 초기화 성공!")
        sys.exit(0)
    else:
        print("❌ 데이터베이스 초기화 실패!")
        sys.exit(1)
