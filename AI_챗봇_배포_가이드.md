# AI 챗봇 기능 강화 배포 가이드

## 🚀 개요

복지정책 챗봇에 OpenAI GPT API를 연동하여 지능적인 대화 기능을 추가했습니다.

## 📋 사전 준비사항

### 1. OpenAI API 키 발급
1. [OpenAI 웹사이트](https://platform.openai.com/)에 가입
2. API 키 발급 (Settings > API Keys)
3. 충분한 크레딧 확인 (GPT-3.5-turbo 사용)

### 2. 환경 변수 설정

#### 로컬 개발 환경
```bash
# backend/.env 파일 생성
OPENAI_API_KEY=sk-your-openai-api-key-here
DATABASE_URL=welfare_policies.db
FLASK_ENV=development
FLASK_DEBUG=True
```

#### Railway 배포 환경
1. Railway 대시보드 접속
2. 프로젝트 선택
3. Variables 탭에서 환경 변수 추가:
   - `OPENAI_API_KEY`: sk-your-openai-api-key-here
   - `FLASK_ENV`: production
   - `FLASK_DEBUG`: False

## 🔧 설치 및 실행

### 1. 패키지 설치
```bash
cd backend
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
python app_flask_api_server.py
```

### 3. 테스트 실행
```bash
python test_ai_chat.py
```

## 🌐 프론트엔드 연동

### 1. 백엔드 URL 업데이트
`front/yu_hackathon/chatbot-ui/src/App.js`에서:
```javascript
// 실제 Railway 배포 URL로 변경
const response = await fetch('https://your-actual-railway-url.railway.app/api/chat', {
```

### 2. 프론트엔드 배포
```bash
cd front/yu_hackathon/chatbot-ui
npm run build
```

## 🧪 테스트 시나리오

### 기본 테스트
1. "안녕하세요" - 인사 응답 확인
2. "서울 청년 정책" - 지역별 정책 추천
3. "25살 주택 지원" - 연령별 맞춤 추천
4. "창업 지원" - 카테고리별 정책 검색

### 고급 테스트
1. 복합 조건 질문: "서울에 사는 30대인데 창업하고 싶어요"
2. 구체적 질문: "월세 지원 정책 신청 방법이 궁금해요"
3. 비교 질문: "서울과 경기도 청년 정책 차이점이 뭔가요?"

## 📊 성능 모니터링

### API 응답 시간
- 목표: 3초 이내
- 모니터링: Railway 로그 확인

### 토큰 사용량
- GPT-3.5-turbo: 약 $0.002/1K 토큰
- 예상 월 비용: $10-50 (사용량에 따라)

### 오류 처리
- API 키 만료 시 fallback 응답
- 네트워크 오류 시 기존 키워드 매칭 사용

## 🔒 보안 고려사항

### API 키 보안
- 환경 변수로 관리
- Git에 절대 커밋하지 않음
- 정기적 키 로테이션

### 사용자 데이터
- 개인정보 수집하지 않음
- 대화 내용 로그 저장하지 않음
- GDPR 준수

## 🚨 문제 해결

### 일반적인 오류

#### 1. API 키 오류
```
Error: Invalid API key
```
**해결**: OpenAI API 키 재확인 및 환경 변수 설정

#### 2. CORS 오류
```
Access to fetch at '...' from origin '...' has been blocked by CORS policy
```
**해결**: 백엔드 CORS 설정 확인

#### 3. 타임아웃 오류
```
Request timeout
```
**해결**: 네트워크 연결 확인 및 API 응답 시간 모니터링

### 로그 확인
```bash
# Railway 로그 확인
railway logs

# 로컬 로그 확인
python app_flask_api_server.py
```

## 📈 향후 개선 계획

### 1. 성능 최적화
- 응답 캐싱 구현
- 프롬프트 최적화
- 토큰 사용량 최적화

### 2. 기능 확장
- 대화 컨텍스트 유지
- 정책 신청 가이드
- 개인화 추천

### 3. 모니터링 강화
- 사용자 행동 분석
- 정책 인기도 추적
- A/B 테스트

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. 환경 변수 설정
2. API 키 유효성
3. 네트워크 연결
4. 서버 로그

---

**배포 완료 후**: https://your-frontend-url.netlify.app 에서 AI 챗봇 기능을 테스트해보세요!
