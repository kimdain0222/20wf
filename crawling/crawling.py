import requests
from bs4 import BeautifulSoup
import re
import json
import os

print("현재 작업 디렉토리:", os.getcwd())

# 크롤링할 정책 URL들
urls = [
    "https://wis.seoul.go.kr/wfs/ywf/sickMan.do",
    "https://wis.seoul.go.kr/wfs/ywf/selfReliance.do",
     "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=379&pgno=1",
    "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=346&menudiv=financial",
    "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=304&menudiv=financial",
    "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=23&menudiv=financial",
    "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=277&empmst=006003",
    "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=253&empmst=006003",
    "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=252&empmst=006003",
    "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoDetail.do?poly_seq=251&empmst=006003"
]

all_results = []

for url in urls:
    res = requests.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, 'html.parser')

    result = {}
    result['url'] = url

    # 제목 추출
    title_tag = soup.select_one('.title-area h2') or soup.select_one('.b-title-box span') or soup.title
    result['title'] = title_tag.get_text(strip=True) if title_tag else '제목 없음'

    # 내용 영역 찾기 (class 여러 개 시도)
    content_box = (
        soup.select_one('.txt-tp1') or 
        soup.select_one('#detail_con .line-box') or 
        soup.select_one('.box-gray') or 
        soup.select_one('.con-box')
    )

    if content_box is None:
        print(f"Warning: 내용 영역을 찾을 수 없습니다: {url}")
        continue

    content_text = content_box.get_text(separator=" ", strip=True)

    # 지역 추출
    regions = []
    for r in ['경기도', '경기', '서울', '인천']:
        if r in content_text:
            regions.append(r.replace('도', ''))
    result['region'] = list(set(regions)) if regions else []

    # 나이 추출
    age_range = re.findall(r'(\d{1,2})\s*세\s*[~\-]\s*(\d{1,2})\s*세', content_text)
    under = re.findall(r'만\s*(\d{1,2})\s*세\s*이하', content_text)
    if age_range:
        result['age_range'] = [int(age_range[0][0]), int(age_range[0][1])]
    elif under:
        result['age_range'] = [0, int(under[0])]
    elif '청년' in content_text or '대학생' in content_text:
        result['age_range'] = [20, 29]
    else:
        result['age_range'] = []

    # 신청기간 추출
    application_period = ""
    for keyword in ['신청기간', '접수기간']:
        pattern = rf"{keyword}[^\d]*(\d{{4}}[.\-]\d{{2}}[.\-]\d{{2}})\s*[~\-]\s*(\d{{4}}[.\-]\d{{2}}[.\-]\d{{2}})"
        match = re.search(pattern, content_text)
        if match:
            application_period = f"{match.group(1)}~{match.group(2)}"
            break
    result['application_period'] = application_period or '미정'

    # 조건 / 혜택 추출 (h3, h4, ul 구조 기반)
    result['conditions'] = ""
    result['benefits'] = ""

    elements = content_box.find_all(['h3', 'h4', 'ul'])
    current_section = None

    for el in elements:
        if el.name in ['h3', 'h4']:
            current_section = el.get_text(strip=True)
        elif el.name == 'ul' and el.get('class') == ['ls-st1'] and current_section:
            text = el.get_text(separator=' ', strip=True)
            if any(kw in current_section for kw in ['지원대상', '사업대상', '신청자격', '지원자격']):
                result['conditions'] += text + " "
            elif any(kw in current_section for kw in ['사업내용', '지원내용', '혜택']):
                result['benefits'] += text + " "

    result['conditions'] = result['conditions'].strip()
    result['benefits'] = result['benefits'].strip()

    # 결과 출력
    print(f"✅ title: {result['title']}")
    print(f"🔗 url: {result['url']}")
    print(f"📍 region: {', '.join(result['region']) if result['region'] else 'None'}")
    print(f"🎂 age_range: {result['age_range'] if result['age_range'] else 'None'}")
    print(f"🗓️ application_period: {result['application_period']}")
    print(f"📌 conditions: {result['conditions'] or '없음'}")
    print(f"🎁 benefits: {result['benefits'] or '없음'}")
    print("-" * 100)

    all_results.append(result)

# JSON 저장
json_path = os.path.join(os.getcwd(), 'policies.json')
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(all_results, f, ensure_ascii=False, indent=4)

print(f"✅ 크롤링 결과가 {json_path} 파일로 저장되었습니다.")
