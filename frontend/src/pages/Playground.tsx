import { useEffect, useMemo, useState } from "react";
import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  MenuItem,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import { useSearchParams } from "react-router-dom";
import PageHeader from "../components/PageHeader";
import { mockApi, versionApi } from "../api";
import type { APIVersion, MockAPI } from "../types";
import { getErrorMessage, prettyBody } from "../utils";

function SendIcon() {
  return (
    <Box
      component="svg"
      viewBox="0 0 24 24"
      sx={{
        width: 20,
        height: 20,
        fill: "none",
        stroke: "currentColor",
        strokeWidth: 1.8,
        strokeLinecap: "round",
        strokeLinejoin: "round",
      }}
    >
      <path d="m22 2-7 20-4-9-9-4Z" />
      <path d="M22 2 11 13" />
    </Box>
  );
}

function BulkIcon() {
  return (
    <Box
      component="svg"
      viewBox="0 0 24 24"
      sx={{
        width: 20,
        height: 20,
        fill: "none",
        stroke: "currentColor",
        strokeWidth: 1.8,
        strokeLinecap: "round",
        strokeLinejoin: "round",
      }}
    >
      <rect x="4" y="4" width="6" height="6" rx="1" />
      <rect x="14" y="4" width="6" height="6" rx="1" />
      <rect x="4" y="14" width="6" height="6" rx="1" />
      <rect x="14" y="14" width="6" height="6" rx="1" />
    </Box>
  );
}

type Result = {
  status: number;
  body: unknown;
  headers: Record<string, string>;
  responseTime: number;
};

