"use client";

import { useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

type Endpoint = {
  label: string;
  method: "GET";
  path: string;
};

const ENDPOINTS: Endpoint[] = [
  { label: "Service banner", method: "GET", path: "/" },
  { label: "Health check", method: "GET", path: "/health" },
  { label: "Current user (auth)", method: "GET", path: "/api/v1/auth/me" },
  { label: "Get CV by id", method: "GET", path: "/api/v1/extraction/cv/demo-cv-id" },
  {
    label: "Render template PDF",
    method: "GET",
    path: "/api/v1/optimization/render_template_pdf?cv_id=demo-cv-id&template=harvard",
  },
  {
    label: "Job recommendations",
    method: "GET",
    path: "/api/v1/jobs/recommendations/demo-cv-id",
  },
  {
    label: "Interview health",
    method: "GET",
    path: "/api/v1/interview/health",
  },
  {
    label: "Interview report",
    method: "GET",
    path: "/api/v1/interview/sessions/demo-session-id/report",
  },
];

type CallResult = {
  status: number | null;
  body: string;
  error?: string;
};

export default function Home() {
  const [results, setResults] = useState<Record<string, CallResult>>({});
  const [loading, setLoading] = useState<string | null>(null);

  async function call(endpoint: Endpoint) {
    setLoading(endpoint.path);
    try {
      const res = await fetch(`${API_BASE}${endpoint.path}`, {
        method: endpoint.method,
      });
      const text = await res.text();
      let pretty = text;
      try {
        pretty = JSON.stringify(JSON.parse(text), null, 2);
      } catch {
        // not JSON, leave as-is
      }
      setResults((prev) => ({
        ...prev,
        [endpoint.path]: { status: res.status, body: pretty },
      }));
    } catch (err) {
      setResults((prev) => ({
        ...prev,
        [endpoint.path]: {
          status: null,
          body: "",
          error: err instanceof Error ? err.message : String(err),
        },
      }));
    } finally {
      setLoading(null);
    }
  }

  return (
    <main
      style={{
        maxWidth: 880,
        margin: "0 auto",
        padding: "48px 20px 80px",
      }}
    >
      <header style={{ marginBottom: 32 }}>
        <h1 style={{ margin: 0, fontSize: 28, fontWeight: 600 }}>
          LancerAI
        </h1>
        <p style={{ color: "var(--muted)", marginTop: 8 }}>
          Gọi thử các <strong>GET</strong> tới backend tại{" "}
          <code>{API_BASE}</code>. Phản hồi phụ thuộc trạng thái triển khai từng
          endpoint.
        </p>
      </header>

      <section style={{ display: "grid", gap: 12 }}>
        {ENDPOINTS.map((ep) => {
          const result = results[ep.path];
          const isLoading = loading === ep.path;
          return (
            <div
              key={ep.path}
              style={{
                border: "1px solid var(--border)",
                background: "var(--card)",
                borderRadius: 10,
                padding: 16,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: 12,
                }}
              >
                <div>
                  <div style={{ fontWeight: 600 }}>{ep.label}</div>
                  <div
                    style={{
                      color: "var(--muted)",
                      fontFamily:
                        "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace",
                      fontSize: 13,
                    }}
                  >
                    {ep.method} {ep.path}
                  </div>
                </div>
                <button
                  onClick={() => call(ep)}
                  disabled={isLoading}
                  style={{
                    background: "var(--accent)",
                    color: "white",
                    border: "none",
                    borderRadius: 8,
                    padding: "8px 14px",
                    opacity: isLoading ? 0.6 : 1,
                  }}
                >
                  {isLoading ? "Loading..." : "Call"}
                </button>
              </div>

              {result && (
                <pre
                  style={{
                    marginTop: 12,
                    background: "#0a0d11",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                    padding: 12,
                    overflowX: "auto",
                    fontSize: 12.5,
                    lineHeight: 1.45,
                  }}
                >
                  {result.error
                    ? `error: ${result.error}`
                    : `status: ${result.status}\n\n${result.body}`}
                </pre>
              )}
            </div>
          );
        })}
      </section>

      <footer style={{ color: "var(--muted)", fontSize: 12, marginTop: 40 }}>
        Thiết lập URL API: <code>NEXT_PUBLIC_API_BASE_URL</code> (ví dụ trong{" "}
        <code>.env.local</code>).
      </footer>
    </main>
  );
}
