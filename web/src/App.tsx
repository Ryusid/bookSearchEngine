// web/src/App.tsx
import { Routes, Route } from "react-router-dom";
import SearchPage from "./pages/SearchPage";
import BookPage from "./pages/BookPage";
import ReadPage from "./pages/ReadPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<SearchPage />} />
      <Route path="/book/:id" element={<BookPage />} />
      <Route path="/read/:id" element={<ReadPage />} />
    </Routes>
  );
}
