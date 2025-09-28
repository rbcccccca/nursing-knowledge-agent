import Link from "next/link";

const QuizPage = () => {
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
          <span className="status-pill">Coming Soon</span>
          <h1 className="page-title">Quiz Generator</h1>
          <p className="page-subtitle">
            Personalized drills are on the roadmap. Soon you will be able to craft spelling, abbreviation, and scenario questions straight from your glossary.
          </p>
        </header>

        <p className="item-notes">
          For now, keep collecting key terminology with the assistant. Quiz data will be powered by the same glossary you are building.
        </p>
      </div>
    </main>
  );
};

export default QuizPage;
