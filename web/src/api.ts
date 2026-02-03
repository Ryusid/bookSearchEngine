import axios from "axios";


declare global {
  interface Window {
    __ENV__?: { API_BASE?: string };
  }
}

export const API_BASE = window.__ENV__?.API_BASE || "/api";



export async function searchTitle(q: string, page: number, page_size: number) {
  return (
    await axios.get(`${API_BASE}/search-title`, {
      params: { q, page, page_size },
    })
  ).data;
}

export async function searchKeyword(
  q: string,
  advanced: boolean,
  rank_mode: string,
  page: number,
  page_size: number
) {
  return (
    await axios.get(`${API_BASE}/search-keyword`, {
      params: { q, advanced, rank_mode, page, page_size },
    })
  ).data;
}

export async function getBook(id: string) {
  return (await axios.get(`${API_BASE}/book/${encodeURIComponent(id)}`)).data;
}

export async function getRecommendations(id: string) {
  return (await axios.get(`${API_BASE}/recommend/${id}`)).data;
}

export async function getBookPage(id: string, page: number) {
  return (
    await axios.get(`${API_BASE}/book-page/${id}`, {
      params: { page },
    })
  ).data;
}
