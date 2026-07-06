/**
 * CityPilot AI — Centralized API Client
 *
 * All API calls in the app must import API_BASE from this module.
 * Set VITE_API_URL in:
 *   - Local dev:    frontend/.env.local → VITE_API_URL=http://localhost:8000
 *   - Vercel prod:  Environment Variables → VITE_API_URL=https://<your>.onrender.com
 */

/** Base URL for the FastAPI backend. Falls back to localhost for local development. */
export const API_BASE: string =
  (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ??
  "http://localhost:8000";

/**
 * Typed wrapper around fetch that prepends API_BASE to every path.
 *
 * @param path    Relative path, e.g. "/analyze"
 * @param init    Standard RequestInit options
 * @returns       Parsed JSON response as T
 * @throws        Error with a human-readable message on HTTP or network failure
 */
export async function apiFetch<T = unknown>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const url = `${API_BASE}${path}`;
  let response: Response;

  try {
    response = await fetch(url, init);
  } catch (networkErr) {
    throw new Error(
      `Network error connecting to CityPilot backend at ${url}. ` +
      `Ensure the backend is running and VITE_API_URL is set correctly.`
    );
  }

  if (!response.ok) {
    throw new Error(`Server error ${response.status} on ${url}`);
  }

  return response.json() as Promise<T>;
}
