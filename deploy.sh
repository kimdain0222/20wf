#!/bin/bash

echo "🚀 복지정책 챗봇 배포 시작!"

# 1. Git 저장소 초기화
echo "📦 Git 저장소 초기화..."
cd "C:\B조"
git init
git add .
git commit -m "Initial commit: 복지정책 챗봇 프로젝트"

echo "✅ Git 초기화 완료!"
echo ""
echo "📋 다음 단계를 따라 배포를 진행하세요:"
echo ""
echo "1. GitHub에서 새 저장소 생성"
echo "2. 아래 명령어 실행:"
echo "   git remote add origin https://github.com/your-username/welfare-chatbot.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Railway에서 백엔드 배포"
echo "4. Vercel에서 프론트엔드 배포"
echo ""
echo "📖 자세한 배포 가이드는 '배포_가이드.md' 파일을 참조하세요!" 