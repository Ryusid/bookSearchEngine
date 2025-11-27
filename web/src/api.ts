// web/src/api.ts
import axios from "axios";

const API_BASE = "http://localhost:8000";

export async function searchBooks(q: string, page: number, page_size: number) {
  const res = await axios.get(`${API_BASE}/search`, {
    params: { q, page, page_size },
  });
  return res.data;
}


export async function advancedSearch(regex: string, page: number, page_size: number) {
  const res = await axios.get(`${API_BASE}/advanced-search`, {
    params: { regex, page, page_size },
  });
  return res.data;
}
export async function getBook(id: string) {
  const res = await axios.get(`${API_BASE}/book/${encodeURIComponent(id)}`);
  return res.data;
}

export async function getRecommendations(filename: string) {
  const res = await axios.get(`${API_BASE}/recommend/${filename}`);
  return res.data;
}

export async function getPageRankRecommendations(filename: string) {
  const res = await axios.get(`${API_BASE}/recommend-pagerank/${filename}`);
  return res.data;
}
