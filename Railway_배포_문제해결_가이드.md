# Railway PostgreSQL 연결 문제 해결 가이드

## 🚨 현재 상황
- ✅ PostgreSQL 연결 성공
- ✅ Flask 2.3+ 호환성 문제 해결
- ✅ 환경 변수 설정 완료
- ❌ 서버 시작 시 오류 발생

## 🔧 해결된 문제들

### 1. Flask 2.3+ 호환성 문제
- `before_first_request` 데코레이터 제거
- 앱 팩토리 패턴에서 직접 앱 생성으로 변경

### 2. PostgreSQL 텍스트 검색 설정
- `korean`에서 `simple`로 변경하여 호환성 문제 해결

### 3. 데이터베이스 자동 초기화
- Flask 앱 시작 시 자동으로 데이터베이스 초기화 실행
- 테이블 생성 및 기본 데이터 삽입 자동화

## 📋 최신 수정사항

### 1. app_postgresql_api.py 개선
```python
# 앱 시작 시 데이터베이스 초기화 추가
print("🚀 Flask 앱 시작 중...")
print("🔧 데이터베이스 자동 초기화 실행...")
initialize_database()
```

### 2. start_railway.py 개선
- 환경 변수 검증 강화
- 패키지 의존성 확인 추가
- 더 안정적인 서버 시작 로직

### 3. 오류 처리 강화
- SQL 문장별 개별 실행으로 오류 격리
- 상세한 로깅 및 오류 추적
- 파일 존재 여부 확인

## 🚀 배포 단계

### 1단계: 로컬 테스트
```bash
cd backend
python test_deployment.py
```

### 2단계: Railway 환경 변수 확인
- `DATABASE_URL`: PostgreSQL 연결 문자열
- `OPENAI_API_KEY`: OpenAI API 키 (선택사항)

### 3단계: 배포 실행
```bash
# Railway CLI 사용
railway up

# 또는 GitHub 연동으로 자동 배포
```

## 🔍 문제 진단

### 서버 시작 오류 확인
1. Railway 대시보드에서 로그 확인
2. 환경 변수 설정 상태 확인
3. 데이터베이스 연결 상태 확인

### 일반적인 오류 해결

#### 1. 모듈 임포트 오류
```bash
# requirements.txt 확인
pip install -r requirements_postgresql.txt
```

#### 2. 데이터베이스 연결 오류
- `DATABASE_URL` 형식 확인
- PostgreSQL 서비스 상태 확인

#### 3. 파일 경로 오류
- `database_schema.sql` 파일 존재 확인
- `insert_data.sql` 파일 존재 확인

## 📊 모니터링

### 헬스체크 엔드포인트
```
GET /api/health
```

### 데이터베이스 상태 확인
```python
# 로그에서 확인
"✅ 데이터베이스 초기화 완료!"
"✅ PostgreSQL 연결 성공!"
```

## 🎯 성공 지표

1. ✅ 서버 시작 성공
2. ✅ 데이터베이스 연결 성공
3. ✅ 테이블 생성 완료
4. ✅ 기본 데이터 삽입 완료
5. ✅ API 엔드포인트 정상 응답

## 📞 추가 지원

문제가 지속되는 경우:
1. Railway 로그 전체 확인
2. 환경 변수 재설정
3. 데이터베이스 서비스 재시작
4. 프로젝트 재배포

---

**마지막 업데이트**: 2024년 12월
**버전**: 2.0 (PostgreSQL 호환)
