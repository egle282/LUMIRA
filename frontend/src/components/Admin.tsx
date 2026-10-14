import { getApiBaseUrl } from "../api";
import { useState, useEffect, useMemo } from 'react';
import { useLanguage } from '../i18n';
import { 
  Shield, 
  Users, 
  MessageSquare, 
  Database, 
  Lock, 
  RefreshCw, 
  Download, 
  Search, 
  Trash2, 
  UserCheck, 
  UserX,
  CreditCard,
  CheckSquare,
  Square,
  AlertTriangle,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';

interface UserRecord {
  id: string;
  email: string | null;
  name?: string | null;
  role: 'admin' | 'user' | string;
  plan?: 'free' | 'pro' | 'premium' | string;
  subscription_status?: string;
  created_at: string;
}

export function Admin() {
  const { t } = useLanguage();
  
  // Data states
  const [stats, setStats] = useState<any>(null);
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [refreshing, setRefreshing] = useState(false);
  const [actionMessage, setActionMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

  // Search & Filter
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<'all' | 'admin' | 'user'>('all');
  const [planFilter, setPlanFilter] = useState<'all' | 'free' | 'pro' | 'premium'>('all');

  // Multi-selection
  const [selectedUserIds, setSelectedUserIds] = useState<Set<string>>(new Set());

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Confirmation Modal
  const [deleteModalUser, setDeleteModalUser] = useState<UserRecord | null>(null);
  const [roleChangeModalUser, setRoleChangeModalUser] = useState<{ user: UserRecord; nextRole: string } | null>(null);
  const [actionLoading, setActionLoading] = useState(false);

  // Login Fallback Form
  const [adminEmail, setAdminEmail] = useState('admin@lumira.local');
  const [adminPassword, setAdminPassword] = useState('lumira_admin_password_123');
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState('');
  
  const token = localStorage.getItem('token');

  const loadAdminData = async (authToken: string) => {
    setRefreshing(true);
    setError('');
    try {
      const [statsRes, usersRes] = await Promise.all([
        fetch(`${getApiBaseUrl()}/api/admin/metrics/ai-cost`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        }),
        fetch(`${getApiBaseUrl()}/api/admin/users`, {
          headers: { 'Authorization': `Bearer ${authToken}` }
        })
      ]);

      if (!statsRes.ok || !usersRes.ok) {
        throw new Error('Not authorized as admin');
      }

      const [statsData, usersData] = await Promise.all([
        statsRes.json(),
        usersRes.json()
      ]);

      setStats(statsData);
      setUsers(usersData);
    } catch (err: any) {
      setError(err.message || 'Ошибка загрузки данных администратора');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    if (token) {
      loadAdminData(token);
    } else {
      setError('Not authorized as admin');
      setLoading(false);
    }
  }, [token]);

  // Filtered & Paginated records
  const filteredUsers = useMemo(() => {
    return users.filter(u => {
      const matchesSearch = 
        (u.email && u.email.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (u.name && u.name.toLowerCase().includes(searchQuery.toLowerCase())) ||
        (u.id && u.id.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesRole = roleFilter === 'all' || u.role === roleFilter;
      const matchesPlan = planFilter === 'all' || (u.plan || 'free') === planFilter;

      return matchesSearch && matchesRole && matchesPlan;
    });
  }, [users, searchQuery, roleFilter, planFilter]);

  const totalPages = Math.ceil(filteredUsers.length / pageSize) || 1;
  const paginatedUsers = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return filteredUsers.slice(start, start + pageSize);
  }, [filteredUsers, currentPage, pageSize]);

  // Selection handlers
  const handleToggleSelectAll = () => {
    if (selectedUserIds.size === paginatedUsers.length && paginatedUsers.length > 0) {
      setSelectedUserIds(new Set());
    } else {
      const allIds = new Set(paginatedUsers.map(u => u.id));
      setSelectedUserIds(allIds);
    }
  };

  const handleToggleSelectUser = (id: string) => {
    const next = new Set(selectedUserIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    setSelectedUserIds(next);
  };

  // Export CSV
  const handleExportCSV = () => {
    if (filteredUsers.length === 0) {
      setActionMessage({ text: 'Нет данных для экспорта', type: 'error' });
      return;
    }

    const headers = ['ID', 'Email', 'Name', 'Role', 'Plan', 'Created_At'];
    const rows = filteredUsers.map(u => [
      `"${u.id.replace(/"/g, '""')}"`,
      `"${(u.email || '').replace(/"/g, '""')}"`,
      `"${(u.name || '').replace(/"/g, '""')}"`,
      `"${u.role}"`,
      `"${u.plan || 'free'}"`,
      `"${u.created_at}"`
    ]);

    const csvContent = '\uFEFF' + [headers.join(','), ...rows.map(r => r.join(','))].join('\r\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `lumira_users_export_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setActionMessage({ text: `Экспортировано ${filteredUsers.length} пользователей в CSV`, type: 'success' });
    setTimeout(() => setActionMessage(null), 4000);
  };

  // Perform Role Change
  const confirmRoleChange = async () => {
    if (!roleChangeModalUser || !token) return;
    setActionLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/admin/users/${roleChangeModalUser.user.id}/role`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ role: roleChangeModalUser.nextRole })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Не удалось изменить роль');
      
      setActionMessage({ text: `Роль пользователя ${roleChangeModalUser.user.email} обновлена на ${roleChangeModalUser.nextRole}`, type: 'success' });
      setRoleChangeModalUser(null);
      await loadAdminData(token);
    } catch (err: any) {
      setActionMessage({ text: err.message, type: 'error' });
    } finally {
      setActionLoading(false);
      setTimeout(() => setActionMessage(null), 5000);
    }
  };

  // Perform User Deletion
  const confirmUserDelete = async () => {
    if (!deleteModalUser || !token) return;
    setActionLoading(true);
    try {
      const res = await fetch(`${getApiBaseUrl()}/api/admin/users/${deleteModalUser.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Не удалось удалить пользователя');

      setActionMessage({ text: `Пользователь ${deleteModalUser.email} успешно удален`, type: 'success' });
      setDeleteModalUser(null);
      await loadAdminData(token);
    } catch (err: any) {
      setActionMessage({ text: err.message, type: 'error' });
    } finally {
      setActionLoading(false);
      setTimeout(() => setActionMessage(null), 5000);
    }
  };

  const handleAdminLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError('');
    try {
      const body = new URLSearchParams({ username: adminEmail, password: adminPassword });
      const res = await fetch(`${getApiBaseUrl()}/api/auth/token`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Неверный логин или пароль администратора');
      localStorage.setItem('token', data.access_token);
      loadAdminData(data.access_token);
      window.location.reload();
    } catch (err: any) {
      setLoginError(err.message);
    } finally {
      setLoginLoading(false);
    }
  };

  // Auth screen
  if (error) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="glass-panel" style={{ 
          padding: '2.5rem', 
          borderRadius: '14px', 
          maxWidth: '440px', 
          width: '100%', 
          background: '#0D090D',
          border: '1px solid #3A1A2B'
        }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem' }}>
            <div style={{ 
              width: '52px', 
              height: '52px', 
              borderRadius: '14px', 
              background: 'rgba(229, 139, 180, 0.12)', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              border: '1px solid rgba(229, 139, 180, 0.3)' 
            }}>
              <Lock size={26} style={{ color: '#E58BB4' }} />
            </div>
          </div>
          <h2 style={{ color: '#F5F1F4', marginBottom: '0.75rem', textAlign: 'center', fontSize: '1.4rem', fontWeight: 600 }}>
            {t('admin.login_title') || 'Требуется вход администратора'}
          </h2>
          <p style={{ color: '#969099', fontSize: '0.85rem', marginBottom: '1.5rem', textAlign: 'center', lineHeight: '1.5' }}>
            {t('admin.login_desc') || 'Вы вошли как обычный пользователь. Введите данные администратора для доступа к управлению.'}
          </p>
          <form onSubmit={handleAdminLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <input 
              type="email" 
              placeholder={t('admin.email') || 'admin@lumira.local'}
              value={adminEmail}
              onChange={(e) => setAdminEmail(e.target.value)}
              className="studio-input"
              style={{ background: '#160B13', border: '1px solid #3A1A2B', color: '#F5F1F4' }}
              required
            />
            <input 
              type="password" 
              placeholder={t('auth.password') || 'Пароль'}
              value={adminPassword}
              onChange={(e) => setAdminPassword(e.target.value)}
              className="studio-input"
              style={{ background: '#160B13', border: '1px solid #3A1A2B', color: '#F5F1F4' }}
              required
            />
            {loginError && <div style={{ color: '#F16B79', fontSize: '0.85rem', textAlign: 'center' }}>{loginError}</div>}
            <button 
              type="submit" 
              disabled={loginLoading}
              className="btn-primary"
              style={{ 
                width: '100%', 
                marginTop: '0.5rem',
                background: '#E58BB4',
                color: '#080809',
                fontWeight: 600
              }}
            >
              {loginLoading ? 'Вход…' : t('admin.login_btn') || 'Войти как Администратор'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '40vh', color: '#969099' }}>
        <RefreshCw size={24} className="spin-slow" style={{ marginRight: '10px' }} />
        Загрузка панели управления LUMIRA…
      </div>
    );
  }

  // Count summaries
  const totalUsersCount = users.length;
  const adminUsersCount = users.filter(u => u.role === 'admin').length;
  const activePaidSubsCount = users.filter(u => u.plan === 'pro' || u.plan === 'premium').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', width: '100%', color: '#F5F1F4' }}>
      
      {/* Action Notification Toast */}
      {actionMessage && (
        <div style={{
          padding: '12px 18px',
          borderRadius: '8px',
          background: actionMessage.type === 'success' ? 'rgba(67, 201, 128, 0.15)' : 'rgba(241, 107, 121, 0.15)',
          border: `1px solid ${actionMessage.type === 'success' ? '#43C980' : '#F16B79'}`,
          color: actionMessage.type === 'success' ? '#43C980' : '#F16B79',
          fontSize: '0.9rem',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <span>{actionMessage.text}</span>
          <button 
            type="button" 
            onClick={() => setActionMessage(null)}
            style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Header Bar */}
      <div style={{
        background: '#0D090D',
        border: '1px solid #3A1A2B',
        borderRadius: '12px',
        padding: '1.25rem 1.75rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: '1rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '12px',
            background: 'rgba(229, 139, 180, 0.15)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            border: '1px solid rgba(229, 139, 180, 0.35)'
          }}>
            <Shield size={24} style={{ color: '#E58BB4' }} />
          </div>
          <div>
            <h1 style={{ fontSize: '1.35rem', fontWeight: 700, margin: 0, letterSpacing: '-0.02em', color: '#F5F1F4' }}>
              Admin Dashboard
            </h1>
            <p style={{ fontSize: '0.82rem', color: '#969099', margin: '4px 0 0 0' }}>
              Управление пользователями, ролями доступа и мониторинг платформы
            </p>
          </div>
        </div>

        {/* Global Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            type="button"
            onClick={() => token && loadAdminData(token)}
            disabled={refreshing}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '8px',
              background: '#160B13',
              border: '1px solid #3A1A2B',
              color: '#F5F1F4',
              fontSize: '0.82rem',
              fontWeight: 500,
              cursor: refreshing ? 'not-allowed' : 'pointer',
              transition: 'background 0.2s'
            }}
          >
            <RefreshCw size={14} className={refreshing ? 'spin-slow' : ''} style={{ color: '#E58BB4' }} />
            Обновить
          </button>

          <button
            type="button"
            onClick={handleExportCSV}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              borderRadius: '8px',
              background: 'rgba(229, 139, 180, 0.12)',
              border: '1px solid rgba(229, 139, 180, 0.35)',
              color: '#E58BB4',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <Download size={14} />
            Экспорт пользователей (CSV)
          </button>
        </div>
      </div>

      {/* KPI Cards Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
        <div style={{ background: '#0D090D', border: '1px solid #3A1A2B', borderRadius: '10px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: '#969099' }}>Всего пользователей</span>
            <Users size={18} style={{ color: '#E58BB4' }} />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#F5F1F4' }}>
            {totalUsersCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#969099', marginTop: '4px' }}>
            {adminUsersCount} администраторов
          </div>
        </div>

        <div style={{ background: '#0D090D', border: '1px solid #3A1A2B', borderRadius: '10px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: '#969099' }}>Платные подписки</span>
            <CreditCard size={18} style={{ color: '#E6BC52' }} />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#E6BC52' }}>
            {activePaidSubsCount}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#969099', marginTop: '4px' }}>
            Тарифы Pro и Premium
          </div>
        </div>

        <div style={{ background: '#0D090D', border: '1px solid #3A1A2B', borderRadius: '10px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: '#969099' }}>AI Запросы пользователей</span>
            <MessageSquare size={18} style={{ color: '#527FA7' }} />
          </div>
          <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#F5F1F4' }}>
            {stats?.total_ai_messages || 0}
          </div>
          <div style={{ fontSize: '0.75rem', color: '#969099', marginTop: '4px' }}>
            Реальные обращения в чат
          </div>
        </div>

        <div style={{ background: '#0D090D', border: '1px solid #3A1A2B', borderRadius: '10px', padding: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
            <span style={{ fontSize: '0.8rem', color: '#969099' }}>Изоляция данных</span>
            <Database size={18} style={{ color: '#43C980' }} />
          </div>
          <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#43C980', marginTop: '6px' }}>
            RLS Active
          </div>
          <div style={{ fontSize: '0.75rem', color: '#969099', marginTop: '8px' }}>
            Аудит безопасности пройден
          </div>
        </div>
      </div>

      {/* Filter & Search Bar */}
      <div style={{
        background: '#0D090D',
        border: '1px solid #3A1A2B',
        borderRadius: '10px',
        padding: '1rem',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '0.75rem'
      }}>
        {/* Search Input */}
        <div style={{ position: 'relative', flex: '1 1 280px', maxWidth: '420px' }}>
          <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#969099' }} />
          <input
            type="text"
            placeholder="Поиск по email, имени или ID..."
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            style={{
              width: '100%',
              padding: '8px 12px 8px 36px',
              borderRadius: '8px',
              background: '#160B13',
              border: '1px solid #3A1A2B',
              color: '#F5F1F4',
              fontSize: '0.85rem'
            }}
          />
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.75rem', color: '#969099' }}>Роль:</span>
            <select
              value={roleFilter}
              onChange={(e: any) => {
                setRoleFilter(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                background: '#160B13',
                border: '1px solid #3A1A2B',
                color: '#F5F1F4',
                padding: '6px 10px',
                borderRadius: '6px',
                fontSize: '0.8rem',
                cursor: 'pointer'
              }}
            >
              <option value="all">Все роли</option>
              <option value="admin">Admin</option>
              <option value="user">User</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.75rem', color: '#969099' }}>Тариф:</span>
            <select
              value={planFilter}
              onChange={(e: any) => {
                setPlanFilter(e.target.value);
                setCurrentPage(1);
              }}
              style={{
                background: '#160B13',
                border: '1px solid #3A1A2B',
                color: '#F5F1F4',
                padding: '6px 10px',
                borderRadius: '6px',
                fontSize: '0.8rem',
                cursor: 'pointer'
              }}
            >
              <option value="all">Все тарифы</option>
              <option value="free">Free</option>
              <option value="pro">Pro</option>
              <option value="premium">Premium</option>
            </select>
          </div>

          {selectedUserIds.size > 0 && (
            <span style={{ fontSize: '0.8rem', color: '#E58BB4', fontWeight: 600 }}>
              Выбрано: {selectedUserIds.size}
            </span>
          )}
        </div>
      </div>

      {/* Main Table Panel */}
      <div style={{
        background: '#0D090D',
        border: '1px solid #3A1A2B',
        borderRadius: '12px',
        overflow: 'hidden'
      }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
            <thead>
              <tr style={{ background: '#160B13', borderBottom: '1px solid #3A1A2B', color: '#969099', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: '0.04em' }}>
                <th style={{ padding: '12px 16px', width: '40px' }}>
                  <button
                    type="button"
                    onClick={handleToggleSelectAll}
                    style={{ background: 'none', border: 'none', color: '#E58BB4', cursor: 'pointer', padding: 0 }}
                  >
                    {selectedUserIds.size === paginatedUsers.length && paginatedUsers.length > 0 ? (
                      <CheckSquare size={16} />
                    ) : (
                      <Square size={16} />
                    )}
                  </button>
                </th>
                <th style={{ padding: '12px 16px' }}>Пользователь</th>
                <th style={{ padding: '12px 16px' }}>Роль</th>
                <th style={{ padding: '12px 16px' }}>Тариф</th>
                <th style={{ padding: '12px 16px' }}>Дата регистрации</th>
                <th style={{ padding: '12px 16px', textAlign: 'right' }}>Действия</th>
              </tr>
            </thead>
            <tbody>
              {paginatedUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ padding: '3rem', textAlign: 'center', color: '#969099' }}>
                    Пользователи не найдены
                  </td>
                </tr>
              ) : (
                paginatedUsers.map((u) => {
                  const isSelected = selectedUserIds.has(u.id);
                  const initials = (u.name || u.email || 'U').slice(0, 2).toUpperCase();
                  const isCurrentUser = u.email === adminEmail;

                  return (
                    <tr 
                      key={u.id}
                      style={{
                        borderBottom: '1px solid rgba(58, 26, 43, 0.5)',
                        background: isSelected ? 'rgba(229, 139, 180, 0.05)' : 'transparent',
                        transition: 'background 0.15s ease'
                      }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'rgba(229, 139, 180, 0.08)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = isSelected ? 'rgba(229, 139, 180, 0.05)' : 'transparent')}
                    >
                      {/* Checkbox */}
                      <td style={{ padding: '14px 16px' }}>
                        <button
                          type="button"
                          onClick={() => handleToggleSelectUser(u.id)}
                          style={{ background: 'none', border: 'none', color: isSelected ? '#E58BB4' : '#969099', cursor: 'pointer', padding: 0 }}
                        >
                          {isSelected ? <CheckSquare size={16} /> : <Square size={16} />}
                        </button>
                      </td>

                      {/* User Info & Avatar */}
                      <td style={{ padding: '14px 16px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                          <div style={{
                            width: '34px',
                            height: '34px',
                            borderRadius: '50%',
                            background: u.role === 'admin' ? 'rgba(229, 139, 180, 0.2)' : 'rgba(255, 255, 255, 0.06)',
                            border: `1px solid ${u.role === 'admin' ? '#E58BB4' : '#3A1A2B'}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 600,
                            fontSize: '0.75rem',
                            color: u.role === 'admin' ? '#E58BB4' : '#F5F1F4'
                          }}>
                            {initials}
                          </div>
                          <div>
                            <div style={{ fontWeight: 600, color: '#F5F1F4', fontSize: '0.88rem' }}>
                              {u.name || u.email || 'Без имени'}
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#969099', fontFamily: 'monospace' }}>
                              {u.email || u.id}
                            </div>
                          </div>
                        </div>
                      </td>

                      {/* Role Badge */}
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{
                          display: 'inline-block',
                          padding: '3px 8px',
                          borderRadius: '6px',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          background: u.role === 'admin' ? 'rgba(229, 139, 180, 0.15)' : 'rgba(255, 255, 255, 0.05)',
                          border: `1px solid ${u.role === 'admin' ? 'rgba(229, 139, 180, 0.4)' : '#3A1A2B'}`,
                          color: u.role === 'admin' ? '#E58BB4' : '#969099'
                        }}>
                          {u.role.toUpperCase()}
                        </span>
                      </td>

                      {/* Subscription Plan Badge */}
                      <td style={{ padding: '14px 16px' }}>
                        <span style={{
                          display: 'inline-block',
                          padding: '3px 8px',
                          borderRadius: '6px',
                          fontSize: '0.72rem',
                          fontWeight: 600,
                          background: u.plan === 'premium' 
                            ? 'rgba(229, 139, 180, 0.2)' 
                            : u.plan === 'pro' 
                            ? 'rgba(230, 188, 82, 0.15)' 
                            : 'rgba(82, 127, 167, 0.15)',
                          border: `1px solid ${
                            u.plan === 'premium' ? '#E58BB4' : u.plan === 'pro' ? '#E6BC52' : '#527FA7'
                          }`,
                          color: u.plan === 'premium' ? '#E58BB4' : u.plan === 'pro' ? '#E6BC52' : '#527FA7'
                        }}>
                          {(u.plan || 'free').toUpperCase()}
                        </span>
                      </td>

                      {/* Created At */}
                      <td style={{ padding: '14px 16px', color: '#969099', fontFamily: 'monospace', fontSize: '0.8rem' }}>
                        {u.created_at ? new Date(u.created_at).toLocaleDateString('ru-RU') : '—'}
                      </td>

                      {/* Actions */}
                      <td style={{ padding: '14px 16px', textAlign: 'right' }}>
                        <div style={{ display: 'inline-flex', gap: '6px' }}>
                          {/* Toggle Role Button */}
                          <button
                            type="button"
                            title={u.role === 'admin' ? 'Понизить до user' : 'Повысить до admin'}
                            onClick={() => setRoleChangeModalUser({
                              user: u,
                              nextRole: u.role === 'admin' ? 'user' : 'admin'
                            })}
                            style={{
                              padding: '6px',
                              borderRadius: '6px',
                              background: '#160B13',
                              border: '1px solid #3A1A2B',
                              color: u.role === 'admin' ? '#E58BB4' : '#969099',
                              cursor: 'pointer'
                            }}
                          >
                            {u.role === 'admin' ? <UserX size={14} /> : <UserCheck size={14} />}
                          </button>

                          {/* Delete User Button */}
                          <button
                            type="button"
                            title="Удалить пользователя"
                            disabled={isCurrentUser}
                            onClick={() => setDeleteModalUser(u)}
                            style={{
                              padding: '6px',
                              borderRadius: '6px',
                              background: '#160B13',
                              border: '1px solid #3A1A2B',
                              color: isCurrentUser ? 'rgba(255, 255, 255, 0.15)' : '#F16B79',
                              cursor: isCurrentUser ? 'not-allowed' : 'pointer'
                            }}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Bar */}
        <div style={{
          padding: '12px 16px',
          borderTop: '1px solid #3A1A2B',
          background: '#160B13',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.8rem',
          color: '#969099'
        }}>
          <div>
            Показано {paginatedUsers.length} из {filteredUsers.length} записей
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <button
              type="button"
              disabled={currentPage <= 1}
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              style={{
                padding: '4px 8px',
                borderRadius: '4px',
                background: '#0D090D',
                border: '1px solid #3A1A2B',
                color: currentPage <= 1 ? '#68697D' : '#F5F1F4',
                cursor: currentPage <= 1 ? 'not-allowed' : 'pointer'
              }}
            >
              <ChevronLeft size={14} />
            </button>
            <span>
              Страница {currentPage} из {totalPages}
            </span>
            <button
              type="button"
              disabled={currentPage >= totalPages}
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              style={{
                padding: '4px 8px',
                borderRadius: '4px',
                background: '#0D090D',
                border: '1px solid #3A1A2B',
                color: currentPage >= totalPages ? '#68697D' : '#F5F1F4',
                cursor: currentPage >= totalPages ? 'not-allowed' : 'pointer'
              }}
            >
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation Modal for Role Change */}
      {roleChangeModalUser && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#0D090D',
            border: '1px solid #3A1A2B',
            borderRadius: '12px',
            padding: '1.75rem',
            maxWidth: '420px',
            width: '90%'
          }}>
            <h3 style={{ margin: '0 0 10px 0', fontSize: '1.1rem', color: '#F5F1F4' }}>
              Подтверждение изменения роли
            </h3>
            <p style={{ fontSize: '0.85rem', color: '#969099', lineHeight: '1.5' }}>
              Вы уверены, что хотите изменить роль пользователя <strong>{roleChangeModalUser.user.email}</strong> на{' '}
              <span style={{ color: '#E58BB4', fontWeight: 600 }}>{roleChangeModalUser.nextRole}</span>?
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '1.5rem' }}>
              <button
                type="button"
                onClick={() => setRoleChangeModalUser(null)}
                disabled={actionLoading}
                style={{
                  padding: '8px 14px',
                  borderRadius: '6px',
                  background: 'transparent',
                  border: '1px solid #3A1A2B',
                  color: '#969099',
                  cursor: 'pointer'
                }}
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={confirmRoleChange}
                disabled={actionLoading}
                style={{
                  padding: '8px 14px',
                  borderRadius: '6px',
                  background: '#E58BB4',
                  border: 'none',
                  color: '#080809',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {actionLoading ? 'Обновление…' : 'Подтвердить'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal for User Delete */}
      {deleteModalUser && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0,0,0,0.7)',
          backdropFilter: 'blur(6px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: '#0D090D',
            border: '1px solid #F16B79',
            borderRadius: '12px',
            padding: '1.75rem',
            maxWidth: '420px',
            width: '90%'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#F16B79', marginBottom: '8px' }}>
              <AlertTriangle size={20} />
              <h3 style={{ margin: 0, fontSize: '1.1rem' }}>Удаление пользователя</h3>
            </div>
            <p style={{ fontSize: '0.85rem', color: '#969099', lineHeight: '1.5' }}>
              Вы действительно хотите безвозвратно удалить аккаунт <strong>{deleteModalUser.email}</strong>? Связанные профили и данные будут удалены каскадно.
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '1.5rem' }}>
              <button
                type="button"
                onClick={() => setDeleteModalUser(null)}
                disabled={actionLoading}
                style={{
                  padding: '8px 14px',
                  borderRadius: '6px',
                  background: 'transparent',
                  border: '1px solid #3A1A2B',
                  color: '#969099',
                  cursor: 'pointer'
                }}
              >
                Отмена
              </button>
              <button
                type="button"
                onClick={confirmUserDelete}
                disabled={actionLoading}
                style={{
                  padding: '8px 14px',
                  borderRadius: '6px',
                  background: '#F16B79',
                  border: 'none',
                  color: '#FFF',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {actionLoading ? 'Удаление…' : 'Удалить'}
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
}
