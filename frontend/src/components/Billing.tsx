import { getApiBaseUrl } from "../api";
import { useState, useEffect } from "react";
import { useLanguage } from "../i18n";
import { Check, Sparkles, Shield, Zap } from "lucide-react";

type BillingStatus = {
  plan_name: string;
  status: string;
  current_period_end?: string | null;
};

export function Billing() {
  const { t } = useLanguage();
  const [status, setStatus] = useState<BillingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [checkoutLoading, setCheckoutLoading] = useState("");
  const [error, setError] = useState("");
  const token = localStorage.getItem("token");

  useEffect(() => {
    fetch(`${getApiBaseUrl()}/api/billing/status`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then(async response => {
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || "Не удалось загрузить подписку.");
        setStatus(data);
      })
      .catch(err => setError(err instanceof Error ? err.message : "Ошибка загрузки статуса подписки."))
      .finally(() => setLoading(false));
  }, [token]);

  const handleUpgrade = async (plan: string) => {
    setCheckoutLoading(plan);
    setError("");
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/billing/upgrade?plan_name=${encodeURIComponent(plan)}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Не удалось открыть оплату.");
      if (!data.checkout_url) throw new Error("Провайдер не вернул ссылку на оплату.");
      window.location.assign(data.checkout_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка подключения к оплате.");
    } finally {
      setCheckoutLoading("");
    }
  };

  const handlePortal = async () => {
    setCheckoutLoading("portal");
    setError("");
    try {
      const response = await fetch(`${getApiBaseUrl()}/api/billing/portal`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Не удалось открыть управление подпиской.");
      if (!data.portal_url) throw new Error("Stripe не вернул ссылку на управление подпиской.");
      window.location.assign(data.portal_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка управления подпиской.");
    } finally {
      setCheckoutLoading("");
    }
  };

  if (loading) {
    return <div style={{ color: "var(--text-secondary)", textAlign: "center", padding: "3rem" }}>Загрузка статуса подписки…</div>;
  }

  const currentPlan = status?.plan_name?.toLowerCase() || "free";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "2rem", maxWidth: "1100px", margin: "0 auto", width: "100%" }}>
      {/* Header banner */}
      <div style={{ textAlign: "center", padding: "1rem 0 0.5rem 0" }}>
        <div className="badge-tag" style={{ marginBottom: "1rem", padding: "4px 12px" }}>
          LUMIRA MEMBERSHIP
        </div>
        <h2 style={{ fontSize: "2rem", fontWeight: 700, letterSpacing: "1px", marginBottom: "0.75rem" }}>
          Тарифные Планы Студии
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", maxWidth: "580px", margin: "0 auto" }}>
          Выберите уровень доступа для неограниченного математического анализа натальной карты, предсказательной астрологии и диалога с оракулом.
        </p>
      </div>

      {error && (
        <div style={{
          padding: "1rem 1.5rem",
          background: "rgba(241, 106, 118, 0.12)",
          border: "1px solid var(--status-error)",
          borderRadius: "8px",
          color: "var(--status-error)",
          fontSize: "0.9rem",
          textAlign: "center"
        }}>
          {error}
        </div>
      )}

      {/* Subscription Active Banner */}
      {currentPlan !== "free" && status?.status === "active" && (
        <div className="glass-panel" style={{ padding: "1.25rem 2rem", display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "1rem" }}>
          <div>
            <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>Текущий активный план:</span>
            <div style={{ fontSize: "1.2rem", fontWeight: 600, color: "var(--accent-gold)", textTransform: "uppercase" }}>
              {status.plan_name}
            </div>
          </div>
          <button className="btn-secondary" onClick={handlePortal} disabled={!!checkoutLoading}>
            {checkoutLoading === "portal" ? "Открываем…" : "Управлять подпиской в Stripe"}
          </button>
        </div>
      )}

      {/* 3 Tier Pricing Cards */}
      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(290px, 1fr))",
        gap: "1.5rem",
        alignItems: "stretch"
      }}>
        {/* TIER 1: FREE */}
        <div className="glass-panel" style={{
          padding: "2rem",
          display: "flex",
          flexDirection: "column",
          borderRadius: "12px",
          background: "var(--bg-card-secondary)",
          border: currentPlan === "free" ? "1px solid rgba(221, 186, 72, 0.4)" : "1px solid var(--border-card)",
          position: "relative"
        }}>
          {currentPlan === "free" && (
            <div className="badge-tag" style={{ position: "absolute", top: "1.25rem", right: "1.25rem" }}>
              Текущий план
            </div>
          )}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "0.5rem" }}>
            <Shield size={20} style={{ color: "var(--text-secondary)" }} />
            <h3 style={{ fontSize: "1.25rem", fontWeight: 600 }}>FREE</h3>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", minHeight: "38px" }}>
            Базовые астрологические расчёты и ежедневный космический брифинг.
          </p>
          <div style={{ margin: "1.5rem 0", borderBottom: "1px solid var(--border-card)", paddingBottom: "1.5rem" }}>
            <span style={{ fontSize: "2rem", fontWeight: 700, color: "var(--text-main)" }}>$0</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}> / навсегда</span>
          </div>

          <ul style={{ listStyle: "none", padding: 0, margin: "0 0 2rem 0", display: "flex", flexDirection: "column", gap: "10px", flex: 1, fontSize: "0.85rem" }}>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--status-success)" }} />
              <span>Расчёт натальной карты (Swiss Ephemeris)</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--status-success)" }} />
              <span>Ежедневная Панчанга и транзиты</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--status-success)" }} />
              <span>Базовый скрининг Мухурты</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px", color: "var(--text-muted)" }}>
              <span>• Лимит AI-чата: до 5 сообщений в день</span>
            </li>
          </ul>

          <button
            className="btn-secondary"
            style={{ width: "100%", opacity: currentPlan === "free" ? 0.6 : 1 }}
            disabled
          >
            {currentPlan === "free" ? "Используется" : "Базовый уровень"}
          </button>
        </div>

        {/* TIER 2: PRO */}
        <div className="glass-panel" style={{
          padding: "2rem",
          display: "flex",
          flexDirection: "column",
          borderRadius: "12px",
          background: "var(--bg-card)",
          border: "2px solid var(--accent-gold)",
          boxShadow: "0 8px 30px var(--accent-gold-glow)",
          position: "relative",
          transform: "scale(1.02)"
        }}>
          <div className="badge-tag" style={{ position: "absolute", top: "-12px", right: "1.5rem", background: "var(--accent-gold)", color: "#080A12", fontWeight: 700 }}>
            РЕКОМЕНДОВАНО
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "0.5rem" }}>
            <Zap size={20} style={{ color: "var(--accent-gold)" }} />
            <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--accent-gold)" }}>PRO</h3>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", minHeight: "38px" }}>
            {t("billing.pro_desc")}
          </p>
          <div style={{ margin: "1.5rem 0", borderBottom: "1px solid var(--border-card)", paddingBottom: "1.5rem" }}>
            <span style={{ fontSize: "2rem", fontWeight: 700, color: "var(--accent-gold)" }}>$9.99</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}> / месяц</span>
          </div>

          <ul style={{ listStyle: "none", padding: 0, margin: "0 0 2rem 0", display: "flex", flexDirection: "column", gap: "10px", flex: 1, fontSize: "0.85rem" }}>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--accent-gold)" }} />
              <span><strong>До 50 сообщений AI-чата</strong> в день</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--accent-gold)" }} />
              <span>Расширенный анализ аспектов и куспидов</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--accent-gold)" }} />
              <span>Персональные транзиты и прогноз натива</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--accent-gold)" }} />
              <span>Приоритетная скорость ответа LLM</span>
            </li>
          </ul>

          <button
            className="btn-primary"
            style={{ width: "100%" }}
            onClick={() => handleUpgrade("pro")}
            disabled={!!checkoutLoading || currentPlan === "pro"}
          >
            {checkoutLoading === "pro" ? "Переход к оплате…" : currentPlan === "pro" ? t("billing.current_plan_btn") : t("billing.upgrade_pro")}
          </button>
        </div>

        {/* TIER 3: PREMIUM */}
        <div className="glass-panel" style={{
          padding: "2rem",
          display: "flex",
          flexDirection: "column",
          borderRadius: "12px",
          background: "var(--bg-card-secondary)",
          border: currentPlan === "premium" ? "2px solid var(--accent-gold)" : "1px solid var(--border-card)",
          position: "relative"
        }}>
          {currentPlan === "premium" && (
            <div className="badge-tag" style={{ position: "absolute", top: "1.25rem", right: "1.25rem" }}>
              Текущий план
            </div>
          )}
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "0.5rem" }}>
            <Sparkles size={20} style={{ color: "var(--accent-gold-light)" }} />
            <h3 style={{ fontSize: "1.25rem", fontWeight: 600, color: "var(--text-main)" }}>PREMIUM</h3>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", minHeight: "38px" }}>
            {t("billing.premium_desc")}
          </p>
          <div style={{ margin: "1.5rem 0", borderBottom: "1px solid var(--border-card)", paddingBottom: "1.5rem" }}>
            <span style={{ fontSize: "2rem", fontWeight: 700, color: "var(--text-main)" }}>$24.99</span>
            <span style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}> / месяц</span>
          </div>

          <ul style={{ listStyle: "none", padding: 0, margin: "0 0 2rem 0", display: "flex", flexDirection: "column", gap: "10px", flex: 1, fontSize: "0.85rem" }}>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--status-success)" }} />
              <span><strong>Увеличенный лимит AI-чата</strong></span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--status-success)" }} />
              <span>Глубокий анализ периодов (Даши и антардаши)</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--status-success)" }} />
              <span>Поддержка астрологического архива и заметок</span>
            </li>
            <li style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <Check size={16} style={{ color: "var(--status-success)" }} />
              <span>Максимальный приоритет обработки запросов</span>
            </li>
          </ul>

          <button
            className="btn-primary"
            style={{ width: "100%", background: "linear-gradient(135deg, var(--accent-gold) 0%, var(--accent-gold-dark) 100%)" }}
            onClick={() => handleUpgrade("premium")}
            disabled={!!checkoutLoading || currentPlan === "premium"}
          >
            {checkoutLoading === "premium" ? "Переход к оплате…" : currentPlan === "premium" ? t("billing.current_plan_btn") : t("billing.upgrade_premium")}
          </button>
        </div>
      </div>

      <p style={{ textAlign: "center", fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "1rem" }}>
        Безопасная оплата через Stripe. Доступ к тарифам активируется мгновенно после подтверждения транзакции сервером.
      </p>
    </div>
  );
}
