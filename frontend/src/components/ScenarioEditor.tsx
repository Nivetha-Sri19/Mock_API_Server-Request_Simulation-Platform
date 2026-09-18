import { useEffect, useState } from "react";
import {
  Alert, Box, Button, Card, CardContent, Chip, Dialog,
  DialogActions, DialogContent, DialogTitle, IconButton,
  MenuItem, TextField, Typography,
} from "@mui/material";
import { scenarioApi } from "../api";
import type { ResponseScenario, ResponseTemplate } from "../types";
import { getErrorMessage, prettyBody } from "../utils";

const scenarios: ResponseScenario[] = ["success", "validation_error", "unauthorized", "not_found", "server_error", "custom"];
const presets: Record<ResponseScenario, { status: number; body: unknown }> = {
  success: { status: 200, body: { success: true, message: "Mock response" } },
  validation_error: { status: 422, body: { success: false, message: "Validation failed" } },
  unauthorized: { status: 401, body: { success: false, message: "Authentication required" } },
  not_found: { status: 404, body: { success: false, message: "Resource not found" } },
  server_error: { status: 500, body: { success: false, message: "Internal server error" } },
  custom: { status: 202, body: { success: true, message: "Custom response" } },
};

type Form = { scenario: ResponseScenario; status_code: number; headersText: string; bodyText: string; delay_ms: number };

