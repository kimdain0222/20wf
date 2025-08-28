#!/usr/bin/env python3
"""
AI 챗봇 테스트 스크립트
"""

import requests
import json
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 서버 URL (로컬 테스트용)
BASE_URL = "http://localhost:5000"

def test_ai_chat():
    """AI 챗봇 테스트"""
    
    # 테스트 메시지들
    test_messages = [
        "안녕하세요! 청년 주택 지원 정책에 대해 알고 싶어요.",
        "서울에 사는 25살 청년인데 어떤 정책을 받을 수 있을까요?",
        "경기도에서 창업하고 싶은데 지원받을 수 있는 정책이 있나요?",
        "인천에 사는 30대인데 문화생활 지원 정책이 궁금해요."
    ]
    
    print("🤖 AI 챗봇 테스트 시작...\n")
    
    for i, message in enumerate(test_messages, 1):
        print(f"📝 테스트 {i}: {message}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": message},
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"✅ AI 응답: {data['response']}")
                else:
                    print(f"❌ 오류: {data.get('error', '알 수 없는 오류')}")
            else:
                print(f"❌ HTTP 오류: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 예외 발생: {e}")
        
        print("\n" + "="*60 + "\n")

def test_health_check():
    """서버 상태 확인"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            print("✅ 서버가 정상 작동 중입니다!")
            return True
        else:
            print(f"❌ 서버 상태 확인 실패: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 서버 연결 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚀 복지정책 AI 챗봇 테스트")
    print("=" * 60)
    
    # 서버 상태 확인
    if not test_health_check():
        print("서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.")
        exit(1)
    
    # AI 챗봇 테스트
    test_ai_chat()
    
    print("🎉 테스트 완료!")
