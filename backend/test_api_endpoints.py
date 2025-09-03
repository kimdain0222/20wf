#!/usr/bin/env python3
"""
백엔드 API 엔드포인트 테스트 스크립트
"""

import requests
import json

def test_api_endpoints():
    """API 엔드포인트 테스트"""
    base_url = "https://20wf-production.up.railway.app"
    
    print("🔍 백엔드 API 엔드포인트 테스트 시작...")
    print(f"📍 테스트 대상: {base_url}")
    print("-" * 50)
    
    # 1. 헬스체크
    print("1️⃣ 헬스체크 테스트...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   상태코드: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ 헬스체크 성공")
            print(f"   응답: {response.text}")
        else:
            print("   ❌ 헬스체크 실패")
    except Exception as e:
        print(f"   ❌ 헬스체크 오류: {e}")
    
    print()
    
    # 2. 지역별 정책 조회 (서울)
    print("2️⃣ 서울 지역 정책 조회 테스트...")
    try:
        response = requests.get(f"{base_url}/api/policies/region/seoul", timeout=10)
        print(f"   상태코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 서울 정책 조회 성공")
            print(f"   정책 수: {len(data.get('policies', []))}")
            if data.get('policies'):
                print(f"   첫 번째 정책: {data['policies'][0].get('title', '제목 없음')}")
        else:
            print("   ❌ 서울 정책 조회 실패")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   ❌ 서울 정책 조회 오류: {e}")
    
    print()
    
    # 3. 전체 정책 조회
    print("3️⃣ 전체 정책 조회 테스트...")
    try:
        response = requests.get(f"{base_url}/api/policies", timeout=10)
        print(f"   상태코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 전체 정책 조회 성공")
            print(f"   정책 수: {len(data.get('policies', []))}")
        else:
            print("   ❌ 전체 정책 조회 실패")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   ❌ 전체 정책 조회 오류: {e}")
    
    print()
    
    # 4. 챗봇 API 테스트
    print("4️⃣ 챗봇 API 테스트...")
    try:
        payload = {"message": "안녕하세요"}
        response = requests.post(f"{base_url}/api/chat", json=payload, timeout=10)
        print(f"   상태코드: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 챗봇 API 성공")
            print(f"   응답: {data.get('response', '응답 없음')[:100]}...")
        else:
            print("   ❌ 챗봇 API 실패")
            print(f"   응답: {response.text}")
    except Exception as e:
        print(f"   ❌ 챗봇 API 오류: {e}")
    
    print("-" * 50)
    print("🏁 API 테스트 완료!")

if __name__ == "__main__":
    test_api_endpoints()
