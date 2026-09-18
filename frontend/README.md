# MockPilot — API Simulation Workspace

React + TypeScript + Vite frontend for the API Mock Server & Request Simulation Platform.

## Backend integration

The UI is wired to the FastAPI backend using `VITE_API_BASE_URL` and JWT Bearer authentication. Dashboard, API catalog, versions, request contracts, response scenarios, permissions and request logs are loaded from backend endpoints rather than hardcoded mock data.

## Run

```powershell
npm install
npm run dev
```

Backend default:

```text
http://127.0.0.1:8000
```

Frontend default:

```text
http://localhost:5173
```
