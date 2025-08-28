from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import json
import os
import openai
from datetime import datetime
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = Flask(__name__)
CORS(app, origins=['https://welfarechatbot02.netlify.app', 'http://localhost:3000'])

# OpenAI API 설정
openai.api_key = os.getenv('OPENAI_API_KEY', 'your-openai-api-key-here')

# PostgreSQL 설정
POSTGRES_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'database': os.getenv('POSTGRES_DB', 'welfare_chatbot'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', ''),
    'port': os.getenv('POSTGRES_PORT', '5432')
}

def get_db_connection():
    """PostgreSQL 데이터베이스 연결"""
    try:
        conn = psycopg2.connect(**POSTGRES_CONFIG)
        return conn
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")
        return None

def get_policies_for_ai():
    """AI 응답을 위한 정책 데이터 준비"""
    try:
        conn = get_db_connection()
        if not conn:
            return []
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT 
                p.title, p.description, p.conditions, p.benefits, 
                p.application_period, p.support_amount_min, p.support_amount_max,
                r.name as region_name, c.name as category_name,
                p.age_min, p.age_max, p.status
            FROM policies p
            LEFT JOIN regions r ON p.region_id = r.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.status = 'active'
            ORDER BY p.priority DESC, p.view_count DESC
            LIMIT 20
        ''')
        
        policies = cursor.fetchall()
        conn.close()
        
        # DictRow를 일반 딕셔너리로 변환
        return [dict(policy) for policy in policies]
    except Exception as e:
        print(f"정책 데이터 조회 오류: {e}")
        return []

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    try:
        conn = get_db_connection()
        if conn:
            conn.close()
            return jsonify({
                "status": "healthy", 
                "message": "API 서버와 PostgreSQL이 정상 작동 중입니다!",
                "database": "PostgreSQL"
            })
        else:
            return jsonify({
                "status": "unhealthy",
                "message": "데이터베이스 연결에 문제가 있습니다.",
                "database": "PostgreSQL"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"서버 오류: {str(e)}",
            "database": "PostgreSQL"
        }), 500

@app.route('/api/policies', methods=['GET'])
def get_all_policies():
    """모든 정책 조회 (고급 검색)"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "데이터베이스 연결 실패"}), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 쿼리 파라미터
        region = request.args.get('region')
        category = request.args.get('category')
        age = request.args.get('age')
        keyword = request.args.get('keyword')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # 기본 쿼리
        query = '''
            SELECT 
                p.id, p.title, p.description, p.url, p.conditions, p.benefits,
                p.application_period, p.support_amount_min, p.support_amount_max,
                p.age_min, p.age_max, p.status, p.priority, p.view_count,
                r.name as region_name, c.name as category_name, c.color as category_color,
                p.created_at, p.updated_at
            FROM policies p
            LEFT JOIN regions r ON p.region_id = r.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.status = 'active'
        '''
        
        params = []
        
        # 필터 조건 추가
        if region:
            query += " AND r.name = %s"
            params.append(region)
        
        if category:
            query += " AND c.name = %s"
            params.append(category)
        
        if age:
            try:
                age_int = int(age)
                query += " AND (%s BETWEEN p.age_min AND p.age_max OR (p.age_min IS NULL AND p.age_max IS NULL))"
                params.append(age_int)
            except ValueError:
                pass
        
        if keyword:
            query += " AND (p.title ILIKE %s OR p.description ILIKE %s OR p.conditions ILIKE %s OR p.benefits ILIKE %s)"
            keyword_param = f"%{keyword}%"
            params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
        
        # 정렬 및 페이징
        query += " ORDER BY p.priority DESC, p.view_count DESC, p.created_at DESC"
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        policies = cursor.fetchall()
        
        # 총 개수 조회
        count_query = '''
            SELECT COUNT(*) 
            FROM policies p
            LEFT JOIN regions r ON p.region_id = r.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.status = 'active'
        '''
        
        count_params = []
        if region:
            count_query += " AND r.name = %s"
            count_params.append(region)
        if category:
            count_query += " AND c.name = %s"
            count_params.append(category)
        if age:
            try:
                age_int = int(age)
                count_query += " AND (%s BETWEEN p.age_min AND p.age_max OR (p.age_min IS NULL AND p.age_max IS NULL))"
                count_params.append(age_int)
            except ValueError:
                pass
        if keyword:
            count_query += " AND (p.title ILIKE %s OR p.description ILIKE %s OR p.conditions ILIKE %s OR p.benefits ILIKE %s)"
            keyword_param = f"%{keyword}%"
            count_params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
        
        cursor.execute(count_query, count_params)
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "success": True,
            "policies": [dict(policy) for policy in policies],
            "total_count": total_count,
            "limit": limit,
            "offset": offset
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/policies/region/<region>', methods=['GET'])
def get_policies_by_region(region):
    """지역별 정책 조회"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "데이터베이스 연결 실패"}), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT 
                p.id, p.title, p.description, p.url, p.conditions, p.benefits,
                p.application_period, p.support_amount_min, p.support_amount_max,
                p.age_min, p.age_max, p.status, p.priority, p.view_count,
                r.name as region_name, c.name as category_name, c.color as category_color,
                p.created_at, p.updated_at
            FROM policies p
            LEFT JOIN regions r ON p.region_id = r.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE r.name = %s AND p.status = 'active'
            ORDER BY p.priority DESC, p.view_count DESC
        ''', (region,))
        
        policies = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "success": True,
            "region": region,
            "count": len(policies),
            "policies": [dict(policy) for policy in policies]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/policies/<int:policy_id>', methods=['GET'])
