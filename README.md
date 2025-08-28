# 복지정책 챗봇 (Welfare Policy Chatbot)

## 📋 프로젝트 소개

복잡하고 방대한 복지정책 정보를 사용자가 쉽게 검색하고 활용할 수 있도록 하는 웹 기반 챗봇 서비스입니다. 전국 17개 시도의 청년 복지정책을 크롤링하여 데이터베이스화하고, 사용자 친화적인 인터페이스를 통해 정책 정보를 제공하는 시스템을 구축했습니다.

## 🚀 주요 기능

- **지능형 챗봇**: OpenAI GPT 기반 자연어 처리
- **정책 검색**: 지역, 연령, 키워드 기반 검색
- **실시간 응답**: 즉시 정책 정보 제공
- **모바일 최적화**: 반응형 웹 디자인
- **PostgreSQL**: 확장 가능한 데이터베이스 구조

## 🛠️ 기술 스택

### 백엔드
- **Python Flask**: API 서버
- **PostgreSQL**: 데이터베이스
- **OpenAI GPT**: 챗봇 AI
- **psycopg2**: PostgreSQL 드라이버

### 프론트엔드
- **React**: 사용자 인터페이스
- **CSS3**: 스타일링
- **Netlify**: 배포 플랫폼

## 📁 프로젝트 구조

```
20wf/
├── backend/                 # 백엔드 API 서버
│   ├── app_postgresql_api.py    # PostgreSQL API 서버
│   ├── database_schema.sql      # 데이터베이스 스키마
│   ├── migrate_to_postgresql.py # 데이터 마이그레이션
│   └── requirements.txt         # Python 의존성
├── front/                   # 프론트엔드 React 앱
│   └── yu_hackathon/
│       └── chatbot-ui/
├── crawling/                # 정책 데이터 크롤링
│   ├── crawling.py
│   └── *.json
└── docs/                    # 문서
    ├── 배포_가이드.md
    └── PostgreSQL_배포_가이드.md
```

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 저장소 클론
git clone https://github.com/kimdain0222/20wf.git
cd 20wf

# 백엔드 의존성 설치
cd backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

```bash
# backend/config.env 파일 생성
cp backend/env_example.txt backend/config.env

# 환경 변수 편집
# PostgreSQL 연결 정보와 OpenAI API 키 설정
```

### 3. 데이터베이스 설정

```bash
# PostgreSQL 데이터베이스 생성
# Railway, Supabase, 또는 로컬 PostgreSQL 사용

# 스키마 생성
python migrate_to_postgresql.py
```

### 4. 서버 실행

```bash
# 백엔드 서버 실행
cd backend
python app_postgresql_api.py

# 프론트엔드 실행
cd front/yu_hackathon/chatbot-ui
npm install
npm start
```

## 🌐 배포

### Railway 배포 (추천)

1. **Railway 계정 생성**: [Railway.app](https://railway.app)
2. **GitHub 연동**: 이 저장소 연결
3. **PostgreSQL 추가**: "Provision PostgreSQL"
4. **환경 변수 설정**: Railway 대시보드에서 설정
5. **자동 배포**: Git 푸시 시 자동 배포

### 환경 변수 설정

Railway에서 다음 환경 변수를 설정하세요:

```
POSTGRES_HOST=your_railway_host
POSTGRES_DB=railway
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_PORT=5432
OPENAI_API_KEY=your_openai_api_key
```

## 📊 데이터베이스 스키마

### 주요 테이블

- **policies**: 정책 정보
- **regions**: 지역 정보 (17개 시도)
- **categories**: 정책 카테고리
- **tags**: 정책 태그
- **users**: 사용자 정보 (향후 확장)

### 데이터 마이그레이션

```bash
# SQLite에서 PostgreSQL로 마이그레이션
python migrate_to_postgresql.py
```

## 🔧 API 엔드포인트

### 정책 관련
- `GET /api/policies` - 정책 목록 조회
- `GET /api/policies/<id>` - 정책 상세 조회
- `GET /api/policies/search` - 정책 검색

### 챗봇 관련
- `POST /api/chat` - 챗봇 대화
- `GET /api/chat/history` - 대화 히스토리

### 통계 관련
- `GET /api/stats` - 정책 통계
- `GET /api/regions` - 지역별 통계

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 GitHub Issues를 통해 연락해주세요.

---

**복지정책 챗봇** - 복지정책 정보의 접근성을 높이고, 사용자 맞춤형 서비스를 제공합니다.
