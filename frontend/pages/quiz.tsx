import { useMemo, useState } from "react";
import Link from "next/link";
import useSWR, { mutate } from "swr";

import { apiClient } from "../services/apiClient";

const quizFetcher = (url: string) => apiClient.get(url).then((res) => res.data);

const QuizPage = () => {
  const [category, setCategory] = useState<string>("");
  const [expandedQuiz, setExpandedQuiz] = useState<string | null>(null);
  const { data } = useSWR(`/quiz${category ? `?category=${encodeURIComponent(category)}` : ""}`, quizFetcher, {
    revalidateOnFocus: false,
  });

  const quizzes = data?.items ?? [];
  const categories = useMemo(() => {
    const set = new Set<string>();
    quizzes.forEach((quiz: any) => {
      if (quiz.category) {
        set.add(quiz.category);
      }
    });
    return Array.from(set);
  }, [quizzes]);

  const handleDeleteQuiz = async (quizId: string) => {
    await apiClient.delete(`/quiz/${quizId}`);
    await mutate(`/quiz${category ? `?category=${encodeURIComponent(category)}` : ""}`);
    setExpandedQuiz(null);
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
        </div>

        <header className="page-header">
          <span className="status-pill">Quiz Vault</span>
          <h1 className="page-title">Quiz Generator</h1>
          <p className="page-subtitle">
            Quizzes triggered during agent sessions are saved here. Drill yourself by topic, review answers, and track explanations.
          </p>
        </header>

        {categories.length > 0 && (
          <select
            className="search-input"
            value={category}
            onChange={(event) => setCategory(event.target.value)}
            aria-label="Filter by category"
          >
            <option value="">All categories</option>
            {categories.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
        )}

        <section className="knowledge-list" aria-live="polite">
          {!quizzes.length ? (
            <p className="item-notes">Ask the agent for quiz drills to start building your question bank.</p>
          ) : (
            quizzes.map((quiz: any) => (
              <div key={quiz.id} className="knowledge-group">
                <button
                  type="button"
                  className="knowledge-item"
                  onClick={() => setExpandedQuiz((prev) => (prev === quiz.id ? null : quiz.id))}
                >
                  <h3 className="item-term">{quiz.title}</h3>
                  <p className="item-translation">
                    {quiz.category ?? "uncategorized"} · {new Date(quiz.created_at ?? new Date()).toLocaleString()}
                  </p>
                  <p className="item-notes">{quiz.questions?.length ?? 0} questions</p>
                </button>
                {expandedQuiz === quiz.id && (
                  <div className="detail-card">
                    {quiz.questions?.map((question: any) => (
                      <article key={question.id} className="knowledge-item">
                        <h4 className="item-term">{question.prompt}</h4>
                        {question.options?.length ? (
                          <ul>
                            {question.options.map((option: string, index: number) => (
                              <li key={index}>{option}</li>
                            ))}
                          </ul>
                        ) : null}
                        <p className="item-translation">Answer: {question.answer}</p>
                        {question.explanation && <p className="item-notes">Reasoning: {question.explanation}</p>}
                      </article>
                    ))}
                    <div className="detail-actions">
                      <button type="button" className="danger-button" onClick={() => handleDeleteQuiz(quiz.id)}>
                        Delete Quiz
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </section>
      </div>
    </main>
  );
};

export default QuizPage;
