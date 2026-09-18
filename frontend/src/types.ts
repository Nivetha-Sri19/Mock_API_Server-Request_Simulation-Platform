export type HTTPMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE" | "HEAD" | "OPTIONS";
export type ResponseScenario = "success" | "validation_error" | "unauthorized" | "not_found" | "server_error" | "custom";

export interface User { id: string; email: string; full_name: string; role: string; is_active: boolean; }
export interface MockAPI { id: string; user_id: string; name: string; description: string | null; base_path: string; http_method: HTTPMethod; is_active: boolean; is_private: boolean; created_at: string; updated_at: string; }
export interface APIVersion { id: string; mock_api_id: string; version: string; is_active: boolean; created_at: string; updated_at: string; }
export interface ParameterDefinition { name: string; type: string; required: boolean; description?: string | null; default?: unknown; example?: unknown; }
export interface RequestSchema { id: string; api_version_id: string; query_parameters: ParameterDefinition[] | null; path_parameters: ParameterDefinition[] | null; headers: ParameterDefinition[] | null; body_schema: Record<string, unknown> | null; created_at: string; updated_at: string; }
export interface ResponseTemplate { id: string; api_version_id: string; scenario: ResponseScenario; status_code: number; headers: Record<string, string> | null; body: unknown; delay_ms: number; created_at: string; updated_at: string; }
export interface APIPermission { id: string; mock_api_id: string; user_id: string; permission: "view" | "execute" | "manage"; created_at: string; updated_at: string; }
export interface RequestLog { id: string; api_version_id: string; endpoint: string; http_method: HTTPMethod; request_parameters: Record<string, unknown> | null; request_headers: Record<string, unknown> | null; request_body: unknown; response_status: number; response_time_ms: number; timestamp: string; }
export interface DashboardSummary { total_mock_apis: number; active_mock_apis: number; total_requests: number; error_requests: number; average_response_time_ms: number; }
export interface MostUsedEndpoint { api_version_id: string; endpoint: string; http_method: string; request_count: number; }
export interface DashboardData { summary: DashboardSummary; most_used_endpoints: MostUsedEndpoint[]; generated_at: string; }
export interface PageResponse<T> { items: T[]; page: number; page_size: number; total: number; total_pages: number; }
export interface TokenResponse { access_token: string; token_type: string; expires_in: number; }
