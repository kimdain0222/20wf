-- 복지정책 챗봇 PostgreSQL 스키마 (UTF-8)
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
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    parent_code VARCHAR(10),
    level INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 정책 카테고리 테이블
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(50),
    color VARCHAR(7),
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
    income_min INTEGER,
    income_max INTEGER,
    application_start DATE,
    application_end DATE,
    support_amount_min INTEGER,
    support_amount_max INTEGER,
    conditions TEXT,
    benefits TEXT,
    application_method TEXT,
    required_documents TEXT,
    contact_info TEXT,
    status VARCHAR(20) DEFAULT 'active',
    priority INTEGER DEFAULT 0,
    view_count INTEGER DEFAULT 0,
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
    filters JSONB,
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
