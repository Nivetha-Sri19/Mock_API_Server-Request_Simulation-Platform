import { createTheme } from "@mui/material/styles";
export const theme = createTheme({
  palette: { mode: "dark", background: { default: "#06080b", paper: "#0d1118" }, primary: { main: "#b8ff3d", contrastText: "#071000" }, secondary: { main: "#00d4ff" }, error: { main: "#ff4d6d" }, warning: { main: "#ffb020" }, success: { main: "#35e28b" }, text: { primary: "#f4f7fb", secondary: "#8d98a8" }, divider: "rgba(255,255,255,.08)" },
  typography: { fontFamily: 'Inter, "Segoe UI", sans-serif', h1: { fontWeight: 900, letterSpacing: "-.045em" }, h2: { fontWeight: 900, letterSpacing: "-.04em" }, h3: { fontWeight: 850, letterSpacing: "-.035em" }, button: { textTransform: "none", fontWeight: 800 } },
  shape: { borderRadius: 14 },
  components: { MuiButton: { defaultProps: { disableElevation: true } }, MuiCard: { styleOverrides: { root: { backgroundImage: "none", border: "1px solid rgba(255,255,255,.07)" } } }, MuiTextField: { defaultProps: { size: "small" } }, MuiTableCell: { styleOverrides: { root: { borderColor: "rgba(255,255,255,.06)" } } } },
});
