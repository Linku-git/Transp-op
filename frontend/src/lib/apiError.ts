import type { AxiosError } from 'axios';

interface PydanticDetail {
  msg?: string;
  loc?: string[];
  type?: string;
}

/**
 * Safely extract a human-readable error message from an Axios error.
 *
 * FastAPI / Pydantic v2 can return `detail` as either:
 *   - a plain string  →  return it directly
 *   - an array of `{type, loc, msg, input, ctx}`  →  join the `.msg` fields
 *
 * Rendering the raw object as a React child throws:
 *   "Objects are not valid as a React child (found: object with keys {type, loc, msg, ...})"
 */
export function extractApiError(err: unknown, fallback: string): string {
  const axiosError = err as AxiosError<{ detail?: string | PydanticDetail[] }>;
  const detail = axiosError?.response?.data?.detail;

  if (typeof detail === 'string' && detail.length > 0) return detail;

  if (Array.isArray(detail) && detail.length > 0) {
    return detail
      .map((d) => (typeof d === 'string' ? d : (d.msg ?? JSON.stringify(d))))
      .join('; ');
  }

  return fallback;
}
