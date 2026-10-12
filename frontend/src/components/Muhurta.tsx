import { useState } from "react";
import { getApiBaseUrl } from "../api";

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

const activities = [
  { value: "business", label: "Бизнес и финансы" },
  { value: "marriage", label: "Отношения и брак" },
  { value: "travel", label: "Путешествия" },
  { value: "health", label: "Здоровье и процедуры" },
];

export function Muhurta() {
  const [selectedDate, setSelectedDate] = useState("");
  const [activity, setActivity] = useState("business");
  const [result, setResult] = useState<MuhurtaResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

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
    <div className="glass-panel" style={{ padding: "2rem", minHeight: "60vh", display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <header style={{ textAlign: "center" }}>
        <h2 style={{ color: "var(--accent-gold)", marginBottom: ".75rem" }}>Мухурта · Панчанга</h2>
        <p style={{ color: "var(--text-muted)" }}>Предварительный почасовой скрининг лунного дня и накшатры по сохранённому месту и часовому поясу.</p>
      </header>
      <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center" }}>
        <label style={{ display: "flex", flexDirection: "column", gap: ".5rem", minWidth: 240 }}>
          <span>Дата события</span>
          <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)} />
        </label>
        <label style={{ display: "flex", flexDirection: "column", gap: ".5rem", minWidth: 240 }}>
          <span>Тип события</span>
          <select value={activity} onChange={e => setActivity(e.target.value)}>
            {activities.map(item => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        </label>
      </div>
      <div style={{ textAlign: "center" }}>
        <button className="btn-primary" onClick={calculateMuhurta} disabled={!selectedDate || loading}>
          {loading ? "Рассчитываем…" : "Рассчитать Панчангу"}
        </button>
      </div>
      {error && <p role="alert" style={{ color: "#ff8c8c", textAlign: "center" }}>{error}</p>}
      {result && <>
        <section className="glass-panel" style={{ padding: "1.5rem", borderRadius: 12 }}>
          <p style={{ color: "var(--text-muted)" }}>Лучший час по базовой эвристике · {result.timezone}</p>
          <h3 style={{ color: "var(--accent-gold)", fontSize: "1.8rem" }}>{result.best_hour.time} · оценка {result.best_hour.score}/9</h3>
          <p>Титхи: {result.best_hour.tithi_name} ({result.best_hour.tithi})</p>
          <p>Накшатра: {result.best_hour.nakshatra_name} ({result.best_hour.nakshatra})</p>
          <p>Йога: {result.best_hour.yoga} · Карана: {result.best_hour.karana_name}</p>
          <p style={{ color: "var(--text-muted)", marginTop: "1rem" }}>{result.method}</p>
        </section>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead><tr><th align="left">Время</th><th align="left">Титхи</th><th align="left">Накшатра</th><th align="right">Оценка</th></tr></thead>
            <tbody>{result.samples.map(s => <tr key={s.time}><td>{s.time}</td><td>{s.tithi_name}</td><td>{s.nakshatra_name}</td><td align="right">{s.score}/9</td></tr>)}</tbody>
          </table>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: ".9rem" }}>{result.limitations}</p>
      </>}
    </div>
  );
}
