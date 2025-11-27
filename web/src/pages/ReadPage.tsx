import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";

export default function ReadPage() {
  const { id } = useParams();
  const [page, setPage] = useState(1);
  const [pageData, setPageData] = useState<any>(null);

  const [dark, setDark] = useState(false);
  const [fontSize, setFontSize] = useState(18);

  const API_BASE = "http://127.0.0.1:8000";

  useEffect(() => {
    axios
      .get(`${API_BASE}/book-page/${id}`, { params: { page, size: 4000 } })
      .then((res) => setPageData(res.data));
  }, [id, page]);

  if (!pageData) return <p>Loading...</p>;

  const totalPages = pageData.total_pages;

  return (
    <div
      style={{
        minHeight: "100vh",
        padding: "1rem",
        background: dark ? "#111" : "#f7f7f7",
        color: dark ? "#eee" : "#222",
        transition: "0.3s background, 0.3s color",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "1rem" }}>
        <Link
          to={`/book/${id}`}
          style={{
            color: dark ? "#9dc1ff" : "#0066cc",
            textDecoration: "none",
            fontSize: "1rem",
          }}
        >
          <button>← Back to details</button>
        </Link>
      </div>

      {/* Title */}
      <h1 style={{ textAlign: "center", marginBottom: "1rem" }}>
        {pageData.title}
      </h1>

      {/* Controls */}
      <div
        style={{
          display: "flex",
          justifyContent: "center",
          gap: "1rem",
          marginBottom: "1rem",
        }}
      >
        <button onClick={() => setFontSize((f) => f - 2)}>A−</button>
        <span>Font size: {fontSize}px</span>
        <button onClick={() => setFontSize((f) => f + 2)}>A+</button>

        <button onClick={() => setDark((v) => !v)}>
          {dark ? "☀ Light Mode" : "🌙 Dark Mode"}
        </button>
      </div>

      {/* Content */}
      <div
        style={{
          maxWidth: "750px",
          margin: "auto",
          padding: "2rem",
          background: dark ? "#1a1a1a" : "#fff",
          borderRadius: "8px",
          boxShadow: dark
            ? "0 0 10px rgba(255,255,255,0.05)"
            : "0 0 10px rgba(0,0,0,0.08)",
          whiteSpace: "pre-wrap",
          lineHeight: "1.8",
          fontSize: `${fontSize}px`,
          fontFamily: "'Merriweather', serif",
          transition: "0.2s all",
        }}
      >
        {pageData.text}
      </div>

      {/* Footer Navigation */}
      <div
        style={{
          textAlign: "center",
          marginTop: "2rem",
        }}
      >
        <p>
          Page {page} / {totalPages}
        </p>

        <button
          disabled={page <= 1}
          onClick={() => setPage((p) => p - 1)}
          style={{ marginRight: "1rem" }}
        >
          ⬅ Previous
        </button>

        <button
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          Next ➡
        </button>
      </div>
    </div>
  );
}
