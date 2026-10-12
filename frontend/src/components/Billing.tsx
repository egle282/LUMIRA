import { getApiBaseUrl } from "../api";
import { useState, useEffect } from 'react';
import { useLanguage } from '../i18n';

export function Billing() {
  const { t } = useLanguage();
  const [status, setStatus] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const token = localStorage.getItem('token');

  useEffect(() => {
    fetch(`${getApiBaseUrl()}/api/billing/status`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        setStatus(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [token]);

  const handleUpgrade = (plan: string) => {
    fetch(`${getApiBaseUrl()}/api/billing/upgrade?plan_name=${plan}`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setStatus({ ...status, plan_name: plan });
          alert(data.message);
        }
      });
  };

  if (loading) return <div style={{ color: 'var(--text-light)' }}>Loading billing status...</div>;

  return (
    <div className="glass-panel" style={{ padding: '2rem', borderRadius: '12px' }}>
      <h2 style={{ color: 'var(--accent-gold)', marginBottom: '1rem' }}>{t('billing.title')}</h2>
      <div style={{ marginBottom: '2rem' }}>
        <p>{t('billing.current')} <strong style={{ color: 'var(--accent-gold)', textTransform: 'uppercase' }}>{status?.plan_name === 'free' ? t('billing.free') : status?.plan_name || t('billing.free')}</strong></p>
        <p>{t('billing.status')} {status?.status}</p>
      </div>

      <p role="status" style={{ color: 'var(--text-muted)' }}>Платёжные провайдеры ещё не подключены. Платный тариф нельзя активировать из интерфейса; это предотвращает фиктивное списание и выдачу платного доступа без подтверждения оплаты.</p>\n      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center', borderRadius: '8px' }}>
          <h3>PRO PLAN</h3>
          <p style={{ margin: '1rem 0' }}>{t('billing.pro_desc')}</p>
          <p style={{ fontSize: '1.5rem', color: 'var(--accent-gold)', marginBottom: '1rem' }}>$9.99 / mo</p>
          <button 
            className="btn-primary" 
            style={{ width: '100%' }}
            onClick={() => handleUpgrade('pro')}
            disabled
          >
            Оплата пока недоступна
          </button>
        </div>

        <div className="glass-panel" style={{ padding: '1.5rem', textAlign: 'center', borderRadius: '8px', border: '1px solid var(--accent-gold)' }}>
          <h3>PREMIUM PLAN</h3>
          <p style={{ margin: '1rem 0' }}>{t('billing.premium_desc')}</p>
          <p style={{ fontSize: '1.5rem', color: 'var(--accent-gold)', marginBottom: '1rem' }}>$24.99 / mo</p>
          <button 
            className="btn-primary" 
            style={{ width: '100%' }}
            onClick={() => handleUpgrade('premium')}
            disabled
          >
            Оплата пока недоступна
          </button>
        </div>
      </div>
    </div>
  );
}
