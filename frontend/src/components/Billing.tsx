import { getApiBaseUrl } from "../api";
import { useState, useEffect } from "react";
import { useLanguage } from "../i18n";

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

  if (loading) return <div style={{ color: "var(--text-light)" }}>Загрузка статуса подписки…</div>;

  return (
    <div className="glass-panel" style={{ padding: "2rem", borderRadius: 12 }}>
      <h2 style={{ color: "var(--accent-gold)", marginBottom: "1rem" }}>{t("billing.title")}</h2>
      <div style={{ marginBottom: "1.5rem" }}>
        <p>{t("billing.current")} <strong style={{ color: "var(--accent-gold)", textTransform: "uppercase" }}>{status?.plan_name === "free" ? t("billing.free") : status?.plan_name || t("billing.free")}</strong></p>
        <p>{t("billing.status")} {status?.status || "unknown"}</p>
      </div>
      <p style={{ color: "var(--text-muted)", marginBottom: "1.5rem" }}>
        Оплата проходит через Stripe при настроенных на сервере ключах и Price ID. Доступ к платному тарифу включается только после подтверждения подписки серверным webhook.
      </p>
      {error && <p role="alert" style={{ color: "#ff8c8c", marginBottom: "1rem" }}>{error}</p>}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "1.5rem" }}>
        <div className="glass-panel" style={{ padding: "1.5rem", textAlign: "center", borderRadius: 8 }}>
          <h3>PRO PLAN</h3>
          <p style={{ margin: "1rem 0" }}>{t("billing.pro_desc")}</p>
          <p style={{ fontSize: "1.5rem", color: "var(--accent-gold)", marginBottom: "1rem" }}>$9.99 / mo</p>
          <button className="btn-primary" style={{ width: "100%" }} onClick={() => handleUpgrade("pro")} disabled={!!checkoutLoading || status?.plan_name === "pro"}>
            {checkoutLoading === "pro" ? "Переход к оплате…" : status?.plan_name === "pro" ? t("billing.current_plan_btn") : t("billing.upgrade_pro")}
          </button>
        </div>
        <div className="glass-panel" style={{ padding: "1.5rem", textAlign: "center", borderRadius: 8, border: "1px solid var(--accent-gold)" }}>
          <h3>PREMIUM PLAN</h3>
          <p style={{ margin: "1rem 0" }}>{t("billing.premium_desc")}</p>
          <p style={{ fontSize: "1.5rem", color: "var(--accent-gold)", marginBottom: "1rem" }}>$24.99 / mo</p>
          <button className="btn-primary" style={{ width: "100%" }} onClick={() => handleUpgrade("premium")} disabled={!!checkoutLoading || status?.plan_name === "premium"}>
            {checkoutLoading === "premium" ? "Переход к оплате…" : status?.plan_name === "premium" ? t("billing.current_plan_btn") : t("billing.upgrade_premium")}
          </button>
        </div>
      </div>
    </div>
  );
}
