import { getApiBaseUrl } from "../api";
import { useState } from 'react';
import { Send, Info, X } from 'lucide-react';

export function AIChat() {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Намасте. Я LUMIRA. О чем бы вы хотели спросить звезды сегодня?' }
  ]);
  const [input, setInput] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [showInfo, setShowInfo] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userText = input;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    setInput('');
    setIsLoading(true);

    try {
      const token = localStorage.getItem('token');
      const res = await fetch(`${getApiBaseUrl()}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ message: userText })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Не удалось получить ответ AI.');
      setMessages(prev => [...prev, { role: 'assistant', text: data.reply }]);
    } catch (err: any) {
      setMessages(prev => [...prev, { role: 'assistant', text: `Error: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: '1rem', height: 'calc(100vh - 12rem)', position: 'relative' }}>
      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative' }}>
        
        {/* Info Toggle Button */}
        <button 
          onClick={() => setShowInfo(!showInfo)}
          style={{
            position: 'absolute', top: '1rem', right: '1rem', zIndex: 10,
            background: 'rgba(0,0,0,0.5)', border: '1px solid var(--accent-gold)',
            color: 'var(--accent-gold)', borderRadius: '20px', padding: '0.5rem 1rem',
            display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer'
          }}
        >
          <Info size={18} /> Информация
        </button>

        {/* Chat History */}
        <div style={{ flex: 1, padding: '2rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '2rem' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ 
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '70%'
            }}>
              <div style={{ 
                background: msg.role === 'user' ? 'rgba(212, 175, 55, 0.15)' : 'rgba(0,0,0,0.4)',
                border: msg.role === 'user' ? '1px solid rgba(212, 175, 55, 0.3)' : '1px solid var(--border-color)',
                padding: '1rem 1.5rem',
                borderRadius: msg.role === 'user' ? '20px 20px 0 20px' : '20px 20px 20px 0',
                lineHeight: '1.5'
              }}>
                {msg.text}
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '0.5rem', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                {msg.role === 'user' ? 'You' : 'LUMIRA'}
              </div>
            </div>
          ))}
        </div>

        {/* Input Area */}
        <div style={{ padding: '1.5rem', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '1rem' }}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Спросите о карьере, отношениях или текущих транзитах..."
            style={{ 
              flex: 1, padding: '1rem 1.5rem', borderRadius: '30px', 
              background: 'rgba(0,0,0,0.5)', border: '1px solid var(--border-color)',
              color: 'white', outline: 'none', fontSize: '1rem'
            }}
          />
          <button 
            onClick={handleSend}
            className="glow-hover"
            style={{ 
              width: '56px', height: '56px', borderRadius: '50%', 
              background: 'var(--accent-gold)', color: 'black', 
              border: 'none', cursor: 'pointer', display: 'flex', 
              alignItems: 'center', justifyContent: 'center'
            }}
          >
            <Send size={24} />
          </button>
        </div>
      </div>

      {/* Info Panel - Right Zone */}
      {showInfo && (
        <div className="glass-panel" style={{ 
          width: '350px', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem',
          animation: 'fadeInRight 0.3s ease-out'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ color: 'var(--accent-gold)' }}>О Проекте LUMIRA</h3>
            <button onClick={() => setShowInfo(false)} style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}><X size={20} /></button>
          </div>
          
          <div style={{ color: 'var(--text-muted)', fontSize: '0.95rem', lineHeight: '1.6', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <p>
              <strong style={{ color: 'white' }}>LUMIRA</strong> — это первый ИИ-Астролог, объединяющий 
              детерминированную ведическую астрологию (Джйотиш) и современные нейросети.
            </p>
            <p>
              <strong style={{ color: 'white' }}>В чём уникальность?</strong><br/>
              Обычные чат-боты придумывают положения звезд (галлюцинируют). 
              LUMIRA использует профессиональный астрономический движок <em>Swiss Ephemeris</em> для точного расчета 
              Вашей натальной карты, транзитов и Панчанги (лунного календаря), а ИИ выступает лишь 
              в роли мудрого интерпретатора.
            </p>
            <p>
              <strong style={{ color: 'white' }}>Как это работает:</strong>
              <ul style={{ paddingLeft: '1.2rem', marginTop: '0.5rem' }}>
                <li>Движок рассчитывает планеты на основе Вашего профиля.</li>
                <li>Данные передаются в нейросеть.</li>
                <li>Вы получаете глубокие, персональные и точные рекомендации.</li>
              </ul>
            </p>
            <p>
              <strong style={{ color: 'white' }}>Выгода для пользователя:</strong><br/>
              Вы получаете персонального астролога, доступного 24/7, который знает Ваш гороскоп 
              и дает советы, опираясь на реальное положение звезд в данный момент времени.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
