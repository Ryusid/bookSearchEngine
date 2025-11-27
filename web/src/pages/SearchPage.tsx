import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { searchBooks, advancedSearch } from "../api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [regexMode, setRegexMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const navigate = useNavigate();
  const API_BASE = "http://127.0.0.1:8000";

  // -----------------------------
  // 🟢 Fonction de recherche réelle
  // -----------------------------
  const runSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);

    const data = regexMode
      ? await advancedSearch(query, page, pageSize)
      : await searchBooks(query, page, pageSize);

    setResults(data.results || []);
    setTotal(data.total || 0);

    setLoading(false);
  };

  // -----------------------------
  // 🔵 Form submit
  // -----------------------------
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1); // reset to first page
    runSearch();
  };

  // -----------------------------
  // 🔴 Quand la page change → recharger
  // -----------------------------
  useEffect(() => {
    if (query.trim() !== "") runSearch();
  }, [page]);

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "1rem" }}>
      <h1>Book Search Engine</h1>

      {/* SEARCH BAR */}
      <form onSubmit={handleSearch} style={{ marginBottom: "1rem" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={regexMode ? "Enter regex..." : "Enter keyword..."}
          style={{ width: "70%", padding: "0.5rem" }}
        />

        <button type="submit" style={{ marginLeft: "0.5rem" }}>
          Search
        </button>

        <label style={{ marginLeft: "1rem" }}>
          <input
            type="checkbox"
            checked={regexMode}
            onChange={() => {
              setRegexMode(!regexMode);
              setPage(1);
            }}
          />{" "}
          Advanced (Regex)
        </label>
      </form>

      {loading && <p>Loading...</p>}

      {/* RESULTS */}
      {results.map((book) => (
        <div
          key={book.book_id}
          onClick={() => navigate(`/book/${book.book_id}`)}
          style={{
            display: "flex",
            gap: "1rem",
            padding: "1rem",
            borderBottom: "1px solid #ddd",
            cursor: "pointer",
          }}
        >
          {book.cover_url && (
            <img src={`${API_BASE}${book.cover_url}`} style={{ width: 80 }} />
          )}

          <div>
            <h3>{book.title}</h3>
            <p>{book.snippet}</p>
          </div>
        </div>
      ))}

      {/* PAGINATION */}
      {total > pageSize && (
        <div style={{ marginTop: "1rem", display: "flex", gap: "1rem" }}>
          <button disabled={page === 1} onClick={() => setPage(page - 1)}>
            ◀ Prev
          </button>

          <span>
            Page {page} / {Math.ceil(total / pageSize)}
          </span>

          <button
            disabled={page >= Math.ceil(total / pageSize)}
            onClick={() => setPage(page + 1)}
          >
            Next ▶
          </button>
        </div>
      )}
    </div>
  );
}
