import React, { useState, useEffect } from "react";
import "./App.css";

function BotMessage({ profileSrc, children, time }) {
  return (
    <div style={{ marginBottom: "6px" }}>
      <div className="chat-message bot">
        {profileSrc && <img className="profile-img" src={profileSrc} alt="profile" />}
        <div className="message-text">{children}</div>
      </div>
      {time && (
        <div
          className="time-label"
          style={{ textAlign: "left", marginLeft: "60px", marginTop: "4px" }}
        >
          {time}
        </div>
      )}
    </div>
  );
}

// 로고 없는 봇 메시지
function BotMessageNoLogo({ children, time }) {
  return (
    <div style={{ marginBottom: "6px" }}>
      <div className="chat-message bot">
        <div className="message-text no-logo-message-text">{children}</div>
      </div>
      {time && (
        <div
          className="time-label"
          style={{ textAlign: "left", marginLeft: "60px", marginTop: "4px" }}
        >
          {time}
        </div>
      )}
    </div>
  );
}

function UserMessage({ children, time }) {
  return (
    <div style={{ marginBottom: "6px" }}>
      <div className="chat-message user">
        <div className="message-text">{children}</div>
      </div>
      {time && <div className="time-label user-time-label">{time}</div>}
    </div>
  );
}

// 요약+상세 토글 메시지 컴포넌트
function PoliciesSummary({ count, onToggle, isOpen }) {
  return (
    <>
      <BotMessageNoLogo>
        선택하신 지역과 나이에 맞는 <br />
        지원금 <span className="count-highlight">{count}건</span>을 찾았어요!
      </BotMessageNoLogo>

      <BotMessageNoLogo>
        <button
          onClick={onToggle}
          className="details-toggle-button"
          type="button"
          style={{
            background: "transparent",
            border: "none",
            color: "black",
            cursor: "pointer",
            fontSize: "12px",
            fontWeight: "normal",
            padding: 0,
          }}
        >
          {isOpen
            ? "[\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 접기 ▲ \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0]"
            : "[\u00A0\u00A0\u00A0\u00A0\u00A0\u00A0 자세히보기 ▼ \u00A0\u00A0\u00A0\u00A0\u00A0\u00A0]"}
        </button>
      </BotMessageNoLogo>
    </>
  );
}

