import { useEffect, useState } from "react";
import API from "../api";
import JobForm from "../components/JobForm";
import LoadingSpinner from "../components/LoadingSpinner";

export default function AdminDashboard({ setPage, setSelectedJob, setToken }) {
  const [jobs, setJobs] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [expandedJobs, setExpandedJobs] = useState({});

  useEffect(() => {
    API.get("/jobs")
      .then((res) => setJobs(res.data))
      .catch(() => {
        localStorage.removeItem("token");
        setToken(null);
        setPage("adminLogin");
      })
      .finally(() => setLoading(false));
  }, [setToken, setPage]);

  if (loading) {
    return <LoadingSpinner label="Verifying admin access..." />;
  }

  const toggleExpand = (jobId) => {
    setExpandedJobs((prev) => ({
      ...prev,
      [jobId]: !prev[jobId],
    }));
  };

  return (
    <div className="min-h-screen bg-blue-50 px-4 py-8 text-blue-900">
      <div className="mx-auto max-w-7xl rounded-3xl border border-blue-300 bg-white p-6 shadow-md shadow-blue-200/50">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
          <div>
            <h1 className="text-3xl font-semibold text-blue-900">Admin Dashboard</h1>
            <p className="text-blue-600">Manage job postings and review candidate matches.</p>
          </div>

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => setShowForm((prev) => !prev)}
              className="rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
            >
              + Create Job
            </button>

            <button
              onClick={() => {
                localStorage.removeItem("token");
                setToken(null);
                setPage("landing");
              }}
              className="rounded-2xl bg-red-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>

        {showForm && <JobForm onJobCreated={(newJob) => setJobs([newJob, ...jobs])} />}

        <div className="grid gap-4 lg:grid-cols-3 mt-6">
          {jobs.map((job) => (
            <div key={job.id} className="rounded-3xl border border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-5 shadow-lg transition hover:shadow-xl hover:border-blue-400">
              <h2 className="text-xl font-semibold text-blue-900">{job.name}</h2>
              <p className={`mt-2 text-sm text-blue-700 leading-6 ${
                expandedJobs[job.id] ? "" : "line-clamp-3"
              }`}>
                {job.description}
              </p>
              
              {job.description.length > 150 && (
                <button
                  onClick={() => toggleExpand(job.id)}
                  className="mt-2 text-sm font-medium text-blue-600 hover:text-blue-900 transition"
                >
                  {expandedJobs[job.id] ? "See Less" : "See More"}
                </button>
              )}

              <button
                onClick={() => {
                  setSelectedJob(job);
                  setPage("jobDetails");
                }}
                className="mt-4 inline-flex rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              >
                View
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}