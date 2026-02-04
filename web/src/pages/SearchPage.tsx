import { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { searchKeyword, searchTitle, API_BASE } from "../api";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState<"keyword" | "title">("keyword");
  const [advanced, setAdvanced] = useState(false);
  const [rankMode, setRankMode] = useState<"tf" | "pr" | "tfpr">("tf");

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any[]>([]);

  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 20;

  const navigate = useNavigate();
  const location = useLocation();
  const [timing, setTiming] = useState({ backend: null, client: null });

  // -----------------------------------------
  // Restore previous search
  // -----------------------------------------
  useEffect(() => {
    const restore = location.state?.restoredSearch;
    if (restore) {
      setQuery(restore.query);
      setMode(restore.mode);
      setAdvanced(restore.advanced);
      setRankMode(restore.rankMode);
      setPage(restore.page);

      runSearch(
        restore.query,
        restore.mode,
        restore.advanced,
        restore.rankMode,
        restore.page
      );
    }
  }, []);

  const runSearch = async (
    q = query,
    m: "keyword" | "title" = mode,
    adv = advanced,
    rank = rankMode,
    p = page
  ) => {
    if (!q.trim()) return;
    setLoading(true);

    const t0 = performance.now();

    let data;
    if (m === "title") {
      data = await searchTitle(q, p, pageSize);
    } else {
      data = await searchKeyword(q, adv, rank, p, pageSize);
    }
    
    const t1 = performance.now();
    const clientMs = t1 - t0;
    setTiming({backend: data.backend_ms?.toFixed(2), client: clientMs.toFixed(2),});
    setResults(data.results || []);
    setTotal(data.total || 0);
    setLoading(false);
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    runSearch(query, mode, advanced, rankMode, 1);
  };

  useEffect(() => {
    if (query.trim()) {
      runSearch(query, mode, advanced, rankMode, page);
    }
  }, [page]);

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "1rem" }}>
      <h1
        onClick={() => {
          setQuery("");
          setResults([]);
          setTotal(0);
          setPage(1);
          setTiming({});
        }}
        style={{ cursor: "pointer", margin: 20 }}
      >
        Book Search Engine
      </h1>

      {/* SEARCH BAR */}
      <form onSubmit={handleSearch} style={{ marginBottom: "1rem" }}>
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={
            mode === "title"
              ? "Search by title or author..."
              : advanced
              ? "Regex in content..."
              : "Keyword in content..."
          }
          style={{ width: "50%", padding: "0.5rem" }}
        />

        <button type="submit" style={{ marginLeft: "0.5rem"}}>
          Search
        </button>

        <select
          value={mode}
          onChange={(e) => {
            setMode(e.target.value as "keyword" | "title");
            setPage(1);
          }}
          style={{ marginLeft: "1rem", padding: "0.3rem", borderRadius: "10px", background: "#ddd", cursor: "pointer" }}
        >
          <option value="keyword">Keyword</option>
          <option value="title">Title</option>
        </select>

        {mode === "keyword" && (
          <select
            value={rankMode}
            onChange={(e) => {
              setRankMode(e.target.value as any);
              setPage(1);
            }}
            style={{ marginLeft: "1rem", padding: "0.3rem", borderRadius: "10px", background: "#ddd", cursor: "pointer" }}
          >
            <option value="tf">Occurrences (TF)</option>
            <option value="pr">Importance (PageRank)</option>
            <option value="tfpr">Combined (TF × PR)</option>
          </select>
        )}

        {mode === "keyword" && (
          <button
            type="button"
            onClick={() => setAdvanced(!advanced)}
            style={{
              marginLeft: "1rem",
              padding: "0.3rem 0.8rem",
              background: advanced ? "#0059ff" : "#ccc",
              color: "white",
              borderRadius: 6,
              border: "none",
              cursor: "pointer",
            }}
          >
            Regex: {advanced ? "ON" : "OFF"}
          </button>
        )}
      </form>

      {loading && <p>Loading...</p>}

      {timing.backend && (
        <p style={{ color: "#28a", fontSize: "0.9rem" }}>
          Backend Time: {timing.backend} ms — Total Client Time	: {timing.client} ms
        </p>
      )}

      {results.map((book) => (
        <div
          key={book.book_id}
          onClick={() =>
            navigate(`/book/${book.book_id}`, {
              state: {
                fromSearch: {
                  query,
                  page,
                  mode,
                  advanced,
                  rankMode,
                },
              },
            })
          }
          style={{
            display: "flex",
            gap: "1rem",
            padding: "1rem",
            borderBottom: "1px solid #0066ff",
            cursor: "pointer",
          }}
        >
          {book.cover_url && (
            <img
              src={`${API_BASE}${book.cover_url}`}
              style={{
                width: "200px",
                height: "250px",
                margin: "auto",
                objectFit: "contain",
                boxShadow: "0 0 5px -1px black, inset -1px 1px 2px rgba(255, 255, 255, 0.5)",
                borderRadius: "5px",
              }}
            />
          )}

          <div>
            <h3>{book.title}</h3>
            <p>{book.snippet}</p>

            <p style={{ marginTop: 6, color: "#333" }}>
              <b>TF:</b> {book.tf} · <b>PR:</b> {book.pagerank.toFixed(6)}
            </p>


            {book.matched_terms && book.matched_terms.length >= 1 && (() => {
              const max = 10;
              const shown = book.matched_terms.slice(0, max);
              const remaining = book.matched_terms.length - shown.length;

              return (
                <p style={{ fontSize: "0.9rem", color: "#666" }}>
                  Matched terms: {shown.join(", ")}
                  {remaining > 0 ? ` … (+${remaining} more)` : ""}
                </p>
              );
            })()}


            <p style={{ color: "#0077ff" }}>
              Score: {book.score.toFixed(6)}
            </p>
          </div>
        </div>
      ))}

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
