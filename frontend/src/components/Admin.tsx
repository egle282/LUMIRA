import { getApiBaseUrl } from "../api";
import { useState, useEffect } from 'react';
import { useLanguage } from '../i18n';

export function Admin() {
  const { t } = useLanguage();
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const token = localStorage.getItem('token');

  useEffect(() => {
    // Fetch stats
    fetch(`${getApiBaseUrl()}/api/admin/metrics/ai-cost`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => {
        if (!res.ok) throw new Error('Not authorized as admin');
        return res.json();
      })
      .then(data => setStats(data))
      .catch(err => setError(err.message));

    // Fetch users
    fetch(`${getApiBaseUrl()}/api/admin/users`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
      .then(res => {
        if (res.ok) return res.json();
        return [];
      })
      .then(data => {
        setUsers(data);
        setLoading(false);
      });
  }, [token]);

  if (error) return <div style={{ color: 'red', padding: '2rem' }}>{error}</div>;
  if (loading) return <div style={{ color: 'var(--text-light)' }}>Loading admin panel...</div>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <div className="glass-panel" style={{ padding: '2rem', borderRadius: '12px' }}>
        <h2 style={{ color: 'var(--accent-gold)', marginBottom: '1rem' }}>{t('admin.title')}</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
            <p style={{ color: 'var(--text-muted)' }}>{t('admin.tokens')}</p>
            <h3 style={{ fontSize: '2rem', color: 'var(--accent-gold)' }}>{stats?.total_ai_messages || 0}</h3>
          </div>
          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.05)', borderRadius: '8px' }}>
            <p style={{ color: 'var(--text-muted)' }}>{t('admin.cost')}</p>
            <h3 style={{ fontSize: '2rem', color: 'var(--accent-gold)' }}>{stats?.token_usage_tracking ? `${stats.estimated_cost_usd}` : t('admin.cost_unavailable')}</h3>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: '2rem', borderRadius: '12px' }}>
        <h2 style={{ color: 'var(--accent-gold)', marginBottom: '1rem' }}>{t('admin.users')}</h2>
        <table style={{ width: '100%', textAlign: 'left', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
              <th style={{ padding: '1rem 0' }}>{t('admin.email')}</th>
              <th style={{ padding: '1rem 0' }}>{t('admin.role')}</th>
              <th style={{ padding: '1rem 0' }}>{t('admin.joined')}</th>
            </tr>
          </thead>
          <tbody>
            {users.map((u: any) => (
              <tr key={u.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                <td style={{ padding: '1rem 0' }}>{u.email || 'N/A'}</td>
                <td style={{ padding: '1rem 0' }}>{u.role}</td>
                <td style={{ padding: '1rem 0' }}>{new Date(u.created_at).toLocaleDateString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
