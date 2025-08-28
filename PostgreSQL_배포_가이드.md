# PostgreSQL 데이터베이스 확장 배포 가이드

## 🚀 개요

복지정책 챗봇을 앱 출시 수준으로 확장하기 위해 SQLite에서 PostgreSQL로 마이그레이션합니다.

## 📊 **PostgreSQL 선택 이유**

### **SQLite vs PostgreSQL 비교**

| 항목 | SQLite | PostgreSQL |
|------|--------|------------|
| **용량** | 단일 파일 (GB 단위) | 대용량 데이터 (TB 단위) |
| **동시 접속** | 단일 사용자 | 다중 사용자 (수천 명) |
| **검색 성능** | 기본 인덱스 | Full-text search, 복합 인덱스 |
| **확장성** | 제한적 | 무제한 |
| **클라우드 호스팅** | 제한적 | Railway, Heroku, AWS RDS |
| **비용** | 무료 | 무료 티어 ~ 월 $5-50 |

### **예상 데이터 규모**
- **현재**: 48개 정책 (3개 지역)
- **목표**: 5,000개 정책 (전국 17개 시도 + 시군구)
- **사용자**: 월 10만명 이상
- **검색**: 초당 100회 이상

## 🗄️ **PostgreSQL 호스팅 옵션**

### **1. Railway (추천)**
```bash
# 무료 티어: 월 500시간, 1GB 저장공간
# 유료: 월 $5부터
```

### **2. Supabase**
```bash
# 무료 티어: 월 500MB, 2개 프로젝트
# 유료: 월 $25부터
```

### **3. Neon**
```bash
# 무료 티어: 월 3GB, 무제한 프로젝트
# 유료: 월 $0.12/GB
```

### **4. AWS RDS**
```bash
# 무료 티어: 월 750시간
# 유료: 월 $15-50
```

## 🔧 **설치 및 설정**

### **1. PostgreSQL 설치 (로컬 개발용)**

#### Windows
```bash
# PostgreSQL 공식 사이트에서 다운로드
# https://www.postgresql.org/download/windows/
```

#### macOS
```bash
brew install postgresql
brew services start postgresql
```

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### **2. 데이터베이스 생성**
```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 생성
CREATE DATABASE welfare_chatbot;

# 사용자 생성 (선택사항)
CREATE USER welfare_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE welfare_chatbot TO welfare_user;

# 종료
\q
```

### **3. 환경 변수 설정**

#### 로컬 개발 환경
```bash
# backend/.env 파일
POSTGRES_HOST=localhost
POSTGRES_DB=welfare_chatbot
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_PORT=5432
OPENAI_API_KEY=sk-your-openai-api-key-here
```

#### Railway 배포 환경
1. Railway 대시보드 접속
2. 프로젝트 선택
3. Variables 탭에서 환경 변수 추가:
   ```
   POSTGRES_HOST=your-railway-postgres-host
   POSTGRES_DB=railway
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=your-railway-password
   POSTGRES_PORT=5432
   OPENAI_API_KEY=sk-your-openai-api-key-here
   ```

## 🚀 **마이그레이션 실행**

### **1. 패키지 설치**
```bash
cd backend
pip install -r requirements_postgresql.txt
```

### **2. 스키마 생성**
```bash
# PostgreSQL에 스키마 적용
psql -h localhost -U postgres -d welfare_chatbot -f database_schema.sql
```

### **3. 데이터 마이그레이션**
```bash
# SQLite → PostgreSQL 마이그레이션 실행
python migrate_to_postgresql.py
```

### **4. 마이그레이션 검증**
```bash
# PostgreSQL 데이터 확인
psql -h localhost -U postgres -d welfare_chatbot -c "SELECT COUNT(*) FROM policies;"
psql -h localhost -U postgres -d welfare_chatbot -c "SELECT region_name, COUNT(*) FROM policy_search_view GROUP BY region_name;"
```

## 🌐 **새로운 API 서버 실행**

### **1. PostgreSQL API 서버 시작**
```bash
cd backend
python app_postgresql_api.py
```

### **2. API 테스트**
```bash
# 서버 상태 확인
curl http://localhost:5000/api/health

# 정책 목록 조회
curl http://localhost:5000/api/policies

# 지역별 정책 조회
curl http://localhost:5000/api/policies/region/서울특별시

# 통계 정보 조회
curl http://localhost:5000/api/stats
```

## 📈 **새로운 기능들**

### **1. 고급 검색**
```bash
# 키워드 검색
GET /api/policies?keyword=주택

# 복합 필터링
GET /api/policies?region=서울특별시&category=주거지원&age=25

# 페이징
GET /api/policies?limit=10&offset=20
```

