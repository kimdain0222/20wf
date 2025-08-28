# 복지정책 API 사용 가이드

## 개요
크롤링한 복지정책 데이터를 프론트엔드에서 사용할 수 있도록 제공하는 API 서버입니다.

##  데이터베이스 정보
- **파일 위치**: `C:\B조\db(PM.VER)\welfare_policies.db`
- **총 정책 수**: 49개
- **지역별 분포**: 
  - 경기도: 20개
  - 인천: 17개  
  - 서울: 11개

##  API 서버 실행 방법

### 1단계: 백엔드 폴더로 이동
```bash
cd "C:\B조\backend"
```

### 2단계: 필요한 패키지 설치
```bash
pip install -r requirements.txt
```

### 3단계: 서버 실행
```bash
python app.py
```

### 4단계: 서버 확인
브라우저에서 `http://localhost:5000/api/health` 접속

## 📡 API 엔드포인트

### 1. 서버 상태 확인
```
GET /api/health
```
**응답 예시:**
```json
{
  "status": "healthy",
  "message": "API 서버가 정상 작동 중입니다!"
}
```

### 2. 모든 정책 조회
```
GET /api/policies
```
**응답 예시:**
```json
{
  "success": true,
  "count": 49,
  "policies": [
    {
      "id": 1,
      "title": "청년농업인 경쟁력 제고사업",
      "url": "https://...",
      "region": "gyeonggi",
      "age_range": [20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
      "application_period": "2025.01.01 ~ 2025.12.31",
      "conditions": "청년농업인 및 청년4-H회원...",
      "benefits": "청년농업인 영농정착 생산 및 가공 시설..."
    }
  ]
}
```

### 3. 지역별 정책 조회
```
GET /api/policies/region/{region}
```
**예시:**
- `GET /api/policies/region/gyeonggi` (경기도)
- `GET /api/policies/region/incheon` (인천)
- `GET /api/policies/region/seoul` (서울)

### 4. 정책 검색 (키워드, 지역, 나이)
```
GET /api/policies/search?keyword={keyword}&region={region}&age={age}
```
**파라미터:**
- `keyword`: 검색할 키워드 (선택)
- `region`: 지역 필터 (선택)
- `age`: 나이 필터 (선택)

**예시:**
- `GET /api/policies/search?keyword=월세` (월세 관련 정책)
- `GET /api/policies/search?region=gyeonggi&age=20` (경기도 20대 정책)
- `GET /api/policies/search?keyword=청년&region=seoul` (서울 청년 정책)

### 5. 사용 가능한 지역 목록
```
GET /api/regions
```
**응답 예시:**
```json
{
  "success": true,
  "regions": ["gyeonggi", "incheon", "seoul"]
}
```

### 6. 데이터베이스 통계
```
GET /api/stats
```
**응답 예시:**
```json
{
  "success": true,
  "total_policies": 49,
  "region_stats": [
    {"region": "gyeonggi", "count": 20},
    {"region": "incheon", "count": 17},
    {"region": "seoul", "count": 11}
  ]
}
```

##  React에서 API 호출 예시

### 기본 fetch 사용
```javascript
// 모든 정책 가져오기
const fetchPolicies = async () => {
  try {
    const response = await fetch('http://localhost:5000/api/policies');
    const data = await response.json();
    
    if (data.success) {
      console.log('정책 수:', data.count);
      console.log('정책 목록:', data.policies);
    }
  } catch (error) {
    console.error('API 호출 실패:', error);
  }
};

// 지역별 정책 검색
const fetchPoliciesByRegion = async (region) => {
  try {
    const response = await fetch(`http://localhost:5000/api/policies/region/${region}`);
    const data = await response.json();
    
    if (data.success) {
      return data.policies;
    }
  } catch (error) {
    console.error('API 호출 실패:', error);
  }
};

// 키워드 검색
const searchPolicies = async (keyword, region, age) => {
  try {
    const params = new URLSearchParams();
    if (keyword) params.append('keyword', keyword);
    if (region) params.append('region', region);
    if (age) params.append('age', age);
    
    const response = await fetch(`http://localhost:5000/api/policies/search?${params}`);
    const data = await response.json();
    
    if (data.success) {
      return data.policies;
    }
  } catch (error) {
    console.error('API 호출 실패:', error);
  }
};
```

### axios 사용 (선택사항)
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

// 모든 정책 가져오기
const getPolicies = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/policies`);
    return response.data.policies;
  } catch (error) {
    console.error('API 호출 실패:', error);
  }
};
```

## 정책 데이터 구조

각 정책 객체는 다음 필드를 포함합니다:

```javascript
{
  id: 1,                    // 고유 ID
  title: "정책 제목",        // 정책명
  url: "https://...",       // 정책 상세 페이지 URL
  region: "gyeonggi",       // 지역 (gyeonggi, incheon, seoul)
  age_range: [20,21,22,23,24,25,26,27,28,29], // 대상 연령대
  application_period: "2025.01.01 ~ 2025.12.31", // 신청 기간
  conditions: "지원 조건...", // 지원 조건
  benefits: "지원 내용..."   // 지원 혜택
}
```

## ⚠️ 주의사항

1. **CORS 설정**: API 서버에 CORS가 설정되어 있어 React에서 호출 가능
2. **서버 실행**: 프론트엔드에서 API를 사용하려면 백엔드 서버가 실행 중이어야 함
3. **포트 충돌**: 5000번 포트가 사용 중이면 다른 포트로 변경 필요
4. **에러 처리**: API 호출 시 항상 try-catch로 에러 처리 권장

## 추천 사용 시나리오

1. **지역 선택 후**: `/api/policies/region/{region}` 호출
2. **키워드 검색**: `/api/policies/search?keyword={keyword}` 호출
3. **나이별 필터링**: `/api/policies/search?age={age}` 호출
4. **복합 검색**: `/api/policies/search?region={region}&age={age}` 호출

## 문의사항
API 사용 중 문제가 발생하면 백엔드 담당자(pm)에게 문의하세요! 