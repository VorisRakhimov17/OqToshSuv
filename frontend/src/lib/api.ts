import axios from "axios";

const api = axios.create({
  //baseURL: "https://api.oqtoshsuv.uz/api",
  baseURL: import.meta.env.VITE_API_URL
});

export default api;