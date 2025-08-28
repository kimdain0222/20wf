-- 기본 데이터 삽입

-- 지역 데이터 삽입
INSERT INTO regions (code, name, level) VALUES
('11', 'Seoul', 1),
('26', 'Busan', 1),
('27', 'Daegu', 1),
('28', 'Incheon', 1),
('29', 'Gwangju', 1),
('30', 'Daejeon', 1),
('31', 'Ulsan', 1),
('36', 'Sejong', 1),
('41', 'Gyeonggi', 1),
('42', 'Gangwon', 1),
('43', 'Chungbuk', 1),
('44', 'Chungnam', 1),
('45', 'Jeonbuk', 1),
('46', 'Jeonnam', 1),
('47', 'Gyeongbuk', 1),
('48', 'Gyeongnam', 1),
('50', 'Jeju', 1)
ON CONFLICT (code) DO NOTHING;

-- 카테고리 데이터 삽입
INSERT INTO categories (name, description, icon, color) VALUES
('Housing Support', 'Housing, rent, lease related support', 'home', '#4CAF50'),
('Employment Support', 'Startup, employment, education related support', 'work', '#2196F3'),
('Cultural Life', 'Culture, leisure, sports related support', 'culture', '#FF9800'),
('Transport Support', 'Transportation, public transport related support', 'transport', '#9C27B0'),
('Savings Support', 'Savings, deposit related support', 'savings', '#607D8B'),
('Medical Support', 'Medical, health related support', 'health', '#F44336'),
('Education Support', 'Scholarship, tuition related support', 'education', '#795548'),
('Other Support', 'Other welfare related support', 'other', '#9E9E9E')
ON CONFLICT (name) DO NOTHING;
