import { useEffect, useState } from "react";
import api from "@/lib/api";

export type Product = {
  id: number; name: string; price: string; description?: string; image?: string;
};

export function useProducts() {
  const [data, setData] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get<Product[]>("/products/").then(res => setData(res.data)).finally(() => setLoading(false));
  }, []);

  return { data, loading };
}
