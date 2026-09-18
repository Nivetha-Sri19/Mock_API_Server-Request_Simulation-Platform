import { useState } from "react";
import {
  Box,
  Button,
  Drawer,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Typography,
  useMediaQuery,
} from "@mui/material";
import { Outlet, useLocation, useNavigate } from "react-router-dom";
import Logo from "./Logo";

type IconName =
  | "dashboard"
  | "apis"
  | "play"
  | "logs"
  | "settings"
  | "logout";

function Icon({ name }: { name: IconName }) {
  const paths: Record<IconName, React.ReactNode> = {
    dashboard: (
      <>
        <rect x="4" y="4" width="6" height="6" rx="1" />
        <rect x="14" y="4" width="6" height="6" rx="1" />
        <rect x="4" y="14" width="6" height="6" rx="1" />
        <rect x="14" y="14" width="6" height="6" rx="1" />
      </>
    ),

    apis: (
      <>
        <path d="M5 6h14M5 12h14M5 18h14" />
        <circle cx="9" cy="6" r="2" />
        <circle cx="15" cy="12" r="2" />
        <circle cx="11" cy="18" r="2" />
      </>
    ),

    play: <path d="m9 5 10 7-10 7V5Z" />,

    logs: (
      <>
        <path d="M5 5h14v14H5z" />
        <path d="M8 9h8M8 12h8M8 15h5" />
      </>
    ),

    settings: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19 12a7 7 0 0 0-.1-1.2l2-1.5-2-3.4-2.3 1a7 7 0 0 0-2-1.2L14.3 3h-4.6l-.3 2.7a7 7 0 0 0-2 1.2l-2.3-1-2 3.4 2 1.5A7 7 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.3-1a7 7 0 0 0 2 1.2l.3 2.7h4.6l.3-2.7a7 7 0 0 0 2-1.2l2.3 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2Z" />
      </>
    ),

    logout: (
      <>
        <path d="M10 5H5v14h5" />
        <path d="M13 8l4 4-4 4M17 12H9" />
      </>
    ),
  };

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
        flexShrink: 0,
      }}
    >
      {paths[name]}
    </Box>
  );
}

const nav = [
  {
    label: "Dashboard",
    to: "/dashboard",
    icon: "dashboard" as IconName,
  },
  {
    label: "Mock APIs",
    to: "/apis",
    icon: "apis" as IconName,
  },
  {
    label: "Request Lab",
    to: "/playground",
    icon: "play" as IconName,
  },
  {
    label: "Request Logs",
    to: "/logs",
    icon: "logs" as IconName,
  },
  {
    label: "Workspace",
    to: "/settings",
    icon: "settings" as IconName,
  },
];

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();

  const mobile = useMediaQuery("(max-width:900px)");

  const [open, setOpen] = useState(false);

  const user = JSON.parse(
    localStorage.getItem("mockpilot_user") ||
      localStorage.getItem("mockforge_user") ||
      "{}"
  );

  const logout = () => {
    localStorage.removeItem("mockpilot_token");
    localStorage.removeItem("mockforge_token");
    localStorage.removeItem("mockpilot_user");
    localStorage.removeItem("mockforge_user");

    navigate("/login", { replace: true });
  };

  const sidebar = (
    <Box
      sx={{
        width: 260,
        height: "100%",
        p: 2,
        display: "flex",
        flexDirection: "column",
        bgcolor: "#0a0d12",
        boxSizing: "border-box",
      }}
    >
      <Box
        sx={{
          p: 1,
          mb: 2,
        }}
      >
        <Logo />
      </Box>

      <List
        sx={{
          display: "grid",
          gap: 0.5,
          p: 0,
        }}
      >
        {nav.map((item) => {
          const selected =
            location.pathname === item.to ||
            location.pathname.startsWith(`${item.to}/`);

          return (
            <ListItemButton
              key={item.to}
              selected={selected}
              onClick={() => {
                navigate(item.to);
                setOpen(false);
              }}
              sx={{
                borderRadius: 2,
                minHeight: 46,
                px: 1.5,

                "&.Mui-selected": {
                  bgcolor: "rgba(184,255,61,.1)",
                  color: "primary.main",
                },

                "&.Mui-selected:hover": {
                  bgcolor: "rgba(184,255,61,.15)",
                },
              }}
            >
              <Icon name={item.icon} />

              <ListItemText
                primary={item.label}
                sx={{
                  ml: 1.2,
                }}
              />
            </ListItemButton>
          );
        })}
      </List>

      <Box
        sx={{
          mt: "auto",
          p: 1.5,
          border: "1px solid rgba(255,255,255,.07)",
          borderRadius: 2,
        }}
      >
        <Typography
          sx={{
            fontSize: 11,
            fontWeight: 800,
            overflow: "hidden",
            textOverflow: "ellipsis",
            whiteSpace: "nowrap",
          }}
        >
          {user.full_name || user.email || "User"}
        </Typography>

        <Typography
          sx={{
            fontSize: 10,
            color: "text.secondary",
            mt: 0.4,
          }}
        >
          {user.role || "user"}
        </Typography>

        <Button
          fullWidth
          size="small"
          startIcon={<Icon name="logout" />}
          onClick={logout}
          sx={{
            mt: 1,
            justifyContent: "flex-start",
          }}
        >
          Sign out
        </Button>
      </Box>
    </Box>
  );

  return (
    <Box
      sx={{
        minHeight: "100vh",
        width: "100%",
        display: "flex",
        bgcolor: "background.default",
        overflowX: "hidden",
      }}
    >
      {mobile ? (
        <>
          <IconButton
            onClick={() => setOpen(true)}
            sx={{
              position: "fixed",
              zIndex: 1200,
              top: 14,
              left: 14,
              bgcolor: "#0d1118",
              border: "1px solid rgba(255,255,255,.08)",
            }}
          >
            <Box
              component="svg"
              viewBox="0 0 24 24"
              sx={{
                width: 22,
                height: 22,
                fill: "none",
                stroke: "currentColor",
                strokeWidth: 2,
              }}
            >
              <path d="M4 7h16M4 12h16M4 17h16" />
            </Box>
          </IconButton>

          <Drawer
            open={open}
            onClose={() => setOpen(false)}
            PaperProps={{
              sx: {
                width: 260,
                bgcolor: "#0a0d12",
              },
            }}
          >
            {sidebar}
          </Drawer>
        </>
      ) : (
        <Box
          sx={{
            position: "fixed",
            left: 0,
            top: 0,
            bottom: 0,
            width: 260,
            zIndex: 1000,
            borderRight: "1px solid rgba(255,255,255,.07)",
            bgcolor: "#0a0d12",
          }}
        >
          {sidebar}
        </Box>
      )}

      <Box
        component="main"
        sx={{
          flex: 1,
          minWidth: 0,
          width: mobile ? "100%" : "calc(100% - 260px)",
          ml: mobile ? 0 : "260px",
          boxSizing: "border-box",
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}