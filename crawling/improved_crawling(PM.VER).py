import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urljoin
import time

class WelfareCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def crawl_seoul(self):
        """서울시 복지 정보 크롤링"""
        print("🔄 서울시 복지 정보 크롤링 시작...")
        
        seoul_urls = [
            "https://wis.seoul.go.kr/wfs/ywf/sickMan.do",
            "https://wis.seoul.go.kr/wfs/ywf/selfReliance.do",
            "https://wis.seoul.go.kr/wfs/ywf/saveAccnt.do"
        ]
        
        results = []
        for url in seoul_urls:
            try:
                result = self._crawl_single_page(url, "서울")
                if result:
                    results.append(result)
                time.sleep(1)  # 서버 부하 방지
            except Exception as e:
                print(f"❌ 서울 크롤링 에러 ({url}): {e}")
                
        return results
    
    def crawl_incheon(self):
        """인천시 복지 정보 크롤링"""
        print("🔄 인천시 복지 정보 크롤링 시작...")
        
        # 인천시 청년정책 사이트에서 목록 페이지 크롤링
        base_url = "https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoList.do"
        
        results = []
        try:
            # 목록 페이지에서 정책 URL들 수집
            policy_urls = self._get_incheon_policy_urls()
            
            for url in policy_urls[:20]:  # 최대 20개로 제한
                try:
                    result = self._crawl_single_page(url, "인천")
                    if result:
                        results.append(result)
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ 인천 크롤링 에러 ({url}): {e}")
                    
        except Exception as e:
            print(f"❌ 인천 크롤링 초기화 에러: {e}")
            
        return results
    
    def crawl_gyeonggi(self):
        """경기도 복지 정보 크롤링"""
        print("🔄 경기도 복지 정보 크롤링 시작...")
        
        base_url = "https://youth.gg.go.kr/gg/intro/youth-policy-job-test.do"
        
        results = []
        try:
            # 경기도 청년정책 목록에서 URL 수집
            policy_urls = self._get_gyeonggi_policy_urls()
            
            for url in policy_urls[:20]:  # 최대 20개로 제한
                try:
                    result = self._crawl_single_page(url, "경기")
                    if result:
                        results.append(result)
                    time.sleep(1)
                except Exception as e:
                    print(f"❌ 경기 크롤링 에러 ({url}): {e}")
                    
        except Exception as e:
            print(f"❌ 경기 크롤링 초기화 에러: {e}")
            
        return results
    
    def _get_incheon_policy_urls(self):
        """인천시 정책 URL 목록 수집"""
        urls = []
        try:
            response = self.session.get("https://youth.incheon.go.kr/youthpolicy/youthPolicyInfoList.do")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 정책 링크들 찾기
            links = soup.select('a[href*="youthPolicyInfoDetail.do"]')
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin("https://youth.incheon.go.kr/", href)
                    urls.append(full_url)
                    
        except Exception as e:
            print(f"인천 URL 수집 에러: {e}")
            
        return urls
    
    def _get_gyeonggi_policy_urls(self):
        """경기도 정책 URL 목록 수집"""
        urls = []
        try:
            response = self.session.get("https://youth.gg.go.kr/gg/intro/youth-policy-job-test.do?mode=list")
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 정책 링크들 찾기
            links = soup.select('a[href*="mode=view"]')
            for link in links:
                href = link.get('href')
                if href:
                    full_url = urljoin("https://youth.gg.go.kr/", href)
                    urls.append(full_url)
                    
        except Exception as e:
            print(f"경기 URL 수집 에러: {e}")
            
        return urls
    
    def _crawl_single_page(self, url, region):
        """단일 페이지 크롤링"""
        try:
            response = self.session.get(url, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            result = {
                'url': url,
                'region': region,
                'title': '',
                'age_range': [],
                'application_period': '',
                'conditions': '',
                'benefits': ''
            }
            
            # 제목 추출
            title_selectors = [
                '.title-area h2',
                '.b-title-box span',
                'h1',
                '.page-title',
                'title'
            ]
            
            for selector in title_selectors:
                title_tag = soup.select_one(selector)
                if title_tag:
                    result['title'] = title_tag.get_text(strip=True)
                    break
            
            if not result['title']:
                result['title'] = '제목 없음'
            
            # 내용 영역 찾기
            content_selectors = [
                '.txt-tp1',
                '#detail_con .line-box',
                '.box-gray',
                '.con-box',
                '.content-area',
                '.detail-content'
            ]
            
            content_text = ""
            for selector in content_selectors:
                content_box = soup.select_one(selector)
                if content_box:
                    content_text = content_box.get_text(separator=" ", strip=True)
                    break
            
            if not content_text:
                return None
            
            # 나이 범위 추출
            result['age_range'] = self._extract_age_range(content_text)
            
            # 신청기간 추출
            result['application_period'] = self._extract_application_period(content_text)
            
            # 조건/혜택 추출
            result['conditions'], result['benefits'] = self._extract_conditions_benefits(soup)
            
            return result
            
        except Exception as e:
            print(f"페이지 크롤링 에러 ({url}): {e}")
            return None
    
    def _extract_age_range(self, text):
        """나이 범위 추출"""
        # 정규식 패턴들
        patterns = [
            r'(\d{1,2})\s*세\s*[~\-]\s*(\d{1,2})\s*세',  # 20세~29세
            r'만\s*(\d{1,2})\s*세\s*이하',  # 만 29세 이하
            r'(\d{1,2})\s*[~\-]\s*(\d{1,2})\s*세',  # 20~29세
            r'만\s*(\d{1,2})\s*[~\-]\s*(\d{1,2})\s*세'  # 만 20~29세
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    start, end = int(match.group(1)), int(match.group(2))
                    return list(range(start, end + 1))
                else:
                    max_age = int(match.group(1))
                    return list(range(0, max_age + 1))
        
        # 키워드 기반 추출
        if '청년' in text or '대학생' in text:
            return list(range(20, 30))
        
        return []
    
    def _extract_application_period(self, text):
        """신청기간 추출"""
        patterns = [
            r'신청기간[^\d]*(\d{4}[.\-]\d{2}[.\-]\d{2})\s*[~\-]\s*(\d{4}[.\-]\d{2}[.\-]\d{2})',
            r'접수기간[^\d]*(\d{4}[.\-]\d{2}[.\-]\d{2})\s*[~\-]\s*(\d{4}[.\-]\d{2}[.\-]\d{2})',
            r'(\d{4}[.\-]\d{2}[.\-]\d{2})\s*[~\-]\s*(\d{4}[.\-]\d{2}[.\-]\d{2})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return f"{match.group(1)}~{match.group(2)}"
        
        return '미정'
    
    def _extract_conditions_benefits(self, soup):
        """조건과 혜택 추출"""
        conditions = ""
        benefits = ""
        
        # 조건/혜택 관련 섹션 찾기
        sections = soup.find_all(['h3', 'h4', 'h5'])
        
        for section in sections:
            section_text = section.get_text(strip=True)
            next_elements = section.find_next_siblings(['ul', 'p', 'div'])
            
            content = ""
            for elem in next_elements[:3]:  # 최대 3개 요소까지만
                if elem.name == 'ul':
                    content += elem.get_text(separator=' ', strip=True) + " "
                elif elem.name in ['p', 'div']:
                    content += elem.get_text(strip=True) + " "
            
            if any(keyword in section_text for keyword in ['지원대상', '사업대상', '신청자격', '지원자격', '조건']):
                conditions += content
            elif any(keyword in section_text for keyword in ['사업내용', '지원내용', '혜택', '지원금액']):
                benefits += content
        
        return conditions.strip(), benefits.strip()
    
    def save_to_json(self, data, filename):
        """JSON 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"✅ {filename}에 {len(data)}개 정책 저장 완료")

def main():
    crawler = WelfareCrawler()
    
    # 각 지역별 크롤링
    seoul_data = crawler.crawl_seoul()
    incheon_data = crawler.crawl_incheon()
    gyeonggi_data = crawler.crawl_gyeonggi()
    
    # 통합 데이터
    all_data = seoul_data + incheon_data + gyeonggi_data
    
    # JSON 파일로 저장
    crawler.save_to_json(all_data, 'welfare_policies.json')
    
    print(f"\n📊 크롤링 완료!")
    print(f"서울: {len(seoul_data)}개")
    print(f"인천: {len(incheon_data)}개")
    print(f"경기: {len(gyeonggi_data)}개")
    print(f"총계: {len(all_data)}개")

if __name__ == "__main__":
    main() 