function App() {
  const regionMap = { 서울: "seoul", 경기: "gyeonggi", 인천: "incheon" };

  const [showIntro, setShowIntro] = useState(true);
  const [directChatMode, setDirectChatMode] = useState(false);
  const [currentDate, setCurrentDate] = useState(new Date());

  const [inputValue, setInputValue] = useState("");
  const [messages, setMessages] = useState([]);

  const [showRegionPrompt, setShowRegionPrompt] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState("");
  const [showUserMessage, setShowUserMessage] = useState(false);
  const [showAgePrompt, setShowAgePrompt] = useState(false);
  const [showAgeDropdown, setShowAgeDropdown] = useState(false);
  const [selectedAge, setSelectedAge] = useState("");
  const [regionSelectedAt, setRegionSelectedAt] = useState(null);
  const [ageDropdownAt, setAgeDropdownAt] = useState(null);

  const [policies, setPolicies] = useState([]);
  const [filteredPolicies, setFilteredPolicies] = useState([]);

  const [showDetails, setShowDetails] = useState(false);
  const [ageDropdownExpanded, setAgeDropdownExpanded] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setCurrentDate(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!showIntro && !directChatMode) {
      const timer = setTimeout(() => setShowRegionPrompt(true), 600);
      return () => clearTimeout(timer);
    }
  }, [showIntro, directChatMode]);

  const formattedDate = (date) =>
    `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(
      date.getDate()
    ).padStart(2, "0")} (${date.toLocaleDateString("ko-KR", { weekday: "short" })})`;

  const formattedTime = (date) =>
    `${String(date.getHours()).padStart(2, "0")}:${String(date.getMinutes()).padStart(2, "0")}`;

  // 간단한 AI 응답 함수 (폴백 옵션)
  const getSimpleAIResponse = (userMessage) => {
    const message = userMessage.toLowerCase();
    
    // 지역 확인
    const regions = ["서울", "경기", "인천"];
    const foundRegion = regions.find(region => message.includes(region));
    
    // 나이 확인
    const ageMatch = message.match(/(\d+)세|(\d+)살/);
    const hasAge = ageMatch || message.includes("20대") || message.includes("청년");
    
    // 카테고리별 키워드 확인 (더 구체적으로 개선)
    const categoryKeywords = {
      housing: ["주거", "월세", "전세", "임대료", "주택", "주거지원", "주거비", "임대", "보증금", "매입임대", "거주비"],
      employment: ["취업", "일자리", "구직", "채용", "고용", "취업지원", "구직활동", "인턴", "면접"],
      culture: ["문화", "공연", "전시", "예술", "콘서트", "뮤지컬", "연극", "문화패스"],
      transportation: ["교통", "교통비", "버스", "지하철", "대중교통"],
      savings: ["저축", "적금", "계좌", "금융", "투자", "통장"],
      education: ["학자금", "교육비", "장학금", "등록금", "학비"],
      general: ["지원금", "복지", "정책", "혜택", "청년", "지원", "거주"]
    };
    
    // 구체적인 카테고리 찾기
    let foundCategory = null;
    let foundKeywords = [];
    
    for (const [category, keywords] of Object.entries(categoryKeywords)) {
      const matchedKeywords = keywords.filter(keyword => message.includes(keyword));
      if (matchedKeywords.length > 0) {
        if (category !== 'general') {
          foundCategory = category;
          foundKeywords = matchedKeywords;
          break; // 구체적인 카테고리를 찾으면 중단
        } else {
          foundKeywords = matchedKeywords; // 일반 키워드는 백업으로 저장
        }
      }
    }
    
    const categoryNames = {
      housing: "주거 관련",
      employment: "취업 관련", 
      culture: "문화 관련",
      transportation: "교통 관련",
      savings: "저축 관련",
      education: "교육 관련"
    };
    
    if (foundRegion && hasAge && (foundCategory || foundKeywords.length > 0)) {
      const categoryText = foundCategory ? categoryNames[foundCategory] : "관련";
      return {
        response: `${foundRegion} 지역의 ${categoryText} 정책을 찾아드릴게요! 잠시만 기다려주세요.`,
        shouldSearchPolicies: true,
        region: foundRegion,
        keywords: foundKeywords,
        category: foundCategory
      };
    } else if (!foundRegion) {
      return {
        response: "어느 지역에 거주하고 계신가요? (서울, 경기, 인천 중 선택해주세요)",
        shouldSearchPolicies: false
      };
    } else if (!hasAge) {
      return {
        response: "나이대를 알려주시면 더 정확한 정책을 찾아드릴 수 있어요. 몇 살이신가요?",
        shouldSearchPolicies: false
      };
    } else if (!foundCategory && foundKeywords.length === 0) {
      return {
        response: "어떤 종류의 지원이나 정책에 관심이 있으신가요? (예: 주거지원, 취업지원, 문화지원 등)",
        shouldSearchPolicies: false
      };
    } else {
      return {
        response: "더 자세한 정보를 알려주시면 맞춤 정책을 찾아드릴게요!",
        shouldSearchPolicies: false
      };
    }
  };

  // AI 챗봇 API 호출 함수
  const sendMessageToAI = async (userMessage) => {
    try {
      console.log("AI 챗봇 API 호출 중...");
      
      const response = await fetch('https://your-backend-url.railway.app/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage
        })
      });
      
      if (!response.ok) {
        console.error("AI API 호출 실패:", response.status);
        return getSimpleAIResponse(userMessage);
      }
      
      const data = await response.json();
      
      if (data.success) {
        console.log("AI 응답 성공:", data.response);
        return data.response;
      } else {
        console.error("AI 응답 실패:", data.error);
        return data.fallback_response || getSimpleAIResponse(userMessage);
      }
    } catch (error) {
      console.error("AI API 호출 중 예외 발생:", error);
      return getSimpleAIResponse(userMessage);
    }
    
    /* Watsonx.ai API 코드 (현재 비활성화)
    const IBM_API_KEY = "kYt1RUcGM7Z2ABr5562ECaO8I5wSQ3UPU6pAYHiWy3C7";
    
    try {
      console.log("1. API 토큰 요청 시작...");
      
      // Access Token 요청
      const tokenResponse = await fetch("https://iam.cloud.ibm.com/identity/token", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: `grant_type=urn:ibm:params:oauth:grant-type:apikey&apikey=${IBM_API_KEY}`
      });
      
      console.log("2. 토큰 응답 상태:", tokenResponse.status);
      
      if (!tokenResponse.ok) {
        const errorText = await tokenResponse.text();
        console.error("토큰 요청 실패:", errorText);
        return getSimpleAIResponse(userMessage);
      }
      
      const tokenData = await tokenResponse.json();
      console.log("3. 토큰 데이터:", tokenData);
      
      if (!tokenData.access_token) {
        console.error("액세스 토큰이 없습니다:", tokenData);
        return getSimpleAIResponse(userMessage);
      }
      
      const accessToken = tokenData.access_token;
      console.log("4. 액세스 토큰 획득 성공");

      // Watsonx.ai 모델 호출
      console.log("5. Watsonx.ai API 호출 시작...");
      
      const requestBody = {
        input: `사용자 질문: "${userMessage}"\n\n위 질문을 분석해서 다음 중 어떤 정보가 필요한지 파악하고, 간단하고 친근한 톤으로 응답해주세요:\n1. 지역 정보 (서울, 경기, 인천)\n2. 나이 정보\n3. 관심 있는 지원금/정책 키워드\n\n만약 모든 정보가 있다면 "정보를 찾아드릴게요!"라고 응답하고, 부족한 정보가 있다면 무엇이 더 필요한지 물어보세요.`,
        parameters: {
          decoding_method: "sample",
          max_new_tokens: 200,
          temperature: 0.7,
          top_p: 1,
          top_k: 50,
          repetition_penalty: 1
        }
      };
      
      console.log("6. 요청 본문:", requestBody);
      
      const response = await fetch(
        "https://us-south.ml.cloud.ibm.com/ml/v4/deployments/14d914db-7824-400e-a29c-0fb60b26a8c1/text/generation?version=2021-05-01",
        {
          method: "POST",
          headers: {
            "Authorization": "Bearer " + accessToken,
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify(requestBody)
        }
      );

      console.log("7. Watsonx.ai 응답 상태:", response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Watsonx.ai API 호출 실패:", response.status, errorText);
        return getSimpleAIResponse(userMessage);
      }
      
      const data = await response.json();
      console.log("8. Watsonx.ai 응답 데이터:", data);
      
      const result = data.results?.[0]?.generated_text || getSimpleAIResponse(userMessage);
      console.log("9. 최종 결과:", result);
      
      return result;
    } catch (error) {
      console.error("AI API 호출 중 예외 발생:", error);
      console.error("에러 스택:", error.stack);
      return getSimpleAIResponse(userMessage);
    }
    */
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    // 사용자 메시지 추가
    setMessages((prev) => [
      ...prev,
      { type: "user", text: inputValue, time: formattedTime(new Date()) },
    ]);
    
    const userInput = inputValue;
    setInputValue("");

    // 직접 대화 모드일 때만 AI 응답 생성
    if (directChatMode) {
      // AI 응답 생성 중 표시
      setMessages((prev) => [
        ...prev,
        { type: "bot", text: "생각 중...", time: formattedTime(new Date()) },
      ]);

      try {
        const aiResult = await sendMessageToAI(userInput);
        
        // "생각 중..." 메시지를 AI 응답으로 교체
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            type: "bot",
            text: aiResult.response || aiResult,
            time: formattedTime(new Date())
          };
          return newMessages;
        });

        // 정책 검색이 필요한 경우 자동으로 검색 실행
        if (aiResult.shouldSearchPolicies) {
          await performPolicySearch(aiResult.region, userInput);
        }
      } catch (error) {
        console.error("AI 응답 생성 실패:", error);
        setMessages((prev) => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            type: "bot",
            text: "죄송합니다. 응답을 생성할 수 없습니다.",
            time: formattedTime(new Date())
          };
          return newMessages;
        });
      }
    }
  };

  // 정책 검색 실행 함수
  const performPolicySearch = async (region, userInput) => {
    console.log(`정책 검색 시작: 지역=${region}, 입력=${userInput}`);
    
    const dbRegion = regionMap[region];
    if (!dbRegion) {
      console.error("지역 매핑 실패:", region);
      return;
    }

    try {
      // 로딩 메시지 추가
      setMessages((prev) => [
        ...prev,
        { 
          type: "bot", 
          text: "정책을 검색하고 있습니다...",
          time: formattedTime(new Date())
        }
      ]);

      // 먼저 지역별 정책을 가져오기
      const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://web-production-a9d2.up.railway.app';
  const apiUrl = `${API_BASE_URL}/api/policies/region/${dbRegion}`;
      console.log("API 호출 URL:", apiUrl);
      
      const response = await fetch(apiUrl);
      
      console.log("API 응답 상태:", response.status);
      console.log("API 응답 헤더:", response.headers);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("API 오류 응답:", errorText);
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log("정책 검색 결과:", data);
      console.log("검색된 정책 수:", data.policies ? data.policies.length : 0);
      
      // 프론트엔드에서 키워드 필터링 (구체적인 카테고리별)
      let filteredPolicies = data.policies || [];
      console.log("🔍 필터링 시작 - userInput:", userInput);
      console.log("🔍 원본 정책 수:", filteredPolicies.length);
      
      if (userInput) {
        const userInputLower = userInput.toLowerCase();
        console.log("🔍 소문자 변환된 입력:", userInputLower);
        
        // 카테고리별 키워드 그룹 (더 구체적으로 개선)
        const categoryKeywords = {
          housing: ["주거", "월세", "전세", "임대료", "주택", "주거지원", "주거비", "임대", "보증금", "매입임대", "거주비"],
          employment: ["취업", "일자리", "구직", "채용", "고용", "취업지원", "구직활동", "인턴", "면접"],
          culture: ["문화", "공연", "전시", "예술", "콘서트", "뮤지컬", "연극", "문화패스"],
          transportation: ["교통", "교통비", "버스", "지하철", "대중교통", "k-패스", "기후동행카드"],
          savings: ["저축", "적금", "계좌", "금융", "투자", "통장"],
          education: ["학자금", "교육비", "장학금", "등록금", "학비"],
          general: ["지원금", "복지", "정책", "혜택", "청년", "지원", "거주"]
        };
        
        // 사용자 입력에서 구체적인 카테고리 찾기
        let matchedCategory = null;
        for (const [category, keywords] of Object.entries(categoryKeywords)) {
          if (category !== 'general' && keywords.some(keyword => userInputLower.includes(keyword))) {
            matchedCategory = category;
            console.log("🎯 매칭된 카테고리:", category, "키워드:", keywords.filter(k => userInputLower.includes(k)));
            break;
          }
        }
        
        console.log("🎯 최종 매칭된 카테고리:", matchedCategory);
        
        // 구체적인 카테고리가 있으면 해당 카테고리로 필터링
        if (matchedCategory) {
          const categoryWords = categoryKeywords[matchedCategory];
          console.log("🔍 필터링에 사용할 키워드들:", categoryWords);
          
          const originalCount = filteredPolicies.length;
          filteredPolicies = filteredPolicies.filter(policy => {
            const policyText = `${policy.title} ${policy.benefits || ''} ${policy.conditions || ''}`.toLowerCase();
            const hasMatch = categoryWords.some(keyword => policyText.includes(keyword));
            if (hasMatch) {
              console.log("✅ 매칭된 정책:", policy.title);
            }
            return hasMatch;
          });
          console.log(`🔍 카테고리 필터링 결과: ${originalCount}개 → ${filteredPolicies.length}개`);
        } else {
          // 일반적인 키워드만 있으면 모든 정책 표시
          const generalKeywords = categoryKeywords.general;
          const hasGeneralKeyword = generalKeywords.some(keyword => userInputLower.includes(keyword));
          console.log("🔍 일반 키워드 체크:", hasGeneralKeyword);
          
          if (hasGeneralKeyword) {
            // 일반 키워드인 경우 모든 정책 표시 (기존 방식 유지)
            filteredPolicies = data.policies || [];
            console.log("🔍 일반 키워드로 모든 정책 표시:", filteredPolicies.length);
          }
        }
      }
      
      console.log("필터링된 정책 수:", filteredPolicies.length);
      
      // 로딩 메시지 제거하고 결과 표시
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages.pop(); // "정책을 검색하고 있습니다..." 메시지 제거
        
        if (data.success && filteredPolicies.length > 0) {
          // 간편찾기와 동일한 형식으로 정책 표시
          newMessages.push({
            type: "bot",
            text: `선택하신 지역과 나이에 맞는\n지원금 ${filteredPolicies.length}건을 찾았어요!`,
            time: formattedTime(new Date())
          });
          
          // 정책 상세 정보를 간편찾기와 동일한 형식으로 표시
          filteredPolicies.slice(0, 5).forEach(policy => {
            let policyInfo = `📋 **${policy.title}**`;
            
            if (policy.application_period) {
              policyInfo += `\n📅 신청기간: ${policy.application_period}`;
            }
            
            if (policy.benefits) {
              const benefitsText = policy.benefits.length > 100 ? policy.benefits.substring(0, 100) + "..." : policy.benefits;
              policyInfo += `\n💰 혜택: ${benefitsText}`;
            }
            
            if (policy.conditions) {
              const conditionsText = policy.conditions.length > 80 ? policy.conditions.substring(0, 80) + "..." : policy.conditions;
              policyInfo += `\n📋 조건: ${conditionsText}`;
            }
            
            // 링크는 별도로 처리하므로 텍스트에서는 제거
            
            newMessages.push({
              type: "bot",
              text: policyInfo,
              url: policy.url, // 링크 정보를 별도로 저장
              time: formattedTime(new Date())
            });
          });
          
          if (filteredPolicies.length > 5) {
            newMessages.push({
              type: "bot",
              text: `📌 더 많은 정책이 있습니다. 총 ${filteredPolicies.length}건의 정책이 검색되었어요!`,
              time: formattedTime(new Date())
            });
          }
        } else {
          newMessages.push({
            type: "bot",
            text: `😅 죄송해요. ${region} 지역에서 관련된 정책을 찾지 못했습니다. 다른 키워드로 다시 검색해보시겠어요?`,
            time: formattedTime(new Date())
          });
        }
        
        return newMessages;
      });
      
    } catch (error) {
      console.error("정책 검색 실패:", error);
      
      // 오류 메시지로 교체
      setMessages((prev) => {
        const newMessages = [...prev];
        newMessages[newMessages.length - 1] = {
          type: "bot",
          text: "죄송합니다. 정책 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
          time: formattedTime(new Date())
        };
        return newMessages;
      });
    }
  };

  // 정책 검색 시도 함수 (기존 버전 - 호환성을 위해 유지)


  const handleRegionClick = (region) => {
    if (selectedRegion) return;
    setSelectedRegion(region);
    setRegionSelectedAt(new Date());

    const dbRegion = regionMap[region];
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://web-production-a9d2.up.railway.app';
            fetch(`${API_BASE_URL}/api/policies/region/${dbRegion}`)
      .then((res) => res.json())
      .then((data) => {
        if (data.success && Array.isArray(data.policies)) {
          setPolicies(data.policies);
          setFilteredPolicies([]);
          setSelectedAge("");
          setShowDetails(false);
        }
      })
      .catch((err) => console.error("API 호출 실패:", err));

    setTimeout(() => setShowUserMessage(true), 300);
    setTimeout(() => {
      setShowAgePrompt(true);
      setShowAgeDropdown(true);
      setAgeDropdownAt(new Date());
    }, 600);
  };

  const handleAgeChange = (e) => {
    const age = e.target.value;
    setSelectedAge(age);
    setShowDetails(false);
    if (!age) {
      setFilteredPolicies([]);
      return;
    }

    const filtered = policies.filter((p) => {
      if (!p.age_range || p.age_range.length === 0) return true;
      return p.age_range.includes(Number(age));
    });

    setFilteredPolicies(filtered);
  };

  const toggleDetails = () => setShowDetails((prev) => !prev);

  const handleBackToIntro = () => {
    setShowIntro(true);
    setDirectChatMode(false);
    setMessages([]);
    setShowRegionPrompt(false);
    setSelectedRegion("");
    setShowUserMessage(false);
    setShowAgePrompt(false);
    setShowAgeDropdown(false);
    setSelectedAge("");
    setPolicies([]);
    setFilteredPolicies([]);
    setRegionSelectedAt(null);
    setAgeDropdownAt(null);
    setShowDetails(false);
  };

  // 인트로 화면
  if (showIntro) {
    return (
      <div className="intro-container">
        <div className="intro-content">
          <div className="intro-icon">
            <img src="/images/IMG_2682.png" alt="chatbot" className="intro-icon-img" />
          </div>
          <p className="intro-text">
            만나서 반가워요! <br />
            저는 <span className="bold">20대를 위한</span> <br />
            지원금/주거정책 안내 <br />
            챗봇 서비스입니다.
          </p>
          <button className="intro-button" onClick={() => setShowIntro(false)}>
            간편 찾기
          </button>
          <button
            className="intro-button"
            onClick={() => {
              setDirectChatMode(true);
              setShowIntro(false);
              setMessages([
                {
                  type: "bot",
                  text: (
                    <>
                      안녕하세요 고객님! <br />
                      지원금이나 주거정책 관련 궁금한 점 있으시면 <br />
                      편하게 말씀해 주세요.
                    </>
                  ),
                  time: formattedTime(new Date()),
                },
              ]);
            }}
          >
            챗봇과 직접 대화하기
          </button>
        </div>
      </div>
    );
  }

  // 직접 대화하기
  if (directChatMode) {
    return (
      <div className="chat-container">
        <header className="header">
          <button className="back-button" onClick={handleBackToIntro}>
            ←
          </button>
          <span className="title">chatbot</span>
        </header>
        <main className="chat-body">
          <p className="date-label">{formattedDate(currentDate)}</p>
          <p className="highlight">
            당신을 위한 지원금,
            <br />
            놓치지 마세요!
          </p>
          {messages.map((msg, index) =>
            msg.type === "bot" ? (
              <BotMessage
                key={index}
                profileSrc="/images/generated-image (3).png"
                time={msg.time}
              >
                {msg.url ? (
                  <div>
                    {msg.text.split('🔗 ')[0]}
                    <br />
                    <a 
                      href={msg.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      style={{
                        color: "#007bff",
                        textDecoration: "underline",
                        cursor: "pointer",
                        fontSize: "12px"
                      }}
                    >
                      🔗 상세보기
                    </a>
                  </div>
                ) : (
                  msg.text
                )}
              </BotMessage>
            ) : (
              <UserMessage key={index} time={msg.time}>
                {msg.text}
              </UserMessage>
            )
          )}
        </main>
        <footer className="input-area">
          <input
            type="text"
            placeholder="메세지를 입력해주세요."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
          />
          <button className="send-button" onClick={handleSendMessage}>
            ↑
          </button>
        </footer>
      </div>
    );
  }

  // 간편 찾기 모드
  return (
    <div className="chat-container">
      <header className="header">
        <button className="back-button" onClick={handleBackToIntro}>
          ←
        </button>
        <span className="title">chatbot</span>
      </header>

      <main className="chat-body">
        <p className="date-label">{formattedDate(currentDate)}</p>
        <p className="highlight">
          당신을 위한 지원금,
          <br />
          놓치지 마세요!
        </p>

        <BotMessage profileSrc="/images/generated-image (3).png">
          안녕하세요. 고객님! <br />
          지원금 안내 챗봇입니다. <br />
          몇 가지 질문을 답해주시면 <br />
          받을 수 있는 모든 지원금을 찾아드릴게요 :)
        </BotMessage>

        {showRegionPrompt && (
          <>
            <div className="chat-message bot">
              <div className="region-question-bubble">
                먼저, 현재 거주하시는 지역을 선택해주세요.
              </div>
            </div>
            <div className="button-grid">
              {Object.keys(regionMap).map((region) => (
                <button
                  key={region}
                  onClick={() => handleRegionClick(region)}
                  disabled={!!selectedRegion}
                  className={selectedRegion === region ? "selected" : ""}
                >
                  {region}
                </button>
              ))}
            </div>
            <div
              className="time-label"
              style={{ textAlign: "left", marginLeft: "60px", marginTop: "3px" }}
            >
              {formattedTime(new Date())}
            </div>
          </>
        )}

        {showUserMessage && selectedRegion && (
          <UserMessage time={regionSelectedAt ? formattedTime(regionSelectedAt) : ""}>
            {selectedRegion}
          </UserMessage>
        )}

        {showAgePrompt && (
          <BotMessage profileSrc="/images/generated-image (3).png">
            좋아요! 이제 나이를 선택해주세요. <br />
            <span className="sub-text">(아래 옵션에서 선택)</span>
          </BotMessage>
        )}

        {showAgeDropdown && (
          <>
            {!ageDropdownExpanded ? (
              <div
                className="chat-message bot age-dropdown-bubble no-logo"
                style={{ cursor: "pointer" }}
                onClick={() => setAgeDropdownExpanded(true)}
              >
                <div className="message-text">
                  {selectedAge ? `${selectedAge}세` : "[ 20~29 ▼ ]"}
                </div>
              </div>
            ) : (
              <div className="chat-message bot age-dropdown-bubble no-logo">
                <div className="message-text">
                  <select
                    className="age-dropdown"
                    value={selectedAge}
                    onChange={(e) => {
                      handleAgeChange(e);
                      setAgeDropdownExpanded(false);
                    }}
                    size={5}
                  >
                    <option value="">[ 20~29 ▼ ]</option>
                    {Array.from({ length: 10 }, (_, i) => 20 + i).map((age) => (
                      <option key={age} value={age}>
                        {age}세
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}
            {!selectedAge && (
              <div
                className="time-label"
                style={{ textAlign: "left", marginLeft: "60px", marginTop: "4px" }}
              >
                {ageDropdownAt ? formattedTime(ageDropdownAt) : ""}
              </div>
            )}
          </>
        )}

        {/* 정책 요약 + 상세 펼치기 */}
        {filteredPolicies.length > 0 && (
          <>
            <PoliciesSummary
              count={filteredPolicies.length}
              onToggle={toggleDetails}
              isOpen={showDetails}
            />
            {showDetails &&
              filteredPolicies.map((p) => (
                <BotMessageNoLogo key={p.id}>
                  <div style={{ marginBottom: "8px" }}>
                    <a
                      href={p.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        color: "#007bff",
                        textDecoration: "underline",
                        cursor: "pointer",
                        fontWeight: "bold",
                        fontSize: "14px"
                      }}
                    >
                      📋 {p.title}
                    </a>
                  </div>
                  

                  
                  {p.application_period && (
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                      <span style={{ fontWeight: "bold" }}>📅 신청기간:</span> {p.application_period}
                    </div>
                  )}
                  
                  {p.benefits && (
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                      <span style={{ fontWeight: "bold" }}>💰 혜택:</span> {p.benefits.length > 100 ? p.benefits.substring(0, 100) + "..." : p.benefits}
                    </div>
                  )}
                  
                  {p.conditions && (
                    <div style={{ fontSize: "12px", color: "#666", marginBottom: "4px" }}>
                      <span style={{ fontWeight: "bold" }}>📋 조건:</span> {p.conditions.length > 80 ? p.conditions.substring(0, 80) + "..." : p.conditions}
                    </div>
                  )}
                  
                  <div style={{ 
                    borderTop: "1px solid #eee", 
                    marginTop: "8px", 
                    paddingTop: "4px",
                    fontSize: "11px",
                    color: "#999"
                  }}>
                    🔗 클릭하면 상세 정보를 확인할 수 있어요!
                  </div>
                </BotMessageNoLogo>
              ))}
          </>
        )}
      </main>

      <footer className="input-area">
        <input 
          type="text" 
          placeholder="메세지를 입력해주세요."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
        />
        <button className="send-button" onClick={handleSendMessage}>↑</button>
      </footer>
    </div>
  );
}

export default App;
