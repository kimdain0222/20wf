-- 복지정책 챗봇 PostgreSQL 스키마
-- 버전: 2.0 (앱 출시용)

-- 사용자 테이블 (향후 개인화 기능용)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 지역 테이블 (시도/시군구)
CREATE TABLE IF NOT EXISTS regions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,  -- 행정구역 코드
    name VARCHAR(50) NOT NULL,         -- 지역명
    parent_code VARCHAR(10),           -- 상위 지역 코드
    level INTEGER NOT NULL,            -- 1: 시도, 2: 시군구
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정책 카테고리 테이블
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7),  -- HEX 색상 코드
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정책 테이블 (메인)
CREATE TABLE IF NOT EXISTS policies (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    url TEXT,
    region_id INTEGER REFERENCES regions(id),
    category_id INTEGER REFERENCES categories(id),
    age_min INTEGER,
    age_max INTEGER,
    income_min INTEGER,  -- 소득 기준 (만원)
    income_max INTEGER,
    application_start DATE,
    application_end DATE,
    support_amount_min INTEGER,  -- 지원금액 (만원)
    support_amount_max INTEGER,
    conditions TEXT,
    benefits TEXT,
    application_method TEXT,
    required_documents TEXT,
    contact_info TEXT,
    status VARCHAR(20) DEFAULT 'active',  -- active, inactive, expired
    priority INTEGER DEFAULT 0,  -- 우선순위 (높을수록 우선)
    view_count INTEGER DEFAULT 0,  -- 조회수
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정책 태그 테이블
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정책-태그 연결 테이블
CREATE TABLE IF NOT EXISTS policy_tags (
    policy_id INTEGER REFERENCES policies(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (policy_id, tag_id)
);

-- 사용자 관심 정책 테이블
CREATE TABLE IF NOT EXISTS user_favorites (
    user_id VARCHAR(50) NOT NULL,
    policy_id INTEGER REFERENCES policies(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, policy_id)
);

-- 검색 히스토리 테이블
CREATE TABLE IF NOT EXISTS search_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50),
    query TEXT NOT NULL,
    filters JSONB,  -- 검색 필터 정보
    result_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정책 조회 로그 테이블
CREATE TABLE IF NOT EXISTS policy_views (
    id SERIAL PRIMARY KEY,
    policy_id INTEGER REFERENCES policies(id),
    user_id VARCHAR(50),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_policies_region ON policies(region_id);
CREATE INDEX IF NOT EXISTS idx_policies_category ON policies(category_id);
CREATE INDEX IF NOT EXISTS idx_policies_status ON policies(status);
CREATE INDEX IF NOT EXISTS idx_policies_age ON policies(age_min, age_max);
CREATE INDEX IF NOT EXISTS idx_policies_application_date ON policies(application_start, application_end);
CREATE INDEX IF NOT EXISTS idx_policies_title ON policies USING gin(to_tsvector('korean', title));
CREATE INDEX IF NOT EXISTS idx_policies_description ON policies USING gin(to_tsvector('korean', description));
CREATE INDEX IF NOT EXISTS idx_policies_conditions ON policies USING gin(to_tsvector('korean', conditions));
CREATE INDEX IF NOT EXISTS idx_policies_benefits ON policies USING gin(to_tsvector('korean', benefits));

-- 복합 인덱스
CREATE INDEX IF NOT EXISTS idx_policies_search ON policies(region_id, category_id, age_min, age_max, status);
CREATE INDEX IF NOT EXISTS idx_policies_popular ON policies(status, priority, view_count DESC);

-- 트리거 함수: updated_at 자동 업데이트
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_policies_updated_at BEFORE UPDATE ON policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 기본 데이터 삽입
INSERT INTO regions (code, name, level) VALUES
('11', '서울특별시', 1),
('26', '부산광역시', 1),
('27', '대구광역시', 1),
('28', '인천광역시', 1),
('29', '광주광역시', 1),
('30', '대전광역시', 1),
('31', '울산광역시', 1),
('36', '세종특별자치시', 1),
('41', '경기도', 1),
('42', '강원도', 1),
('43', '충청북도', 1),
('44', '충청남도', 1),
('45', '전라북도', 1),
('46', '전라남도', 1),
('47', '경상북도', 1),
('48', '경상남도', 1),
('50', '제주특별자치도', 1)
ON CONFLICT (code) DO NOTHING;

INSERT INTO categories (name, description, icon, color) VALUES
('주거지원', '주택, 월세, 전세 관련 지원', 'home', '#4CAF50'),
('취업지원', '창업, 취업, 교육 관련 지원', 'work', '#2196F3'),
('문화생활', '문화, 여가, 체육 관련 지원', 'culture', '#FF9800'),
('교통지원', '교통비, 대중교통 관련 지원', 'transport', '#9C27B0'),
('저축지원', '적금, 저축 관련 지원', 'savings', '#607D8B'),
('의료지원', '의료, 건강 관련 지원', 'health', '#F44336'),
('교육지원', '학자금, 장학금 관련 지원', 'education', '#795548'),
('기타지원', '기타 복지 관련 지원', 'other', '#9E9E9E')
ON CONFLICT (name) DO NOTHING;

-- 뷰 생성: 정책 검색용
CREATE OR REPLACE VIEW policy_search_view AS
SELECT 
    p.id,
    p.title,
    p.description,
    p.url,
    r.name as region_name,
    c.name as category_name,
    c.color as category_color,
    p.age_min,
    p.age_max,
    p.income_min,
    p.income_max,
    p.application_start,
    p.application_end,
    p.support_amount_min,
    p.support_amount_max,
    p.conditions,
    p.benefits,
    p.application_method,
    p.required_documents,
    p.contact_info,
    p.status,
    p.priority,
    p.view_count,
    p.created_at,
    p.updated_at,
    array_agg(t.name) as tags
FROM policies p
LEFT JOIN regions r ON p.region_id = r.id
LEFT JOIN categories c ON p.category_id = c.id
LEFT JOIN policy_tags pt ON p.id = pt.policy_id
LEFT JOIN tags t ON pt.tag_id = t.id
GROUP BY p.id, r.name, c.name, c.color;

-- 통계 뷰 생성
CREATE OR REPLACE VIEW policy_stats AS
SELECT 
    r.name as region_name,
    c.name as category_name,
    COUNT(*) as policy_count,
    AVG(p.view_count) as avg_views,
    SUM(p.view_count) as total_views
FROM policies p
LEFT JOIN regions r ON p.region_id = r.id
LEFT JOIN categories c ON p.category_id = c.id
WHERE p.status = 'active'
GROUP BY r.name, c.name;
