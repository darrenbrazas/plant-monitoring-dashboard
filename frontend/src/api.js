import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function getData() {
  const response = await axios.get(`${API_URL}/data`);
  return response.data;
}
