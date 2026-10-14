import { getApiBaseUrl } from "../api";
import { useState } from 'react';
import { Send, Info, X, Sparkles } from 'lucide-react';
import { useLanguage } from '../i18n';

export function AIChat() {
  const { t, language } = useLanguage();
  const [messages, setMessages] = useState([
    { role: 'assistant', text: t('chat.initial') }
  ]);
  const [input, setInput] = useState('');

  const [isLoading, setIsLoading] = useState(false);
  const [showInfo, setShowInfo] = useState(false);

  const quickPrompts = [
    'Каково влияние текущих транзитов на карьеру?',
    'Благоприятен ли этот месяц для финансовых начинаний?',
    'Какие сильные стороны раскрывает моя натальная карта?'
  ];

  const handleSend = async (textToSend?: string) => {
    const userText = (textToSend || input).trim();
    if (!userText || isLoading) return;
    setMessages(prev => [...prev, { role: 'user', text: userText }]);
    if (!textToSend) setInput('');
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
      setMessages(prev => [...prev, { role: 'assistant', text: `Ошибка: ${err.message}` }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', gap: '1rem', height: 'calc(100vh - 11rem)', position: 'relative' }}>
      <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
        
        {/* Chat Header Bar */}
        <div style={{
          padding: '1rem 1.5rem',
          borderBottom: '1px solid var(--border-card)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          background: 'var(--bg-card-secondary)'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{ width: '32px', height: '32px', borderRadius: '8px', background: 'rgba(221, 186, 72, 0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Sparkles size={16} style={{ color: 'var(--accent-gold)' }} />
            </div>
            <div>
              <span style={{ fontWeight: 600, fontSize: '0.95rem' }}>LUMIRA AI Astrologer</span>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                Интерпретатор натальной карты и транзитов
              </div>
            </div>
          </div>

          <button 
            onClick={() => setShowInfo(!showInfo)}
            style={{
              background: 'transparent',
              border: '1px solid var(--border-card)',
              color: 'var(--text-secondary)',
              borderRadius: '6px',
              padding: '6px 12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer',
              fontSize: '0.8rem'
            }}
          >
            <Info size={15} /> {t('chat.info_btn')}
          </button>
        </div>

        {/* Chat History */}
        <div style={{ flex: 1, padding: '1.5rem', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {messages.map((msg, i) => (
            <div key={i} style={{ 
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '75%'
            }}>
              <div style={{ 
                background: msg.role === 'user' ? 'rgba(221, 186, 72, 0.15)' : 'var(--bg-card-secondary)',
                border: msg.role === 'user' ? '1px solid rgba(221, 186, 72, 0.35)' : '1px solid var(--border-card)',
                color: 'var(--text-main)',
                padding: '1rem 1.25rem',
                borderRadius: msg.role === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                lineHeight: '1.6',
                fontSize: '0.92rem',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.text}
              </div>
              <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                {msg.role === 'user' ? t('chat.you') : 'LUMIRA'}
              </div>
            </div>
          ))}

          {isLoading && (
            <div style={{ alignSelf: 'flex-start', color: 'var(--text-secondary)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ animation: 'pulseGlow 1.5s infinite' }}>●</span> Составление астрологического ответа…
            </div>
          )}
        </div>

        {/* Quick Prompts Bar */}
        <div style={{ padding: '0.5rem 1.5rem', display: 'flex', gap: '8px', overflowX: 'auto', borderTop: '1px solid var(--border-card)' }}>
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p)}
              disabled={isLoading}
              style={{
                background: 'var(--bg-card-secondary)',
                border: '1px solid var(--border-card)',
                color: 'var(--text-secondary)',
                padding: '4px 10px',
                borderRadius: '6px',
                fontSize: '0.75rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--text-main)'; e.currentTarget.style.borderColor = 'var(--accent-gold)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--text-secondary)'; e.currentTarget.style.borderColor = 'var(--border-card)'; }}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Input Area */}
        <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid var(--border-card)', display: 'flex', gap: '0.75rem', background: 'var(--bg-card-secondary)' }}>
          <input 
            type="text" 
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder={t('chat.placeholder')}
            className="studio-input"
            disabled={isLoading}
          />
          <button 
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="btn-primary"
            style={{ padding: '10px 18px', flexShrink: 0 }}
          >
            <Send size={18} />
          </button>
        </div>
      </div>

      {/* Info Panel - Right Zone */}
      {showInfo && (
        <div className="glass-panel" style={{ 
          width: '320px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem',
          animation: 'fadeInRight 0.25s ease-out',
          background: 'var(--bg-card)'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ color: 'var(--accent-gold)', fontSize: '1rem', fontWeight: 600 }}>
              {language === 'ru' ? 'О Проекте LUMIRA' : 'About LUMIRA'}
            </h3>
            <button onClick={() => setShowInfo(false)} style={{ background: 'none', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
              <X size={18} />
            </button>
          </div>
          
          <div style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', lineHeight: '1.5', display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            <p>
              <strong style={{ color: 'var(--text-main)' }}>LUMIRA</strong> объединяет детерминированную ведическую астрологию (Джйотиш) и современные языковые модели.
            </p>
            <p>
              В отличие от универсальных нейросетей, LUMIRA не придумывает координаты светил: швейцарские эфемериды <em>Swiss Ephemeris</em> гарантируют астрономическую точность всех положений.
            </p>
            <div style={{ borderTop: '1px solid var(--border-card)', paddingTop: '0.75rem', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Контекст натальной карты передаётся в модель автоматически.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
