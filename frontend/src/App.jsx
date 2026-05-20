// frontend/src/App.jsx
import { useState, useEffect } from "react";
import LandingPage   from "./pages/LandingPage";
import Home          from "./pages/Home";
import SharePage     from "./pages/SharePage";
import ErrorBoundary from "./components/ErrorBoundary";

function getRoute() {
  const path = window.location.pathname;
  if (path.startsWith("/share/")) return { name: "share", token: path.replace("/share/", "") };
  if (path === "/app")            return { name: "app" };
  return { name: "landing" };
}

export default function App() {
  const [route, setRoute] = useState(getRoute);

  useEffect(() => {
    const handler = () => setRoute(getRoute());
    window.addEventListener("popstate", handler);
    return () => window.removeEventListener("popstate", handler);
  }, []);

  const navigate = (path) => {
    window.history.pushState({}, "", path);
    setRoute(getRoute());
  };

  return (
    <ErrorBoundary>
      {route.name === "share"   && <SharePage token={route.token} />}
      {route.name === "app"     && <Home />}
      {route.name === "landing" && <LandingPage onGetStarted={() => navigate("/app")} />}
    </ErrorBoundary>
  );
}