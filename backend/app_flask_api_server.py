from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
import os
import openai
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=['https://welfarechatbot02.netlify.app', 'http://localhost:3000'])  # React에서 API 호출할 수 있도록 CORS 설정

# OpenAI API 설정
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

# DB 파일 경로
DB_PATH = "welfare_policies.db"

def get_db_connection():
    """데이터베이스 연결"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
    return conn

def get_policies_for_ai():
    """AI 응답을 위한 정책 데이터 준비"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT title, region, age_range, conditions, benefits, application_period
            FROM welfare_policies
            ORDER BY region, title
        ''')
        
        policies = []
        for row in cursor.fetchall():
            policy = dict(row)
            if policy['age_range']:
                policy['age_range'] = json.loads(policy['age_range'])
            else:
                policy['age_range'] = []
            policies.append(policy)
        
        conn.close()
        return policies
    except Exception as e:
        print(f"정책 데이터 조회 오류: {e}")
        return []

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({"status": "healthy", "message": "API 서버가 정상 작동 중입니다!"})

@app.route('/api/policies/region/<region>', methods=['GET'])
def get_policies_by_region(region):
    """지역별 정책 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, url, region, age_range, application_period, conditions, benefits
            FROM welfare_policies
            WHERE region = ?
            ORDER BY title
        ''', (region,))
        
        policies = []
        for row in cursor.fetchall():
            policy = dict(row)
            if policy['age_range']:
                policy['age_range'] = json.loads(policy['age_range'])
            else:
                policy['age_range'] = []
            policies.append(policy)
        
        conn.close()
        return jsonify({
            "success": True,
            "region": region,
            "count": len(policies),
            "policies": policies
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/policies', methods=['GET'])
def get_all_policies():
    """모든 정책 조회"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, title, url, region, age_range, application_period, conditions, benefits
            FROM welfare_policies
            ORDER BY region, title
        ''')
        
        policies = []
        for row in cursor.fetchall():
            policy = dict(row)
            if policy['age_range']:
                policy['age_range'] = json.loads(policy['age_range'])
            else:
                policy['age_range'] = []
            policies.append(policy)
        
        conn.close()
        return jsonify({
            "success": True,
            "count": len(policies),
            "policies": policies
        })
    
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_ai():
    """AI 챗봇과의 대화"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({
                "success": False,
                "error": "메시지가 필요합니다."
            }), 400
        
        # 정책 데이터 가져오기
        policies = get_policies_for_ai()
        
        # OpenAI GPT에 전달할 시스템 프롬프트 생성
        system_prompt = f"""
당신은 복지정책 전문 상담사입니다. 다음 정책 정보를 바탕으로 사용자의 질문에 친근하고 도움이 되는 답변을 해주세요.

**사용 가능한 정책 정보 ({len(policies)}개):**
"""
        
        for i, policy in enumerate(policies[:10], 1):  # 처음 10개만 예시로 포함
            system_prompt += f"""
{i}. {policy['title']}
   - 지역: {policy['region']}
   - 대상 연령: {', '.join(policy['age_range']) if policy['age_range'] else '제한없음'}
   - 지원 조건: {policy['conditions'][:100]}...
   - 혜택: {policy['benefits'][:100]}...
   - 신청 기간: {policy['application_period']}
"""

        system_prompt += """

**응답 가이드라인:**
1. 사용자의 상황을 파악하여 적절한 정책을 추천해주세요
2. 지역, 나이, 관심사에 따라 맞춤형 답변을 제공하세요
3. 친근하고 이해하기 쉬운 언어를 사용하세요
4. 구체적인 혜택과 신청 방법을 설명해주세요
5. 관련된 다른 정책도 함께 추천해주세요

**주의사항:**
- 정확한 정보만 제공하세요
- 신청 기간이 지난 정책은 언급하지 마세요
- 사용자가 더 구체적인 정보를 원하면 질문해주세요
"""

        # OpenAI GPT API 호출
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({
            "success": True,
            "response": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"AI 챗봇 오류: {e}")
        return jsonify({
            "success": False,
            "error": "AI 응답 생성 중 오류가 발생했습니다.",
            "fallback_response": "죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요."
        }), 500

if __name__ == '__main__':
    print("🚀 복지정책 API 서버 시작...")
    print("📊 사용 가능한 엔드포인트:")
    print("   GET /api/health - 서버 상태 확인")
    print("   GET /api/policies - 모든 정책 조회")
    print("   GET /api/policies/region/<region> - 지역별 정책 조회")
    print("\n🌐 서버 주소: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 