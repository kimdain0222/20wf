import React, { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedRegion, setSelectedRegion] = useState(""); // 선택한 지역 저장
  const [messages, setMessages] = useState([]); // 대화 내용

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentDate(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  const formattedDate = `${currentDate.getFullYear()}.${String(
    currentDate.getMonth() + 1
  ).padStart(2, "0")}.${String(currentDate.getDate()).padStart(2, "0")} (${currentDate.toLocaleDateString(
    "ko-KR",
    { weekday: "short" }
  )})`;

  const handleRegionClick = (region) => {
    if (selectedRegion) return; // 이미 선택했으면 실행 안 함

    setSelectedRegion(region);

    // 사용자 말풍선 + 챗봇 말풍선 추가
    setMessages((prev) => [
      ...prev,
      { type: "user", text: region },
      { type: "bot", text: "좋아요! 이제 나이를 선택해주세요." }
    ]);
  };

  return (
    <div className="chat-container">
      {/* 상단 헤더 */}
      <header className="header">
        <button className="back-button">←</button>
        <span className="title">chatbot</span>
      </header>

      {/* 채팅 내용 */}
      <main className="chat-body">
        {/* 날짜/요일 표시 */}
        <p className="date-label">{formattedDate}</p>

        {/* highlight는 날짜 바로 아래 */}
        <p className="highlight">
          당신을 위한 지원금,
          <br />
          놓치지 마세요!
        </p>

        {/* 기존 봇 인트로 */}
        <div className="chat-message bot">
          <img
            className="profile-img"
            src="프로필이미지경로" // 여기에 이미지 경로 넣기
            alt="profile"
          />
          <div className="message-text">
            안녕하세요. 고객님! <br />
            지원금 안내 챗봇입니다. <br />
            몇 가지 질문을 답해주시면 <br />받을 수 있는 모든 지원금을 찾아드릴게요 :)
          </div>
        </div>

        {/* 질문 */}
        <p className="question">먼저, 현재 거주하시는 지역을 선택해주세요.</p>

        {/* 버튼 */}
        <div className="button-grid">
          {["서울", "인천", "경기"].map((region) => (
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

        {/* 선택 후 대화 출력 */}
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.type}`}>
            <div className="message-text">{msg.text}</div>
          </div>
        ))}
      </main>

      {/* 입력창 */}
      <footer className="input-area">
        <input type="text" placeholder="메세지를 입력해주세요." />
        <button className="send-button">↑</button>
      </footer>
    </div>
  );
}

export default App;
