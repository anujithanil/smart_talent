import { useState } from "react";
import LandingPage from "./pages/LandingPage.jsx";
import JobPage from "./pages/JobPage.jsx";
import AdminLogin from "./pages/AdminLogin.jsx";

import JobDetails from "./pages/JobDetails.jsx";
import AdminDashboard from "./pages/AdminDashboard.jsx";
import Navbar from "./components/Navbar";

function App() {
  const [page, setPage] = useState("landing");
  const [token, setToken] = useState(localStorage.getItem("token"));
  const [selectedJob, setSelectedJob] = useState(null);

  return (
    <div className="min-h-screen bg-blue-50 text-blue-900">
      <Navbar setPage={setPage} token={token} setToken={setToken} />

    {page === "landing" && <LandingPage setPage={setPage} />}

    {page === "jobs" && <JobPage />}

    {page === "adminLogin" && (
      <AdminLogin setToken={setToken} setPage={setPage} />
    )}

    {/* 🔥 PROTECTED ROUTE */}
    {page === "adminDashboard" &&
      (token ? (
        <AdminDashboard
          setPage={setPage}
          setSelectedJob={setSelectedJob}
          setToken={setToken}
        />
      ) : (
        <AdminLogin setToken={setToken} setPage={setPage} />
      ))}

    {page === "jobDetails" && token && (
      <JobDetails job={selectedJob} setPage={setPage} />
    )}
  </div>
);
}

export default App;