### **2. 정책 상세 정보**
```bash
# 정책 상세 조회 (조회수 자동 증가)
GET /api/policies/1
```

### **3. 카테고리 및 지역 관리**
```bash
# 카테고리 목록
GET /api/categories

# 지역 목록
GET /api/regions
```

### **4. 통계 정보**
```bash
# 전체 통계
GET /api/stats
```

## 🔍 **성능 최적화**

### **1. 인덱스 최적화**
```sql
-- Full-text search 인덱스
CREATE INDEX idx_policies_title_fts ON policies USING gin(to_tsvector('korean', title));
CREATE INDEX idx_policies_description_fts ON policies USING gin(to_tsvector('korean', description));

-- 복합 인덱스
CREATE INDEX idx_policies_search ON policies(region_id, category_id, age_min, age_max, status);
CREATE INDEX idx_policies_popular ON policies(status, priority, view_count DESC);
```

### **2. 쿼리 최적화**
```sql
-- 뷰 생성으로 복잡한 조인 최적화
CREATE VIEW policy_search_view AS
SELECT p.*, r.name as region_name, c.name as category_name
FROM policies p
LEFT JOIN regions r ON p.region_id = r.id
LEFT JOIN categories c ON p.category_id = c.id;
```

### **3. 연결 풀링**
```python
# psycopg2 연결 풀 설정
import psycopg2.pool

connection_pool = psycopg2.pool.SimpleConnectionPool(
    1, 20,  # 최소, 최대 연결 수
    host=POSTGRES_CONFIG['host'],
    database=POSTGRES_CONFIG['database'],
    user=POSTGRES_CONFIG['user'],
    password=POSTGRES_CONFIG['password']
)
```

## 📊 **모니터링 및 관리**

### **1. 데이터베이스 성능 모니터링**
```sql
-- 느린 쿼리 확인
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- 테이블 크기 확인
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'policies';
```

### **2. 백업 및 복구**
```bash
# 데이터베이스 백업
pg_dump -h localhost -U postgres welfare_chatbot > backup.sql

# 데이터베이스 복구
psql -h localhost -U postgres welfare_chatbot < backup.sql
```

### **3. 로그 모니터링**
```bash
# PostgreSQL 로그 확인
tail -f /var/log/postgresql/postgresql-*.log

# Railway 로그 확인
railway logs
```

## 🚨 **문제 해결**

### **1. 연결 오류**
```
Error: connection to server at "localhost" (127.0.0.1), port 5432 failed
```
**해결**: PostgreSQL 서비스 시작 확인

### **2. 인증 오류**
```
Error: authentication failed for user "postgres"
```
**해결**: 비밀번호 확인 및 pg_hba.conf 설정

### **3. 권한 오류**
```
Error: permission denied for table policies
```
**해결**: 사용자 권한 부여

### **4. 메모리 부족**
```
Error: out of memory
```
**해결**: PostgreSQL 메모리 설정 조정

## 📈 **확장 계획**

### **1. 데이터 확장**
- **전국 정책 수집**: 17개 시도 + 시군구 단위
- **정책 카테고리 확장**: 의료, 교육, 문화 등
- **실시간 업데이트**: 정책 변경사항 자동 반영

### **2. 기능 확장**
- **사용자 프로필**: 개인화된 정책 추천
- **북마크 기능**: 관심 정책 저장
- **알림 서비스**: 마감일 알림, 새 정책 알림
- **통계 대시보드**: 관리자용 분석 도구

### **3. 성능 확장**
- **캐싱 시스템**: Redis 연동
- **CDN**: 정적 파일 최적화
- **로드 밸런싱**: 다중 서버 구성

## 💰 **비용 예상**

### **Railway 기준**
- **무료 티어**: 월 $0 (500시간, 1GB)
- **기본 플랜**: 월 $5 (무제한 시간, 1GB)
- **표준 플랜**: 월 $20 (무제한 시간, 10GB)

### **예상 사용량**
- **데이터베이스**: 100MB (5,000개 정책)
- **트래픽**: 월 10만 요청
- **저장공간**: 1GB 이내

## 🎯 **성공 지표**

### **기술적 지표**
- **응답 시간**: 평균 200ms 이하
- **동시 접속**: 100명 이상 지원
- **가용성**: 99.9% 이상
- **데이터 정확성**: 100%

### **비즈니스 지표**
- **정책 매칭 성공률**: 95% 이상
- **사용자 만족도**: 4.5/5.0 이상
- **정책 활용률**: 30% 이상
- **사용자 유지율**: 60% 이상

---

**PostgreSQL 마이그레이션 완료 후**: 앱 출시 준비가 완료됩니다! 🚀
