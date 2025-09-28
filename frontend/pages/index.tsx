import Head from "next/head";
import Link from "next/link";

const features = [
  {
    icon: "📚",
    title: "Knowledge Base",
    copy: "Capture core terms, add bilingual context, and keep organized notes in one scroll-friendly hub.",
    href: "/knowledge",
  },
  {
    icon: "🧠",
    title: "AI Assistant",
    copy: "Blend RAG lookups with GPT explanations for fast clarification during study sprints.",
    href: "/dashboard",
  },
  {
    icon: "📝",
    title: "Quiz Generator",
    copy: "Spin up spelling drills, abbreviation reveals, and scenario questions in seconds.",
    href: "/quiz",
  },
];

const HomePage = () => {
  return (
    <>
      <Head>
        <title>Nursing Knowledge Agent</title>
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
      </Head>
      <main className="page-shell">
        <div className="page-card">
          <header className="page-header">
            <span className="status-pill">Study Companion</span>
            <h1 className="page-title">Nursing Knowledge Agent</h1>
            <p className="page-subtitle">
              Bite-size explanations, bilingual terminology, and adaptive quizzes designed for busy clinical schedules.
            </p>
          </header>

          <div className="feature-list">
            {features.map(({ icon, title, copy, href }) => (
              <Link href={href} key={title} className="feature-card" aria-label={`Open ${title}`}>
                <div className="feature-icon" aria-hidden>
                  {icon}
                </div>
                <h2 className="feature-title">{title}</h2>
                <p className="feature-copy">{copy}</p>
              </Link>
            ))}
          </div>

          <Link href="/dashboard" className="primary-button" aria-label="Open nursing study dashboard">
            Enter Dashboard →
          </Link>

          <p className="footer-note">Works beautifully on iPhone — add it to your home screen for quick review sessions.</p>
        </div>
      </main>
    </>
  );
};

export default HomePage;