function ActionIcon({ type }: { type: "add" | "edit" | "delete" }) {
  const content = type === "add"
    ? <><path d="M12 5v14" /><path d="M5 12h14" /></>
    : type === "edit"
      ? <><path d="M4 20h4L19 9l-4-4L4 16v4Z" /><path d="m13.5 6.5 4 4" /></>
      : <><path d="M4 7h16" /><path d="M10 11v6" /><path d="M14 11v6" /><path d="M6 7l1 14h10l1-14" /><path d="M9 7V4h6v3" /></>;
  return <Box component="svg" viewBox="0 0 24 24" sx={{ width: 19, height: 19, fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round" }}>{content}</Box>;
}

export default function ScenarioEditor({ mockId, versionId }: { mockId: string; versionId: string }) {
  const [items, setItems] = useState<ResponseTemplate[]>([]);
  const [error, setError] = useState("");
  const [open, setOpen] = useState(false);
  const [editing, setEditing] = useState<ResponseTemplate | null>(null);
  const [form, setForm] = useState<Form>({ scenario: "success", status_code: 200, headersText: '{\n  "Content-Type": "application/json"\n}', bodyText: JSON.stringify(presets.success.body, null, 2), delay_ms: 0 });

  const load = async () => {
    try {
      const response = await scenarioApi.list(mockId, versionId, { page: 1, page_size: 100 });
      setItems(response.data.items);
    } catch (e) { setError(getErrorMessage(e)); }
  };
  useEffect(() => { void load(); }, [mockId, versionId]);

  const start = (item?: ResponseTemplate) => {
    if (item) {
      setEditing(item);
      setForm({ scenario: item.scenario, status_code: item.status_code, headersText: JSON.stringify(item.headers || {}, null, 2), bodyText: prettyBody(item.body), delay_ms: item.delay_ms });
    } else {
      setEditing(null);
      setForm({ scenario: "success", status_code: 200, headersText: '{\n  "Content-Type": "application/json"\n}', bodyText: JSON.stringify(presets.success.body, null, 2), delay_ms: 0 });
    }
    setOpen(true);
  };

  const save = async () => {
    try {
      setError("");
      const headers = JSON.parse(form.headersText) as Record<string, string>;
      let body: unknown;
      try { body = JSON.parse(form.bodyText); } catch { body = form.bodyText; }
      if (editing) {
        await scenarioApi.update(mockId, versionId, editing.id, { status_code: form.status_code, headers, body, delay_ms: form.delay_ms });
      } else {
        await scenarioApi.create(mockId, versionId, { scenario: form.scenario, status_code: form.status_code, headers, body, delay_ms: form.delay_ms });
      }
      setOpen(false);
      await load();
    } catch (e) {
      setError(e instanceof SyntaxError ? "Response headers must be valid JSON." : getErrorMessage(e));
    }
  };

  const remove = async (item: ResponseTemplate) => {
    if (!confirm(`Delete ${item.scenario} scenario?`)) return;
    try { await scenarioApi.remove(mockId, versionId, item.id); await load(); }
    catch (e) { setError(getErrorMessage(e)); }
  };

  return <Box>
    {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>{error}</Alert>}
    <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2, gap: 2, flexWrap: "wrap" }}>
      <Box><Typography variant="h6" sx={{ fontWeight: 900 }}>Response scenarios</Typography><Typography sx={{ fontSize: 12, color: "text.secondary" }}>Persisted response templates selected by the runtime with the <code>__scenario</code> query parameter.</Typography></Box>
      <Button variant="contained" startIcon={<ActionIcon type="add" />} onClick={() => start()}>Add scenario</Button>
    </Box>
    {items.length === 0 ? <Typography sx={{ py: 5, color: "text.secondary" }}>No scenarios configured. Create a success response before using Request Lab.</Typography> : <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "1fr 1fr" }, gap: 1.5 }}>
      {items.map(item => <Card key={item.id}><CardContent sx={{ p: 2 }}><Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}><Chip label={item.scenario.replaceAll("_", " ")} size="small" color={item.status_code >= 400 ? "error" : "success"} variant="outlined" /><Typography sx={{ fontFamily: "monospace", fontWeight: 900 }}>{item.status_code}</Typography></Box><Typography sx={{ fontSize: 10, color: "text.secondary", mt: 1 }}>DELAY · {item.delay_ms} ms</Typography><Box sx={{ mt: 1, p: 1.5, bgcolor: "rgba(0,0,0,.22)", borderRadius: 1.5, maxHeight: 150, overflow: "auto" }}><Typography component="pre" sx={{ m: 0, fontFamily: "monospace", fontSize: 11, whiteSpace: "pre-wrap" }}>{prettyBody(item.body)}</Typography></Box><Box sx={{ display: "flex", justifyContent: "flex-end" }}><IconButton onClick={() => start(item)}><ActionIcon type="edit" /></IconButton><IconButton color="error" onClick={() => void remove(item)}><ActionIcon type="delete" /></IconButton></Box></CardContent></Card>)}
    </Box>}
    <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="md">
      <DialogTitle sx={{ fontWeight: 900 }}>{editing ? "Edit response scenario" : "Create response scenario"}</DialogTitle>
      <DialogContent sx={{ display: "grid", gap: 1.5, pt: "12px !important" }}>
        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr 1fr" }, gap: 1.5 }}>
          <TextField select label="Scenario" value={form.scenario} disabled={!!editing} onChange={e => { const scenario = e.target.value as ResponseScenario; setForm({ ...form, scenario, status_code: presets[scenario].status, bodyText: JSON.stringify(presets[scenario].body, null, 2) }); }}>{scenarios.map(s => <MenuItem key={s} value={s}>{s.replaceAll("_", " ")}</MenuItem>)}</TextField>
          <TextField label="Status code" type="number" value={form.status_code} onChange={e => setForm({ ...form, status_code: Number(e.target.value) })} />
          <TextField label="Delay (ms)" type="number" value={form.delay_ms} onChange={e => setForm({ ...form, delay_ms: Number(e.target.value) })} />
        </Box>
        <TextField label="Response headers JSON" multiline minRows={4} value={form.headersText} onChange={e => setForm({ ...form, headersText: e.target.value })} sx={{ "& textarea": { fontFamily: "monospace", fontSize: 12 } }} />
        <TextField label="Response body" multiline minRows={9} value={form.bodyText} onChange={e => setForm({ ...form, bodyText: e.target.value })} sx={{ "& textarea": { fontFamily: "monospace", fontSize: 12 } }} />
      </DialogContent>
      <DialogActions sx={{ p: 2 }}><Button onClick={() => setOpen(false)}>Cancel</Button><Button variant="contained" onClick={() => void save()}>Save scenario</Button></DialogActions>
    </Dialog>
  </Box>;
}
