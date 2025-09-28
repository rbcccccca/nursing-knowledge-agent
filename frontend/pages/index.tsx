import Head from "next/head";
import Link from "next/link";

const HomePage = () => {
  return (
    <>
      <Head>
        <title>Nursing Knowledge Agent</title>
      </Head>
      <main className="mx-auto max-w-3xl px-4 py-12">
        <h1 className="text-3xl font-semibold">Nursing Knowledge Agent</h1>
        <p className="mt-4 text-slate-600">
          Centralize your terms, run RAG-powered searches, and generate targeted quizzes to stay prepared for exams.
        </p>
        <section className="mt-10 space-y-6">
          <div>
            <h2 className="text-xl font-medium">Knowledge Base</h2>
            <p className="text-sm text-slate-500">
              Upload PDFs or add manual terms, review bilingual definitions, and attach personalized notes.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-medium">AI Assistant</h2>
            <p className="text-sm text-slate-500">
              Ask questions and let the agent orchestrate Supabase, Qdrant, and GPT responses.
            </p>
          </div>
          <div>
            <h2 className="text-xl font-medium">Quiz Generator</h2>
            <p className="text-sm text-slate-500">
              Practice spelling, abbreviations, and usage with adaptive feedback.
            </p>
          </div>
        </section>
        <Link href="/dashboard" className="mt-10 inline-block rounded bg-blue-600 px-4 py-2 text-white">
          Enter Dashboard
        </Link>
      </main>
    </>
  );
};

export default HomePage;
