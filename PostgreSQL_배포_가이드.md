# PostgreSQL 데이터베이스 배포 가이드

## 🚀 Railway에서 PostgreSQL 설정하기

### 1단계: Railway에서 PostgreSQL 데이터베이스 생성

1. **Railway 대시보드 접속**: https://railway.app/dashboard
2. **프로젝트 선택**: `20wf` 프로젝트
3. **"New" 버튼 클릭** → **"Database" 선택**
4. **"PostgreSQL" 선택**
5. **데이터베이스 생성 완료**

### 2단계: 환경 변수 확인

PostgreSQL이 생성되면 Railway에서 자동으로 다음 환경 변수들이 설정됩니다:

```bash
PGHOST=containers-us-west-XX.railway.app
PGDATABASE=railway
PGUSER=postgres
PGPASSWORD=your_password_here
PGPORT=5432
```

### 3단계: 데이터베이스 마이그레이션 실행

#### 로컬에서 마이그레이션 실행 (권장)

1. **환경 변수 설정**:
   ```bash
   cd backend
   # Railway에서 받은 PostgreSQL 연결 정보로 config.env 업데이트
   ```

2. **마이그레이션 실행**:
   ```bash
   python migrate_to_postgresql.py
   ```

#### Railway에서 직접 마이그레이션 실행

1. **Railway 대시보드** → **프로젝트** → **"Deployments" 탭**
2. **"Deploy" 버튼 클릭**
3. **배포 완료 후 마이그레이션 실행**:
   ```bash
   # Railway CLI 사용
   railway run python migrate_to_postgresql.py
   ```

### 4단계: 마이그레이션 결과 확인

마이그레이션이 완료되면 다음 정보가 출력됩니다:

```
📊 마이그레이션 결과:
   - 활성 정책: XXX개
   - 지역: 17개
   - 카테고리: 8개

📍 지역별 정책 분포:
   - 서울특별시: XXX개
   - 인천광역시: XXX개
   - 경기도: XXX개
```

### 5단계: API 서버 재시작

1. **Railway 대시보드** → **프로젝트**
2. **"Deployments" 탭** → **"Deploy" 버튼 클릭**
3. **배포 완료 대기**

### 6단계: 연결 확인

배포 완료 후 다음 URL로 연결을 확인합니다:

```
https://20wf-production.up.railway.app/api/health
```

예상 응답:
```json
{
  "status": "healthy",
  "message": "API 서버와 PostgreSQL이 정상 작동 중입니다!",
  "database": "PostgreSQL"
}
```

## 🔧 문제 해결

### 데이터베이스 연결 실패

1. **환경 변수 확인**:
   - Railway 대시보드에서 PostgreSQL 환경 변수 확인
   - `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGPORT` 설정 확인

2. **네트워크 연결 확인**:
   - Railway PostgreSQL이 외부 접근 허용되어 있는지 확인
   - 방화벽 설정 확인

### 마이그레이션 실패

1. **로그 확인**:
   ```bash
   railway logs
   ```

2. **수동 마이그레이션**:
   ```bash
   railway run python migrate_to_postgresql.py
   ```

3. **데이터베이스 초기화**:
   - Railway PostgreSQL에서 모든 테이블 삭제 후 재실행

### API 서버 오류

1. **의존성 확인**:
   ```bash
   pip install -r requirements_postgresql.txt
   ```

2. **환경 변수 확인**:
   - `FLASK_ENV=production`
   - `FLASK_DEBUG=False`

## 📊 데이터베이스 구조

### 주요 테이블

- **policies**: 정책 정보 (메인 테이블)
- **regions**: 지역 정보 (시도/시군구)
- **categories**: 정책 카테고리
- **tags**: 정책 태그
- **policy_tags**: 정책-태그 연결
- **user_favorites**: 사용자 관심 정책
- **search_history**: 검색 히스토리
- **policy_views**: 정책 조회 로그

### 인덱스

- **텍스트 검색**: 한국어 전문 검색 인덱스
- **복합 검색**: 지역, 카테고리, 연령, 상태
- **인기도**: 우선순위, 조회수 기반 정렬

## 🔄 데이터 업데이트

### 새로운 정책 추가

1. **JSON 파일 업데이트**: `crawling/` 폴더의 지역별 JSON 파일
2. **마이그레이션 재실행**: `python migrate_to_postgresql.py`

### 카테고리 수정

1. **데이터베이스 직접 수정**:
   ```sql
   UPDATE categories SET name = '새카테고리명' WHERE id = 1;
   ```

2. **API 재시작**: Railway에서 재배포

## 📈 모니터링

### 데이터베이스 상태 확인

```bash
# 연결 상태
curl https://20wf-production.up.railway.app/api/health

# 정책 통계
curl https://20wf-production.up.railway.app/api/stats

# 지역별 정책
curl https://20wf-production.up.railway.app/api/policies/region/서울특별시
```

### 로그 모니터링

```bash
# Railway 로그 확인
railway logs

# 실시간 로그
railway logs --follow
```

## 🎯 다음 단계

1. ✅ **PostgreSQL 데이터베이스 연결**
2. ✅ **정책 데이터 마이그레이션**
3. 🔄 **AI 챗봇 기능 활성화**
4. 🔄 **OpenAI API 키 설정**
5. 🔄 **프론트엔드 연결 테스트**

---

**마이그레이션이 완료되면 AI 챗봇 기능을 활성화할 수 있습니다!**
