import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { getBook, getRecommendations, getPageRankRecommendations } from "../api";

export default function BookPage() {
  const { id } = useParams();
  const [book, setBook] = useState<any>(null);

  const [recsJaccard, setRecsJaccard] = useState<any[]>([]);
  const [recsPageRank, setRecsPageRank] = useState<any[]>([]);

  const API_BASE = "http://127.0.0.1:8000";

  useEffect(() => {
    getBook(id!).then(setBook);

    getRecommendations(id!).then((data) =>
      setRecsJaccard(data.recommendations)
    );

    getPageRankRecommendations(id!).then((data) =>
      setRecsPageRank(data.recommendations)
    );
  }, [id]);

  if (!book) return <p>Loading...</p>;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "1rem" }}>
      <Link to="/">
        <button>← Back</button>
      </Link>

      <h1>{book.title}</h1>

      {/* Cover + snippet */}
      <div
        style={{
          display: "flex",
          gap: "1rem",
          alignItems: "flex-start",
          marginTop: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        {book.cover_url && (
          <img
            src={`${API_BASE}${book.cover_url}`}
            style={{ width: 200, borderRadius: 4 }}
          />
        )}

        <p style={{ fontSize: "1rem", lineHeight: "1.6" }}>{book.snippet}</p>
      </div>

      {/* Read button */}
      <Link
        to={`/read/${id}`}
        style={{
          padding: "0.5rem 1rem",
          display: "inline-block",
          background: "#0077ff",
          color: "white",
          borderRadius: 10,
        }}
      >
        📖 Read this book
      </Link>

      {/* --- Similar Books (Jaccard) --- */}
      <h2 style={{ marginTop: "2rem" }}>📚 Similar Books</h2>
      <RecommendationList items={recsJaccard} />

      {/* --- PageRank global recommendations --- */}
      <h2 style={{ marginTop: "2rem" }}>⭐ Top Global Recommendations</h2>
      <RecommendationList items={recsPageRank} />
    </div>
  );
}

// -------------------
// Shared component for the 2 lists
// -------------------
function RecommendationList({ items }: { items: any[] }) {
  const API_BASE = "http://127.0.0.1:8000";

  return (
    <div>
      {items.map((b) => (
        <div
          key={b.filename}
          onClick={() => (window.location.href = `/book/${b.filename}`)}
          style={{
            display: "flex",
            gap: "1rem",
            padding: "0.5rem 0",
            borderBottom: "1px solid #ddd",
            cursor: "pointer",
          }}
        >
          {b.cover_url && (
            <img
              src={`${API_BASE}${b.cover_url}`}
              style={{ width: 80, borderRadius: 4 }}
            />
          )}

          <div>
            <h3>{b.title}</h3>
            <p style={{ color: "#555" }}>Score: {b.score.toFixed(4)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
