import client from "./client";
import type { APIPermission, APIVersion, DashboardData, HTTPMethod, MockAPI, PageResponse, RequestLog, RequestSchema, ResponseScenario, ResponseTemplate, TokenResponse, User } from "../types";

export const authApi = {
  register: (data: { email: string; password: string; full_name: string }) => client.post<User>("/api/v1/auth/register", data),
  login: (data: { email: string; password: string }) => client.post<TokenResponse>("/api/v1/auth/login", data),
  me: () => client.get<User>("/api/v1/auth/me"),
};

export const mockApi = {
  list: (params?: { page?: number; page_size?: number; http_method?: HTTPMethod; is_active?: boolean; is_private?: boolean }) => client.get<PageResponse<MockAPI>>("/api/v1/mock-apis", { params }),
  get: (id: string) => client.get<MockAPI>(`/api/v1/mock-apis/${id}`),
  create: (data: { name: string; description?: string | null; base_path: string; http_method: HTTPMethod; is_private: boolean }) => client.post<MockAPI>("/api/v1/mock-apis", data),
  update: (id: string, data: Partial<{ name: string; description: string | null; base_path: string; http_method: HTTPMethod; is_private: boolean; is_active: boolean }>) => client.patch<MockAPI>(`/api/v1/mock-apis/${id}`, data),
  remove: (id: string) => client.delete(`/api/v1/mock-apis/${id}`),
  activate: (id: string) => client.post<MockAPI>(`/api/v1/mock-apis/${id}/activate`),
  deactivate: (id: string) => client.post<MockAPI>(`/api/v1/mock-apis/${id}/deactivate`),
};

export const versionApi = {
  list: (mockId: string, params?: { page?: number; page_size?: number; is_active?: boolean }) => client.get<PageResponse<APIVersion>>(`/api/v1/mock-apis/${mockId}/versions`, { params }),
  get: (mockId: string, versionId: string) => client.get<APIVersion>(`/api/v1/mock-apis/${mockId}/versions/${versionId}`),
  create: (mockId: string, data: { version: string; is_active?: boolean }) => client.post<APIVersion>(`/api/v1/mock-apis/${mockId}/versions`, data),
  update: (mockId: string, versionId: string, data: { is_active?: boolean }) => client.patch<APIVersion>(`/api/v1/mock-apis/${mockId}/versions/${versionId}`, data),
  remove: (mockId: string, versionId: string) => client.delete(`/api/v1/mock-apis/${mockId}/versions/${versionId}/request-schema`),
};

export const schemaApi = {
  get: (mockId: string, versionId: string) => client.get<RequestSchema>(`/api/v1/mock-apis/${mockId}/versions/${versionId}/request-schema`),
  create: (mockId: string, versionId: string, data: Omit<RequestSchema, "id" | "api_version_id" | "created_at" | "updated_at">) => client.post<RequestSchema>(`/api/v1/mock-apis/${mockId}/versions/${versionId}/request-schema`, data),
  update: (mockId: string, versionId: string, data: Partial<Omit<RequestSchema, "id" | "api_version_id" | "created_at" | "updated_at">>) => client.patch<RequestSchema>(`/api/v1/mock-apis/${mockId}/versions/${versionId}/request-schema`, data),
  remove: (mockId: string, versionId: string) => client.delete(`/api/v1/mock-apis/${mockId}/versions/${versionId}/request-schema`),
};

export const scenarioApi = {
  list: (mockId: string, versionId: string, params?: { page?: number; page_size?: number }) => client.get<PageResponse<ResponseTemplate>>(`/api/v1/mock-apis/${mockId}/versions/${versionId}/scenarios`, { params }),
  create: (mockId: string, versionId: string, data: { scenario: ResponseScenario; status_code: number; headers: Record<string, string>; body: unknown; delay_ms: number }) => client.post<ResponseTemplate>(`/api/v1/mock-apis/${mockId}/versions/${versionId}/scenarios`, data),
  update: (mockId: string, versionId: string, scenarioId: string, data: Partial<{ status_code: number; headers: Record<string, string>; body: unknown; delay_ms: number }>) => client.patch<ResponseTemplate>(`/api/v1/mock-apis/${mockId}/versions/${versionId}/scenarios/${scenarioId}`, data),
  remove: (mockId: string, versionId: string, scenarioId: string) => client.delete(`/api/v1/mock-apis/${mockId}/versions/${versionId}/scenarios/${scenarioId}`),
};

export const permissionApi = {
  list: (mockId: string, params?: { page?: number; page_size?: number }) => client.get<PageResponse<APIPermission>>(`/api/v1/mock-apis/${mockId}/permissions`, { params }),
  create: (mockId: string, data: { user_id: string; permission: "view" | "execute" | "manage" }) => client.post<APIPermission>(`/api/v1/mock-apis/${mockId}/permissions`, data),
  update: (mockId: string, permissionId: string, permission: "view" | "execute" | "manage") => client.patch<APIPermission>(`/api/v1/mock-apis/${mockId}/permissions/${permissionId}`, { permission }),
  remove: (mockId: string, permissionId: string) => client.delete(`/api/v1/mock-apis/${mockId}/permissions/${permissionId}`),
};

export const logsApi = {
  list: (mockId: string, versionId: string, params?: { page?: number; page_size?: number; response_status?: number; http_method?: string; start_time?: string; end_time?: string }) => client.get<PageResponse<RequestLog>>(`/api/v1/mock-apis/${mockId}/versions/${versionId}/logs`, { params }),
};

export const dashboardApi = { get: () => client.get<DashboardData>("/api/v1/dashboard") };

export type { HTTPMethod, ResponseScenario } from "../types";
