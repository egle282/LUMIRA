import { createPortal } from 'react-dom';
import { Info, X } from 'lucide-react';
import { useLanguage } from '../i18n';

interface InfoModalProps {
  onClose: () => void;
}

export function InfoModal({ onClose }: InfoModalProps) {
  const { language } = useLanguage();

  const modalContent = (
    <div style={{
      position: 'fixed',
      top: 0, left: 0, right: 0, bottom: 0,
      background: 'rgba(0, 0, 0, 0.7)',
      backdropFilter: 'blur(5px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 1000
    }}>
      <div className="glass-panel" style={{
        maxWidth: '700px',
        width: '90%',
        padding: '2.5rem',
        position: 'relative',
        maxHeight: '85vh',
        overflowY: 'auto'
      }}>
        <button 
          onClick={onClose}
          style={{
            position: 'absolute', top: '1.5rem', right: '1.5rem',
            background: 'none', border: 'none', color: 'var(--text-muted)',
            cursor: 'pointer'
          }}
        >
          <X size={24} />
        </button>
        
        <h2 className="text-gradient" style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1.5rem' }}>
          <Info size={28} color="var(--accent-gold)" />
          {language === 'ru' ? 'О проекте LUMIRA' : 'About LUMIRA'}
        </h2>

        {language === 'ru' ? (
          <div style={{ color: 'var(--text-main)', lineHeight: '1.7', fontSize: '1.05rem', display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
            <p>
              <strong>LUMIRA</strong> — это первый по-настоящему детерминированный ИИ-ведический астролог, созданный для тех, кто ищет максимальную точность.
            </p>
            
            <h3 style={{ color: 'var(--accent-gold)', marginTop: '0.5rem' }}>Как это работает?</h3>
            <p>
              В отличие от развлекательных приложений, которые придумывают гороскопы или используют "гадания" через API, LUMIRA использует встроенный астрономический движок <strong>Swiss Ephemeris</strong> (Швейцарские эфемериды). 
              Это математический стандарт, который используется в NASA и профессиональных программах (таких как Jagannatha Hora). 
              Наш сервер <i>локально и математически</i> вычисляет положение каждой планеты с точностью до долей секунд дуги (Джйотиш, Айанамша Лахири).
            </p>

            <h3 style={{ color: 'var(--accent-gold)', marginTop: '0.5rem' }}>Уникальные преимущества</h3>
            <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              <li><strong>Никаких выдумок:</strong> Нейросеть (LLM) не придумывает транзиты. Она лишь <i>интерпретирует</i> сухие и точные математические данные, которые ей передает наше ядро.</li>
              <li><strong>Полная независимость:</strong> Математика считается на нашем сервере, а интерпретация происходит через передовые закрытые ИИ-модели, обеспечивая беспрецедентный уровень анализа вашей карты 24/7.</li>
              <li><strong>Конфиденциальность:</strong> Ваши натальные данные надежно защищены и используются исключительно для генерации персонализированных отчетов.</li>
            </ul>

            <h3 style={{ color: 'var(--accent-gold)', marginTop: '0.5rem' }}>Для чего это нужно?</h3>
            <p>
              Вы получаете не просто гороскоп на день, а персональную стратегию (Мухурту), разбор ключевых транзитов и глубокое понимание своей Матрицы Судьбы с помощью инструмента, который никогда не устает и всегда беспристрастен.
            </p>
          </div>
        ) : (
          <div style={{ color: 'var(--text-main)', lineHeight: '1.7', fontSize: '1.05rem', display: 'flex', flexDirection: 'column', gap: '1.2rem' }}>
            <p>
              <strong>LUMIRA</strong> is the first truly deterministic AI Vedic Astrologer, built for those who seek maximum accuracy.
            </p>
            
            <h3 style={{ color: 'var(--accent-gold)', marginTop: '0.5rem' }}>How does it work?</h3>
            <p>
              Unlike entertainment apps that invent horoscopes or use API guessing, LUMIRA utilizes the embedded astronomical engine <strong>Swiss Ephemeris</strong>. 
              This is the mathematical standard used by NASA and professional software (like Jagannatha Hora). 
              Our server <i>locally and mathematically</i> calculates the position of every planet down to the arcsecond (Jyotish, Lahiri Ayanamsa).
            </p>

            <h3 style={{ color: 'var(--accent-gold)', marginTop: '0.5rem' }}>Unique Advantages</h3>
            <ul style={{ paddingLeft: '1.5rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '0.8rem' }}>
              <li><strong>No Hallucinations:</strong> The AI (LLM) does not invent transits. It only <i>interprets</i> the dry, precise mathematical data provided by our core.</li>
              <li><strong>Complete Independence:</strong> Math is calculated on our server, and interpretation is handled by advanced AI models, providing an unprecedented level of chart analysis 24/7.</li>
              <li><strong>Privacy:</strong> Your natal data is securely protected and used exclusively to generate personalized reports.</li>
            </ul>

            <h3 style={{ color: 'var(--accent-gold)', marginTop: '0.5rem' }}>Why use LUMIRA?</h3>
            <p>
              You receive not just a daily horoscope, but a personal strategy (Muhurta), breakdown of key transits, and a deep understanding of your Destiny Matrix using a tool that never tires and is always impartial.
            </p>
          </div>
        )}
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
}
