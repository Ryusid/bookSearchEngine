import { useEffect, useState } from "react";
import {
  useParams,
  useNavigate,
  useLocation,
  Link,
} from "react-router-dom";
import { getBook, getRecommendations, API_BASE } from "../api";

export default function BookPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();

  const [book, setBook] = useState<any>(null);
  const [recs, setRecs] = useState<any[]>([]);


  useEffect(() => {
    getBook(id!).then(setBook);
    getRecommendations(id!).then((data) => setRecs(data.recommendations));
  }, [id]);

  if (!book) return <p>Loading...</p>;

  // ========== BACK BUTTON LOGIC ==========
  const handleBack = () => {
    const s = location.state;
    // Case 1 : came from another book
    if (s?.savedState) {
      if (s?.fromBook) {
        return navigate(`/book/${s.fromBook}`, { replace: true,
          state: { savedState : s.savedState },});
      }
      if (s.savedState?.fromBook) {
         return navigate(`/book/${s.savedState.fromBook}`, { replace: true,
          state: { savedState : s.savedState.savedState },});
      }
      return navigate("/", {
        replace: true,
        state: { restoredSearch: s.savedState.fromSearch },
      });
    }

    // Case 2 : came directly from search
    if (s?.fromSearch) {
      return navigate("/", {
        replace : true, 
        state : { restoredSearch : s.fromSearch },
      });
    } 
    // Safe fallback
    navigate("/");
  };

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "1rem" }}>
      <button onClick={handleBack}>← Back</button>
      <h1>{book.title}</h1>
      <h3 style={{textAlign: "center"}}>{book.authors}</h3>
      <div
        style={{
          display: "flex",
          gap: "1rem",
          marginTop: "1.5rem",
          marginBottom: "1.5rem",
        }}
      >
        {book.cover_url && (
          <img
            src={`${API_BASE}${book.cover_url}`}
            style={{
              width: 200,
              height: "auto",
              objectFit: "contain",
              borderRadius: 4,
            }}
          />
        )}

        <p style={{ fontSize: "0.9rem", lineHeight: "1.6" }}>{book.summary || "No summary available/"}</p>
      </div>

      <button
        onClick={()=> navigate(`/read/${id}`, {state : {readState : location.state,},})}
        style={{
          padding: "0.5rem 1rem",
          display: "inline-block",
          background: "#0077ff",
          color: "white",
          borderRadius: 10,
        }}
      >
        📖 Read this book
      </button>

      <h2 style={{ marginTop: "2rem" }}>📚 Similar Books</h2>

      {recs.map((b) => (
        <div
          key={b.book_id}
          onClick={() =>
            navigate(`/book/${b.book_id}`, {
              state: {
                fromBook: id,
                savedState: location.state, // ONLY this for recommendations
              },
            })
          }
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
              style={{
                width: 80,
                height: "auto",
                objectFit: "contain",
                borderRadius: 4,
              }}
            />
          )}

          <div>
            <h3>{b.title}</h3>
            <p style={{ color: "#555" }}>Similarity: {b.score.toFixed(4)}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