export default function Playground() {
  const [params] = useSearchParams();

  const [apis, setApis] = useState<MockAPI[]>([]);
  const [versions, setVersions] = useState<APIVersion[]>([]);

  const [apiId, setApiId] = useState(params.get("apiId") || "");
  const [versionId, setVersionId] = useState(
    params.get("versionId") || "",
  );

  const [path, setPath] = useState("");
  const [query, setQuery] = useState("");

  const [headers, setHeaders] = useState(
    '{\n  "Content-Type": "application/json"\n}',
  );

  const [body, setBody] = useState("{}");
  const [scenario, setScenario] = useState("success");

  const [result, setResult] = useState<Result | null>(null);
  const [error, setError] = useState("");

  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [bulkSending, setBulkSending] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const response = await mockApi.list({
          page: 1,
          page_size: 100,
        });

        setApis(response.data.items);

        if (!apiId && response.data.items[0]) {
          setApiId(response.data.items[0].id);
        }
      } catch (e) {
        setError(getErrorMessage(e));
      } finally {
        setLoading(false);
      }
    };

    void load();
  }, []);

  useEffect(() => {
    if (!apiId) {
      setVersions([]);
      return;
    }

    const load = async () => {
      try {
        const response = await versionApi.list(apiId, {
          page: 1,
          page_size: 100,
        });

        setVersions(response.data.items);

        const currentVersion = params.get("versionId");

        const selected =
          currentVersion &&
          response.data.items.some((item) => item.id === currentVersion)
            ? currentVersion
            : response.data.items.find((item) => item.is_active)?.id ||
              response.data.items[0]?.id ||
              "";

        setVersionId(selected);
      } catch (e) {
        setError(getErrorMessage(e));
      }
    };

    void load();
  }, [apiId]);

  const api = useMemo(
    () => apis.find((item) => item.id === apiId),
    [apis, apiId],
  );

  useEffect(() => {
    if (api) {
      setPath(`/mock${api.base_path}`);
    }
  }, [api]);

  const version = versions.find((item) => item.id === versionId);

  const executeRequest = async (): Promise<Result | null> => {
    try {
      let parsedBody: unknown = undefined;

      if (body.trim()) {
        try {
          parsedBody = JSON.parse(body);
        } catch {
          setError("Request body must be valid JSON.");
          return null;
        }
      }

      let headerObject: Record<string, string> = {};

      try {
        headerObject = JSON.parse(headers || "{}");
      } catch {
        setError("Request headers must be valid JSON.");
        return null;
      }

      const qs = new URLSearchParams(query);

      if (scenario && scenario !== "success") {
        qs.set("__scenario", scenario);
      }

      const base =
        import.meta.env.VITE_API_BASE_URL ||
        "http://127.0.0.1:8000";

      const url =
        `${base.replace(/\/$/, "")}` +
        `${path.startsWith("/") ? path : `/${path}`}` +
        `${qs.toString() ? `?${qs.toString()}` : ""}`;

      const token =
        localStorage.getItem("mockpilot_token") ||
        localStorage.getItem("mockforge_token");

      if (token) {
        headerObject.Authorization = `Bearer ${token}`;
      }

      const method = api?.http_method || "GET";

      const started = performance.now();

      const response = await fetch(url, {
        method,
        headers: headerObject,
        body: ["GET", "HEAD", "OPTIONS", "DELETE"].includes(method)
          ? undefined
          : JSON.stringify(parsedBody ?? {}),
      });

      const responseTime = performance.now() - started;

      const contentType =
        response.headers.get("content-type") || "";

      const responseBody = contentType.includes("application/json")
        ? await response.json()
        : await response.text();

      const responseHeaders: Record<string, string> = {};

      response.headers.forEach((value, key) => {
        responseHeaders[key] = value;
      });

      return {
        status: response.status,
        body: responseBody,
        headers: responseHeaders,
        responseTime,
      };
    } catch (e) {
      setError(getErrorMessage(e));
      return null;
    }
  };

  const execute = async () => {
    if (!api || !path.trim()) {
      return;
    }

    setError("");
    setResult(null);
    setSending(true);

    try {
      const response = await executeRequest();

      if (response) {
        setResult(response);
      }
    } finally {
      setSending(false);
    }
  };

  const sendTenRequests = async () => {
    if (!api || !path.trim()) {
      return;
    }

    setError("");
    setResult(null);
    setBulkSending(true);

    try {
      let lastResult: Result | null = null;

      for (let index = 0; index < 10; index += 1) {
        const response = await executeRequest();

        if (response) {
          lastResult = response;
          setResult(response);
        } else {
          break;
        }
      }
    } finally {
      setBulkSending(false);
    }
  };

  return (
    <Box
      sx={{
        p: {
          xs: 2.5,
          md: 5,
        },
      }}
    >
      <PageHeader
        eyebrow="API SIMULATOR / REQUEST LAB"
        title="Request Lab"
        subtitle="Build a real HTTP request and send it to the backend's catch-all /mock runtime."
      />

      {error && (
        <Alert
          severity="error"
          sx={{ mb: 2 }}
          onClose={() => setError("")}
        >
          {error}
        </Alert>
      )}

      {loading ? (
        <Box
          sx={{
            display: "grid",
            placeItems: "center",
            py: 8,
          }}
        >
          <CircularProgress />
        </Box>
      ) : (
        <Box
          sx={{
            display: "grid",
            gap: 2,
          }}
        >
          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 900,
                  mb: 2,
                }}
              >
                Target
              </Typography>

              <Box
                sx={{
                  display: "grid",
                  gridTemplateColumns: {
                    xs: "1fr",
                    md: "1fr 1fr",
                  },
                  gap: 1.5,
                }}
              >
                <TextField
                  select
                  label="Endpoint"
                  value={apiId}
                  onChange={(event) => {
                    setApiId(event.target.value);
                    setResult(null);
                  }}
                >
                  {apis.map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.name} · {item.http_method}
                    </MenuItem>
                  ))}
                </TextField>

                <TextField
                  select
                  label="Backend version record"
                  value={versionId}
                  onChange={(event) =>
                    setVersionId(event.target.value)
                  }
                >
                  {versions.map((item) => (
                    <MenuItem key={item.id} value={item.id}>
                      {item.version}
                      {item.is_active ? " · ACTIVE" : ""}
                    </MenuItem>
                  ))}
                </TextField>

                <TextField
                  label="Request URL path"
                  value={path}
                  onChange={(event) =>
                    setPath(event.target.value)
                  }
                  sx={{
                    gridColumn: {
                      xs: "auto",
                      md: "1 / -1",
                    },
                  }}
                  helperText={
                    api
                      ? `${api.http_method} · ${
                          api.is_private ? "private" : "public"
                        } · runtime route is /mock/{full_path}`
                      : "Select an endpoint"
                  }
                />
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 900,
                  mb: 2,
                }}
              >
                Query parameters
              </Typography>

              <TextField
                fullWidth
                value={query}
                onChange={(event) =>
                  setQuery(event.target.value)
                }
                placeholder="userId=42&limit=10"
                helperText="Use standard query-string syntax."
              />
            </CardContent>
          </Card>

          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 900,
                  mb: 2,
                }}
              >
                Headers JSON
              </Typography>

              <TextField
                fullWidth
                multiline
                minRows={5}
                value={headers}
                onChange={(event) =>
                  setHeaders(event.target.value)
                }
                sx={{
                  "& textarea": {
                    fontFamily: "monospace",
                    fontSize: 12,
                  },
                }}
              />
            </CardContent>
          </Card>

          <Card>
            <CardContent sx={{ p: 3 }}>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2,
                  gap: 2,
                  flexWrap: "wrap",
                }}
              >
                <Typography
                  variant="h6"
                  sx={{ fontWeight: 900 }}
                >
                  Request body
                </Typography>

                <TextField
                  select
                  size="small"
                  label="Scenario"
                  value={scenario}
                  onChange={(event) =>
                    setScenario(event.target.value)
                  }
                  sx={{ minWidth: 190 }}
                >
                  {[
                    "success",
                    "validation_error",
                    "unauthorized",
                    "not_found",
                    "server_error",
                    "custom",
                  ].map((item) => (
                    <MenuItem key={item} value={item}>
                      {item.replaceAll("_", " ")}
                    </MenuItem>
                  ))}
                </TextField>
              </Box>

              <TextField
                fullWidth
                multiline
                minRows={10}
                value={body}
                onChange={(event) =>
                  setBody(event.target.value)
                }
                sx={{
                  "& textarea": {
                    fontFamily: "monospace",
                    fontSize: 12,
                  },
                }}
              />

              <Box
                sx={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: 1.5,
                  mt: 2,
                  flexWrap: "wrap",
                }}
              >
                <Button
                  variant="outlined"
                  startIcon={<BulkIcon />}
                  onClick={() => void sendTenRequests()}
                  disabled={
                    !api ||
                    !path.trim() ||
                    sending ||
                    bulkSending
                  }
                  sx={{
                    borderColor: "rgba(184,255,61,.45)",
                  }}
                >
                  {bulkSending
                    ? "Sending 10 requests..."
                    : "Send 10 Requests"}
                </Button>

                <Button
                  variant="contained"
                  startIcon={
                    sending ? (
                      <CircularProgress size={18} />
                    ) : (
                      <SendIcon />
                    )
                  }
                  onClick={() => void execute()}
                  disabled={
                    !api ||
                    !path.trim() ||
                    sending ||
                    bulkSending
                  }
                >
                  {sending ? "Sending..." : "Send Request"}
                </Button>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent sx={{ p: 3 }}>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 900,
                  mb: 2,
                }}
              >
                Response
              </Typography>

              {!result ? (
                <Typography
                  sx={{
                    py: 4,
                    color: "text.secondary",
                  }}
                >
                  No response yet.
                </Typography>
              ) : (
                <Box
                  sx={{
                    display: "grid",
                    gap: 2,
                  }}
                >
                  <Box
                    sx={{
                      display: "flex",
                      gap: 1,
                      flexWrap: "wrap",
                    }}
                  >
                    <Chip
                      label={`HTTP ${result.status}`}
                      color={
                        result.status >= 400
                          ? "error"
                          : "success"
                      }
                      variant="outlined"
                    />

                    <Chip
                      label={`${result.responseTime.toFixed(
                        2,
                      )} ms`}
                      variant="outlined"
                    />
                  </Box>

                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      maxHeight: 400,
                      overflow: "auto",
                    }}
                  >
                    <Typography
                      sx={{
                        fontSize: 10,
                        fontWeight: 900,
                        color: "text.secondary",
                        mb: 1,
                      }}
                    >
                      BODY
                    </Typography>

                    <Box
                      component="pre"
                      sx={{
                        m: 0,
                        fontFamily: "monospace",
                        fontSize: 12,
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {prettyBody(result.body)}
                    </Box>
                  </Paper>

                  <Paper
                    variant="outlined"
                    sx={{
                      p: 2,
                      maxHeight: 250,
                      overflow: "auto",
                    }}
                  >
                    <Typography
                      sx={{
                        fontSize: 10,
                        fontWeight: 900,
                        color: "text.secondary",
                        mb: 1,
                      }}
                    >
                      HEADERS
                    </Typography>

                    <Box
                      component="pre"
                      sx={{
                        m: 0,
                        fontFamily: "monospace",
                        fontSize: 12,
                        whiteSpace: "pre-wrap",
                      }}
                    >
                      {JSON.stringify(
                        result.headers,
                        null,
                        2,
                      )}
                    </Box>
                  </Paper>

                  {version && (
                    <Typography
                      sx={{
                        fontSize: 10,
                        color: "text.secondary",
                        fontFamily: "monospace",
                      }}
                    >
                      Selected backend version record:{" "}
                      {version.version}. The current backend
                      runtime matches active definitions by
                      method/path.
                    </Typography>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
}