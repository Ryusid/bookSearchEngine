import axios from "axios";
import { API_BASE } from "./config";

export async function searchKeyword(q: string, advanced: boolean, rankMode: string, page: number, pageSize: number) {
  return (await axios.get(`${API_BASE}/search-keyword`, {
    params: { q, advanced, rank_mode: rankMode, page, page_size: pageSize },
  })).data;
}

export async function searchTitle(q: string, page: number, pageSize: number) {
  return (await axios.get(`${API_BASE}/search-title`, {
    params: { q, page, page_size: pageSize },
  })).data;
}

export async function getBook(id: string) {
  return (await axios.get(`${API_BASE}/book/${id}`)).data;
}

export async function getRecommendations(id: string) {
  return (await axios.get(`${API_BASE}/recommend/${id}`)).data;
}

export async function getBookPage(id: string, page: number) {
  return (await axios.get(`${API_BASE}/book-page/${id}`, {
    params: { page },
  })).data;
}
