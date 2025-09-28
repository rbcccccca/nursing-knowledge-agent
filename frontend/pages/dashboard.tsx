import { useEffect, useState } from "react";
import useSWR from "swr";

import { apiClient } from "../services/apiClient";

const fetcher = (url: string) => apiClient.get(url).then((res) => res.data);

const DashboardPage = () => {
  const { data: health } = useSWR("/health", fetcher);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<string>("");

  useEffect(() => {
    if (health) {
      console.log("API health", health);
    }
  }, [health]);

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const response = await apiClient.post("/agent/query", { query });
    setResult(response.data?.answer ?? "No response yet");
  };

  return (
    <main className="mx-auto max-w-3xl px-4 py-10 space-y-8">
      <section>
        <h1 className="text-2xl font-semibold">Study Dashboard</h1>
        <p className="text-sm text-slate-500">Check API health and ask quick questions.</p>
      </section>
      <section>
        <h2 className="text-xl font-medium">Agent Quick Query</h2>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <textarea
            className="w-full rounded border border-slate-300 p-2"
            rows={4}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Describe the nursing concept you want explained"
          />
          <button type="submit" className="rounded bg-blue-600 px-4 py-2 text-white">
            Ask Agent
          </button>
        </form>
        {result && (
          <article className="mt-4 rounded border border-slate-200 bg-slate-50 p-4">
            <h3 className="text-lg font-medium">Agent Response</h3>
            <p className="whitespace-pre-wrap text-sm text-slate-700">{result}</p>
          </article>
        )}
      </section>
    </main>
  );
};

export default DashboardPage;
