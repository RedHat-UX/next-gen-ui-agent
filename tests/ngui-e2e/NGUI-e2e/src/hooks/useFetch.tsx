import { useState } from "react";

type RequestConfig = {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: any;
  headers?: Record<string, string>;
};

export function useFetch<T = any>() {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<Error | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async (url: string, config: RequestConfig = {}) => {
    const controller = new AbortController();
    const { method = "GET", body, headers } = config;

    setLoading(true);
    try {
      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
        body: body ? JSON.stringify(body) : body,
        signal: controller.signal,
      });
      if (!res.ok) throw new Error(`Error: ${res.status}`);
      const json = await res.json();
      setData(json);
      setError(null);
      return json;
    } catch (err) {
      if ((err as any).name !== "AbortError") {
        setError(err as Error);
      }
    } finally {
      setLoading(false);
    }
  };

  return { data, error, loading, fetchData };
}
