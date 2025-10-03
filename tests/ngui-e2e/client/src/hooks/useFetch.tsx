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
    setError(null);
    
    try {
      // Validate URL
      if (!url || !url.trim()) {
        throw new Error("URL is required");
      }

      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          ...headers,
        },
        body: body ? JSON.stringify(body) : body,
        signal: controller.signal,
      });
      
      // Handle HTTP errors
      if (!res.ok) {
        let errorMessage = `HTTP ${res.status}: ${res.statusText}`;
        
        try {
          const errorData = await res.json();
          if (errorData.error) {
            errorMessage = errorData.error;
            if (errorData.details) {
              errorMessage += ` - ${errorData.details}`;
            }
          }
        } catch {
          // If response is not JSON, use the default error message
        }
        
        throw new Error(errorMessage);
      }
      
      const json = await res.json();
      
      // Validate response structure
      if (!json) {
        throw new Error("Empty response from server");
      }
      
      setData(json);
      setError(null);
      return json;
      
    } catch (err) {
      if ((err as any).name !== "AbortError") {
        const error = err as Error;
        console.error('Fetch error:', error);
        setError(error);
        
        // Return error object for UI handling
        return {
          error: error.message,
          details: error.message.includes('HTTP') ? 'Server error' : 'Network or parsing error'
        };
      }
    } finally {
      setLoading(false);
    }
  };

  return { data, error, loading, fetchData };
}
