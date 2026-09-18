import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Apis from "./pages/Apis";
import ApiDetail from "./pages/ApiDetail";
import VersionDetail from "./pages/VersionDetail";
import Playground from "./pages/Playground";
import Logs from "./pages/Logs";
import Settings from "./pages/Settings";
function Protected(){return localStorage.getItem("mockpilot_token")||localStorage.getItem("mockforge_token")?<Layout/>:<Navigate to="/login" replace/>}
export default function App(){return <Routes><Route path="/login" element={<Login/>}/><Route element={<Protected/>}><Route path="/dashboard" element={<Dashboard/>}/><Route path="/apis" element={<Apis/>}/><Route path="/apis/:id" element={<ApiDetail/>}/><Route path="/apis/:id/versions/:versionId" element={<VersionDetail/>}/><Route path="/playground" element={<Playground/>}/><Route path="/logs" element={<Logs/>}/><Route path="/settings" element={<Settings/>}/></Route><Route path="*" element={<Navigate to="/dashboard" replace/>}/></Routes>}
