import { useEffect, useMemo, useState } from "react";
import useSWR from "swr";

import { apiClient } from "../services/apiClient";

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

const DashboardPage = () => {
  const { data: health, error } = useSWR("/health", fetcher, {
    revalidateOnFocus: false,
  });
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (health) {
      console.debug("API health", health);
    }
  }, [health]);

  const status = useMemo(() => {
    if (health) {
      return { label: "Backend online", variant: "status-pill" } as const;
    }
    if (error) {
      return { label: "Backend offline", variant: "status-pill offline" } as const;
    }
    return { label: "Checking status¡­", variant: "status-pill" } as const;
  }, [health, error]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!query.trim()) {
      return;
    }
    setLoading(true);
    try {
      const response = await apiClient.post("/agent/query", { query });
      setResult(response.data?.answer ?? "No response yet");
    } catch (submitError) {
      console.error("Agent query failed", submitError);
      setResult("Unable to reach the agent service right now. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <div className="page-card">
        <header className="page-header">
          <span className={status.variant}>{status.label}</span>
          <h1 className="page-title">Study Dashboard</h1>
          <p className="page-subtitle">
            Keep pulse on your study flow, queue quick questions, and review generated answers in one clean view.
          </p>
        </header>

        <section>
          <p className="section-label">Agent quick query</p>
          <form className="dashboard-form" onSubmit={handleSubmit}>
            <textarea
              className="dashboard-textarea"
              rows={4}
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Describe the nursing concept, abbreviation, or scenario you want clarified"
            />
            <button type="submit" className="primary-button" disabled={loading}>
              {loading ? "Thinking¡­" : "Ask Agent ¡ú"}
            </button>
          </form>
        </section>

        {result && (
          <article className="response-card" aria-live="polite">
            <h2 className="response-title">Agent response</h2>
            <p className="response-body">{result}</p>
          </article>
        )}

        <p className="footer-note">
          Tip: add complex cases here during rounds, then refine the flashcards back on a larger screen.
        </p>
      </div>
    </main>
  );
};

export default DashboardPage;
