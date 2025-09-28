import { useMemo, useState } from "react";
import Link from "next/link";
import useSWR, { mutate } from "swr";

import { apiClient } from "../services/apiClient";

const knowledgeFetcher = (url: string) => apiClient.get(url).then((res) => res.data);
const documentFetcher = (url: string) => apiClient.get(url).then((res) => res.data);

const groupEntries = (items: Array<{ id?: string; term?: string; translation?: string | null; notes?: string | null }>) => {
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

const buildTermKey = (search: string) => {
  const trimmed = search.trim();
  return `/agent/entries${trimmed ? `?search=${encodeURIComponent(trimmed)}` : ""}`;
};

const buildDocumentKey = (search: string) => {
  const trimmed = search.trim();
  return `/agent/documents${trimmed ? `?search=${encodeURIComponent(trimmed)}` : ""}`;
};

const KnowledgePage = () => {
  const [search, setSearch] = useState("");
  const [activeTab, setActiveTab] = useState<"terms" | "documents">("terms");
  const [selectedEntry, setSelectedEntry] = useState<Record<string, any> | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<Record<string, any> | null>(null);
  const { data: termsData } = useSWR(activeTab === "terms" ? buildTermKey(search) : null, knowledgeFetcher, {
    revalidateOnFocus: false,
  });
  const { data: documentsData } = useSWR(activeTab === "documents" ? buildDocumentKey(search) : null, documentFetcher, {
    revalidateOnFocus: false,
  });

  const groups = useMemo(() => {
    if (!termsData?.items) {
      return [] as ReturnType<typeof groupEntries>;
    }
    return groupEntries(termsData.items as any);
  }, [termsData]);

  const handleSelectEntry = async (entryId: string) => {
    const response = await apiClient.get(`/agent/entries/${entryId}`);
    setSelectedEntry(response.data);
  };

  const handleUpdateEntry = async () => {
    if (!selectedEntry?.id) {
      return;
    }
    await apiClient.put(`/agent/entries/${selectedEntry.id}`, {
      term: selectedEntry.term,
      translation: selectedEntry.translation,
      notes: selectedEntry.notes,
      categories: selectedEntry.categories ?? [],
    });
    await mutate(buildTermKey(search));
  };

  const handleDeleteEntry = async (entryId: string) => {
    await apiClient.delete(`/agent/entries/${entryId}`);
    setSelectedEntry(null);
    await mutate(buildTermKey(search));
  };

  const handleSelectDocument = async (docId: string) => {
    const response = await apiClient.get(`/agent/documents/${docId}`);
    setSelectedDocument(response.data);
  };

  const handleDeleteDocument = async (docId: string) => {
    await apiClient.delete(`/agent/documents/${docId}`);
    setSelectedDocument(null);
    await mutate(buildDocumentKey(search));
  };

  const handleUploadDocument = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    await apiClient.post("/agent/documents", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    event.currentTarget.reset();
    await mutate(buildDocumentKey(""));
    setSearch("");
  };

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
          <div className="nav-tabs">
            <button
              className={`tab-button ${activeTab === "terms" ? "active" : ""}`}
              type="button"
              onClick={() => {
                setActiveTab("terms");
                setSelectedDocument(null);
              }}
            >
              Terms
            </button>
            <button
              className={`tab-button ${activeTab === "documents" ? "active" : ""}`}
              type="button"
              onClick={() => {
                setActiveTab("documents");
                setSelectedEntry(null);
              }}
            >
              Documents
            </button>
          </div>
        </div>

        <header className="page-header">
          <span className="status-pill">Knowledge Base</span>
          <h1 className="page-title">Study Library</h1>
          <p className="page-subtitle">
            Every agent lookup and uploaded resource lives here. Open, edit, or delete items as you curate your personalized encyclopedia.
          </p>
        </header>

        <input
          className="search-input"
          placeholder="Search terms, translations, or documents"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          aria-label="Search knowledge base"
        />

        {activeTab === "terms" ? (
          <section className="knowledge-list" aria-live="polite">
            {groups.length === 0 ? (
              <p className="item-notes">Ask the assistant a question to populate your glossary.</p>
            ) : (
              groups.map(({ letter, entries }) => (
                <div className="knowledge-group" key={letter}>
                  <h2 className="group-title">{letter}</h2>
                  {entries.map((entry) => (
                    <button
                      key={entry.id ?? entry.term}
                      type="button"
                      className="knowledge-item"
                      onClick={() => handleSelectEntry(entry.id ?? "")}
                    >
                      <h3 className="item-term">{entry.term}</h3>
                      {entry.translation && <p className="item-translation">{entry.translation}</p>}
                      {entry.notes && <p className="item-notes">{entry.notes.slice(0, 100)}...</p>}
                    </button>
                  ))}
                </div>
              ))
            )}
          </section>
        ) : (
          <section className="knowledge-list" aria-live="polite">
            <form className="upload-form" onSubmit={handleUploadDocument}>
              <label className="upload-label">
                <span>Upload TXT or PDF</span>
                <input name="file" type="file" accept=".txt,.pdf,.md" required />
              </label>
              <input name="title" placeholder="Title (optional)" />
              <input name="summary" placeholder="Summary (optional)" />
              <input name="categories" placeholder="Categories (comma separated)" />
              <button type="submit" className="primary-button">
                Upload Document
              </button>
            </form>

            {!documentsData?.items?.length ? (
              <p className="item-notes">Upload PDFs or notes to enrich the retrieval knowledge base.</p>
            ) : (
              documentsData.items.map((doc: any) => (
                <button
                  key={doc.id}
                  type="button"
                  className="knowledge-item"
                  onClick={() => handleSelectDocument(doc.id)}
                >
                  <h3 className="item-term">{doc.title}</h3>
                  <p className="item-translation">{doc.filename}</p>
                  {doc.summary && <p className="item-notes">{doc.summary}</p>}
                </button>
              ))
            )}
          </section>
        )}

        {selectedEntry && (
          <section className="detail-card">
            <h2 className="response-title">{selectedEntry.term}</h2>
            <textarea
              className="dashboard-textarea"
              rows={3}
              value={selectedEntry.translation ?? ""}
              placeholder="Translation"
              onChange={(event) => setSelectedEntry({ ...selectedEntry, translation: event.target.value })}
            />
            <textarea
              className="dashboard-textarea"
              rows={6}
              value={selectedEntry.notes ?? ""}
              placeholder="Notes"
              onChange={(event) => setSelectedEntry({ ...selectedEntry, notes: event.target.value })}
            />
            <input
              className="search-input"
              value={(selectedEntry.categories ?? []).join(", ")}
              onChange={(event) =>
                setSelectedEntry({
                  ...selectedEntry,
                  categories: event.target.value
                    .split(",")
                    .map((item) => item.trim())
                    .filter(Boolean),
                })
              }
              placeholder="Categories"
            />
            <div className="detail-actions">
              <button type="button" className="primary-button" onClick={handleUpdateEntry}>
                Save Changes
              </button>
              <button type="button" className="danger-button" onClick={() => handleDeleteEntry(selectedEntry.id)}>
                Delete
              </button>
            </div>
          </section>
        )}

        {selectedDocument && (
          <section className="detail-card">
            <h2 className="response-title">{selectedDocument.title}</h2>
            <p className="item-translation">{selectedDocument.filename}</p>
            {selectedDocument.summary && <p className="item-notes">{selectedDocument.summary}</p>}
            <pre className="document-preview">{selectedDocument.content?.slice(0, 1200) ?? "(no text extracted)"}</pre>
            <div className="detail-actions">
              <button type="button" className="danger-button" onClick={() => handleDeleteDocument(selectedDocument.id)}>
                Delete Document
              </button>
            </div>
          </section>
        )}
      </div>
    </main>
  );
};

export default KnowledgePage;
