export function getErrorMessage(error: unknown): string {
  const e = error as { response?: { data?: { error?: { message?: string }; detail?: string } } };
  return e?.response?.data?.error?.message || e?.response?.data?.detail || "Something went wrong.";
}
export function methodColor(method: string) {
  const map: Record<string, string> = { GET: "#35e28b", POST: "#00d4ff", PUT: "#ffb020", PATCH: "#b8ff3d", DELETE: "#ff4d6d", HEAD: "#9d8cff", OPTIONS: "#8d98a8" };
  return map[method] || "#8d98a8";
}
export function formatDate(value?: string) { return value ? new Date(value).toLocaleString() : "—"; }
export function formatNumber(value: unknown) { return Number(value ?? 0).toLocaleString(); }
export function formatMs(value: unknown) { return `${Number(value ?? 0).toFixed(2)} ms`; }
export function downloadJson(name: string, data: unknown) { const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }); const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = name; a.click(); URL.revokeObjectURL(url); }
export function prettyBody(body: unknown) { return typeof body === "string" ? body : JSON.stringify(body ?? null, null, 2); }
