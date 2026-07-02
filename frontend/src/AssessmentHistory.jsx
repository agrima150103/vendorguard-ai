import { useEffect, useMemo, useState } from "react";

import { getAssessments } from "./api";
import "./assessment-history.css";

function label(value) {
  if (!value) return "—";
  return String(value)
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatDate(value) {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export default function AssessmentHistory({ onBack, onOpenAssessment }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [risk, setRisk] = useState("ALL");
  const [status, setStatus] = useState("ALL");
  const [sort, setSort] = useState("NEWEST");

  async function load() {
    try {
      setLoading(true);
      setError("");
      setItems(await getAssessments());
    } catch (loadError) {
      console.error(loadError);
      setError("Assessment history could not be loaded. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  const filteredItems = useMemo(() => {
    const query = search.trim().toLowerCase();
    const result = items.filter((item) => {
      const matchesSearch =
        !query ||
        item.vendor_name.toLowerCase().includes(query) ||
        item.assessment_id.toLowerCase().includes(query);
      const matchesRisk = risk === "ALL" || item.risk_tier === risk;
      const matchesStatus = status === "ALL" || item.status === status;
      return matchesSearch && matchesRisk && matchesStatus;
    });

    return [...result].sort((a, b) => {
      if (sort === "OLDEST") {
        return new Date(a.created_at) - new Date(b.created_at);
      }
      if (sort === "RISK_HIGH") {
        return (b.risk_score ?? -1) - (a.risk_score ?? -1);
      }
      if (sort === "RISK_LOW") {
        return (a.risk_score ?? 101) - (b.risk_score ?? 101);
      }
      return new Date(b.created_at) - new Date(a.created_at);
    });
  }, [items, search, risk, status, sort]);

  return (
    <div className="history-page">
      <header className="history-header">
        <div>
          <button className="history-back" onClick={onBack}>← Home</button>
          <h1>Assessment history</h1>
          <p>Search, filter, sort, and reopen saved vendor assessments.</p>
        </div>
        <button className="history-refresh" onClick={load} disabled={loading}>
          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </header>

      <section className="history-controls" aria-label="Assessment filters">
        <label>
          Search
          <input
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Vendor name or assessment ID"
          />
        </label>

        <label>
          Risk
          <select value={risk} onChange={(event) => setRisk(event.target.value)}>
            <option value="ALL">All risks</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
          </select>
        </label>

        <label>
          Status
          <select value={status} onChange={(event) => setStatus(event.target.value)}>
            <option value="ALL">All statuses</option>
            <option value="AWAITING_HUMAN_REVIEW">Awaiting review</option>
            <option value="COMPLETE">Complete</option>
            <option value="FAILED">Failed</option>
          </select>
        </label>

        <label>
          Sort
          <select value={sort} onChange={(event) => setSort(event.target.value)}>
            <option value="NEWEST">Newest first</option>
            <option value="OLDEST">Oldest first</option>
            <option value="RISK_HIGH">Highest risk</option>
            <option value="RISK_LOW">Lowest risk</option>
          </select>
        </label>
      </section>

      {error && <div className="history-error">{error}</div>}

      {loading ? (
        <div className="history-empty">Loading saved assessments...</div>
      ) : items.length === 0 ? (
        <div className="history-empty">No assessments have been created yet.</div>
      ) : filteredItems.length === 0 ? (
        <div className="history-empty">No assessments match the selected filters.</div>
      ) : (
        <div className="history-table-wrap">
          <table className="history-table">
            <thead>
              <tr>
                <th>Vendor</th>
                <th>Risk</th>
                <th>Recommendation</th>
                <th>Pipeline</th>
                <th>Status</th>
                <th>Created</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredItems.map((item) => (
                <tr key={item.assessment_id}>
                  <td>
                    <strong>{item.vendor_name}</strong>
                    <span>{item.assessment_id}</span>
                  </td>
                  <td>
                    <span className={`history-risk history-risk-${item.risk_tier.toLowerCase()}`}>
                      {item.risk_score ?? "—"} · {label(item.risk_tier)}
                    </span>
                  </td>
                  <td>{label(item.recommendation)}</td>
                  <td><span className={`history-pipeline history-pipeline-${item.pipeline_mode.toLowerCase()}`}>{label(item.pipeline_mode)}</span></td>
                  <td>{label(item.status)}</td>
                  <td>{formatDate(item.created_at)}</td>
                  <td>
                    <button onClick={() => onOpenAssessment(item)}>Open</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
