import { useMemo, useState } from "react";
import Link from "next/link";
import useSWR from "swr";

import { apiClient } from "../services/apiClient";

const knowledgeFetcher = (url: string) => apiClient.get(url).then((res) => res.data);

const groupEntries = (items: Array<{ term?: string; translation?: string | null; notes?: string | null }>) => {
  const groups = new Map<string, typeof items>();
  items.forEach((item) => {
    const term = (item.term ?? "").trim();
    const firstChar = term.charAt(0).toUpperCase();
    const key = /[A-Z]/.test(firstChar) ? firstChar : "#";
    if (!groups.has(key)) {
      groups.set(key, []);
    }
    groups.get(key)?.push(item);
  });
  return Array.from(groups.entries())
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([letter, entries]) => ({ letter, entries: entries.sort((a, b) => (a.term ?? "").localeCompare(b.term ?? "")) }));
};

const buildKey = (search: string) => {
  const trimmed = search.trim();
  return `/agent/entries${trimmed ? `?search=${encodeURIComponent(trimmed)}` : ""}`;
};

const KnowledgePage = () => {
  const [search, setSearch] = useState("");
  const { data } = useSWR(buildKey(search), knowledgeFetcher, {
    revalidateOnFocus: false,
  });

  const groups = useMemo(() => {
    if (!data?.items) {
      return [] as ReturnType<typeof groupEntries>;
    }
    return groupEntries(data.items as any);
  }, [data]);

  return (
    <main className="page-shell">
      <div className="page-card">
        <div className="top-nav">
          <Link href="/" className="back-link" aria-label="Go back to home">
            <svg viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M11.25 5L6.25 10L11.25 15" stroke="#2563EB" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            Back
          </Link>
        </div>

        <header className="page-header">
          <span className="status-pill">Glossary</span>
          <h1 className="page-title">Knowledge Base</h1>
          <p className="page-subtitle">
            Every agent lookup is stored here so you can revisit bilingual explanations on the go.
          </p>
        </header>

        <input
          className="search-input"
          placeholder="Search terms or translations"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Search glossary"
        />

        <section className="knowledge-list" aria-live="polite">
          {groups.length === 0 ? (
            <p className="item-notes">Ask the assistant a question to populate your glossary.</p>
          ) : (
            groups.map(({ letter, entries }) => (
              <div className="knowledge-group" key={letter}>
                <h2 className="group-title">{letter}</h2>
                {entries.map((entry) => (
                  <article className="knowledge-item" key={entry.term}>
                    <h3 className="item-term">{entry.term}</h3>
                    {entry.translation && <p className="item-translation">{entry.translation}</p>}
                    {entry.notes && <p className="item-notes">{entry.notes.slice(0, 140)}...</p>}
                  </article>
                ))}
              </div>
            ))
          )}
        </section>
      </div>
    </main>
  );
};

export default KnowledgePage;
