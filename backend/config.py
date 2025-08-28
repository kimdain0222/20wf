import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # IBM Watsonx.ai API 설정
    IBM_API_KEY = os.getenv('IBM_API_KEY', 'kYt1RUcGM7Z2ABr5562ECaO8I5wSQ3UPU6pAYHiWy3C7')
    WATSON_ENDPOINT = os.getenv('WATSON_ENDPOINT', 'https://us-south.ml.cloud.ibm.com/ml/v1/text/generation')
    
    # 데이터베이스 설정
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///welfare_policies.db')
    
    # CORS 설정
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # 서버 설정
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true' 