def get_policy_detail(policy_id):
    """정책 상세 정보 조회"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "데이터베이스 연결 실패"}), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 조회수 증가
        cursor.execute('UPDATE policies SET view_count = view_count + 1 WHERE id = %s', (policy_id,))
        
        # 정책 정보 조회
        cursor.execute('''
            SELECT 
                p.*, r.name as region_name, c.name as category_name, c.color as category_color
            FROM policies p
            LEFT JOIN regions r ON p.region_id = r.id
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.id = %s
        ''', (policy_id,))
        
        policy = cursor.fetchone()
        conn.close()
        
        if not policy:
            return jsonify({
                "success": False,
                "error": "정책을 찾을 수 없습니다."
            }), 404
        
        return jsonify({
            "success": True,
            "policy": dict(policy)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """카테고리 목록 조회"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "데이터베이스 연결 실패"}), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, name, description, icon, color
            FROM categories
            ORDER BY name
        ''')
        
        categories = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "success": True,
            "categories": [dict(category) for category in categories]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """지역 목록 조회"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "데이터베이스 연결 실패"}), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        cursor.execute('''
            SELECT id, code, name, level
            FROM regions
            WHERE level = 1
            ORDER BY name
        ''')
        
        regions = cursor.fetchall()
        conn.close()
        
        return jsonify({
            "success": True,
            "regions": [dict(region) for region in regions]
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """통계 정보 조회"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "error": "데이터베이스 연결 실패"}), 500
        
        cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # 전체 정책 수
        cursor.execute("SELECT COUNT(*) as total FROM policies WHERE status = 'active'")
        total_policies = cursor.fetchone()['total']
        
        # 지역별 정책 수
        cursor.execute('''
            SELECT r.name, COUNT(*) as count
            FROM policies p
            LEFT JOIN regions r ON p.region_id = r.id
            WHERE p.status = 'active'
            GROUP BY r.name
            ORDER BY count DESC
        ''')
        region_stats = cursor.fetchall()
        
        # 카테고리별 정책 수
        cursor.execute('''
            SELECT c.name, COUNT(*) as count
            FROM policies p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.status = 'active'
            GROUP BY c.name
            ORDER BY count DESC
        ''')
        category_stats = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            "success": True,
            "statistics": {
                "total_policies": total_policies,
                "regions": [dict(stat) for stat in region_stats],
                "categories": [dict(stat) for stat in category_stats]
            }
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
   - 지역: {policy['region_name']}
   - 카테고리: {policy['category_name']}
   - 대상 연령: {policy['age_min']}~{policy['age_max']}세
   - 지원금액: {policy['support_amount_min']}~{policy['support_amount_max']}만원
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
    print("🚀 복지정책 PostgreSQL API 서버 시작...")
    print("📊 사용 가능한 엔드포인트:")
    print("   GET /api/health - 서버 상태 확인")
    print("   GET /api/policies - 모든 정책 조회 (고급 검색)")
    print("   GET /api/policies/region/<region> - 지역별 정책 조회")
    print("   GET /api/policies/<id> - 정책 상세 정보")
    print("   GET /api/categories - 카테고리 목록")
    print("   GET /api/regions - 지역 목록")
    print("   GET /api/stats - 통계 정보")
    print("   POST /api/chat - AI 챗봇 대화")
    print("\n🌐 서버 주소: http://localhost:5000")
    
    # 프로덕션 환경에서는 gunicorn 사용, 개발 환경에서는 Flask 개발 서버 사용
    import os
    if os.getenv('FLASK_ENV') == 'production':
        # gunicorn으로 실행 (프로덕션)
        app.run(debug=False, host='0.0.0.0', port=5000)
    else:
        # Flask 개발 서버 (개발)
        app.run(debug=True, host='0.0.0.0', port=5000)
