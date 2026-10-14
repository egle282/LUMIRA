import { useState } from "react";
import { getApiBaseUrl } from "../api";
import { useLanguage } from "../i18n";
import { Calendar, Clock, Sparkles } from "lucide-react";

type Sample = {
  time: string;
  score: number;
  tithi: number;
  tithi_name: string;
  nakshatra: number;
  nakshatra_name: string;
  yoga: number;
  karana: number;
  karana_name: string;
};

type MuhurtaResult = {
  date: string;
  activity: string;
  timezone: string;
  method: string;
  best_hour: Sample;
  samples: Sample[];
  limitations: string;
};

export function Muhurta() {
  const { t } = useLanguage();
  const [selectedDate, setSelectedDate] = useState("");
  const [activity, setActivity] = useState("business");
  const [result, setResult] = useState<MuhurtaResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const activities = [
    { value: "business", label: t("muhurta.business") },
    { value: "marriage", label: t("muhurta.marriage") },
    { value: "travel", label: t("muhurta.travel") },
    { value: "health", label: t("muhurta.health") },
  ];

  const calculateMuhurta = async () => {
    if (!selectedDate) return;
    const token = localStorage.getItem("token");
    if (!token) {
      setError("Войдите в аккаунт и заполните профиль с часовым поясом.");
      return;
    }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const query = new URLSearchParams({ date: selectedDate, activity });
      const response = await fetch(`${getApiBaseUrl()}/api/muhurta/calculate?${query}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || "Не удалось рассчитать Панчангу.");
      setResult(data as MuhurtaResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка запроса. Попробуйте ещё раз.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem", maxWidth: "900px", margin: "0 auto", width: "100%" }}>
      {/* Header Panel */}
      <div className="glass-panel" style={{ padding: "1.75rem", textAlign: "center" }}>
        <div style={{ display: "inline-flex", padding: "10px", borderRadius: "12px", background: "rgba(221, 186, 72, 0.12)", marginBottom: "0.75rem", border: "1px solid rgba(221, 186, 72, 0.25)" }}>
          <Calendar size={24} style={{ color: "var(--accent-gold)" }} />
        </div>
        <h2 style={{ fontSize: "1.5rem", fontWeight: 700, letterSpacing: "1px", marginBottom: "0.5rem" }}>
          {t('muhurta.title')}
        </h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem", maxWidth: "560px", margin: "0 auto" }}>
          {t('muhurta.desc')}
        </p>

        {/* Inputs */}
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center", marginTop: "1.5rem" }}>
          <div style={{ display: "flex", flexDirection: "column", gap: "6px", textAlign: "left", minWidth: "220px" }}>
            <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{t('muhurta.event_date')}</label>
            <input
              type="date"
              value={selectedDate}
              onChange={e => setSelectedDate(e.target.value)}
              className="studio-input"
            />
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "6px", textAlign: "left", minWidth: "220px" }}>
            <label style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>{t('muhurta.event_type')}</label>
            <select
              value={activity}
              onChange={e => setActivity(e.target.value)}
              className="studio-input"
              style={{ cursor: "pointer" }}
            >
              {activities.map(item => (
                <option key={item.value} value={item.value} style={{ background: "#141521", color: "#FFF" }}>
                  {item.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div style={{ marginTop: "1.5rem" }}>
          <button
            className="btn-primary"
            onClick={calculateMuhurta}
            disabled={!selectedDate || loading}
            style={{ minWidth: "200px" }}
          >
            {loading ? t('muhurta.calculating') : t('muhurta.calc_btn')}
          </button>
        </div>

        {error && (
          <p role="alert" style={{ color: "var(--status-error)", marginTop: "1rem", fontSize: "0.9rem" }}>
            {error}
          </p>
        )}
      </div>

      {/* Results */}
      {result && (
        <>
          {/* Best Hour Hero Card */}
          <div className="glass-panel" style={{
            padding: "1.75rem",
            background: "var(--bg-card)",
            border: "2px solid var(--accent-gold)",
            boxShadow: "0 8px 30px var(--accent-gold-glow)",
            display: "flex",
            flexDirection: "column",
            gap: "1rem"
          }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "0.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Sparkles size={18} style={{ color: "var(--accent-gold)" }} />
                <span style={{ color: "var(--text-secondary)", fontSize: "0.85rem", textTransform: "uppercase", letterSpacing: "1px" }}>
                  {t('muhurta.best_hour')} • {result.timezone}
                </span>
              </div>
              <div className="badge-tag">
                Благоприятность: {result.best_hour.score}/9
              </div>
            </div>

            <div style={{ display: "flex", alignItems: "baseline", gap: "1rem" }}>
              <div style={{ fontSize: "2.2rem", fontWeight: 700, color: "var(--accent-gold)" }}>
                {result.best_hour.time}
              </div>
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: "0.75rem", background: "var(--bg-card-secondary)", padding: "1rem", borderRadius: "8px" }}>
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{t('dash.tithi')}:</span>
                <div style={{ fontWeight: 600 }}>{result.best_hour.tithi_name} (#{result.best_hour.tithi})</div>
              </div>
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{t('dash.nakshatra')}:</span>
                <div style={{ fontWeight: 600 }}>{result.best_hour.nakshatra_name} (#{result.best_hour.nakshatra})</div>
              </div>
              <div>
                <span style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>{t('dash.yoga')} / {t('dash.karana')}:</span>
                <div style={{ fontWeight: 600 }}>#{result.best_hour.yoga} • {result.best_hour.karana_name}</div>
              </div>
            </div>

            <p style={{ color: "var(--text-secondary)", fontSize: "0.82rem", margin: 0 }}>
              {result.method}
            </p>
          </div>

          {/* Hourly Breakdown Table */}
          <div className="glass-panel" style={{ padding: "1.5rem" }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, marginBottom: "1rem", display: "flex", alignItems: "center", gap: "8px" }}>
              <Clock size={16} style={{ color: "var(--accent-gold)" }} />
              Почасовая шкала благоприятности
            </h3>
            <div style={{ overflowX: "auto" }}>
              <table className="studio-table">
                <thead>
                  <tr>
                    <th>{t('muhurta.time')}</th>
                    <th>{t('dash.tithi')}</th>
                    <th>{t('dash.nakshatra')}</th>
                    <th style={{ textAlign: "right" }}>{t('dash.auspiciousness')}</th>
                  </tr>
                </thead>
                <tbody>
                  {result.samples.map(s => {
                    const isBest = s.time === result.best_hour.time;
                    return (
                      <tr key={s.time} style={{ background: isBest ? "rgba(221, 186, 72, 0.12)" : undefined }}>
                        <td style={{ fontWeight: isBest ? 700 : 500, color: isBest ? "var(--accent-gold)" : undefined }}>
                          {s.time} {isBest && "★"}
                        </td>
                        <td>{s.tithi_name}</td>
                        <td>{s.nakshatra_name}</td>
                        <td style={{ textAlign: "right", fontWeight: 600, color: s.score >= 7 ? "var(--status-success)" : undefined }}>
                          {s.score}/9
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
            <p style={{ color: "var(--text-muted)", fontSize: "0.78rem", marginTop: "1rem", lineHeight: "1.4" }}>
              {result.limitations}
            </p>
          </div>
        </>
      )}
    </div>
  );
}
