import { useEffect, useState } from "react";
import API from "../api";
import CandidateCard from "../components/CandidateCard";
import InsightsPanel from "../components/InsightsPanel";
import IntelligencePanel from "../components/IntelligencePanel";
import LoadingSpinner from "../components/LoadingSpinner";

export default function JobDetails({ job, setPage }) {
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (job) {
      setLoading(true);
      API.get(`/rank/${job.id}`)
        .then((res) => {
          const data = res.data?.candidates ?? res.data;
          setCandidates(data);
        })
        .finally(() => setLoading(false));
    }
  }, [job]);

  if (!job) return <p>Select a job</p>;

  return (
    <div className="min-h-screen bg-blue-50 px-6 py-8">
      <div className="max-w-7xl mx-auto">
        <button
          onClick={() => setPage("adminDashboard")}
          className="mb-4 inline-flex items-center rounded-2xl border border-blue-300 bg-white px-4 py-2 text-sm font-semibold text-blue-700 shadow-sm transition hover:bg-blue-50"
        >
          ← Back to Dashboard
        </button>
      <h1 className="text-3xl font-bold mb-6 text-blue-900">{job.name}</h1>

      <div className="flex gap-6">
        {/* LEFT: Candidates */}
        <div className="w-2/3">
          <h2 className="font-bold mb-4 text-blue-900 text-2xl">Applicants</h2>

            {loading ? (
              <LoadingSpinner label="Loading applicants..." />
            ) : (
              <div className="grid gap-4">
                {candidates.map((c, i) => (
                  <CandidateCard key={i} candidate={c} />
                ))}
              </div>
            )}
        </div>
        <div className="w-1/3">
          <InsightsPanel jobId={job.id} />
          <IntelligencePanel jobId={job.id} />
         
        </div>
      </div>
      </div>
    </div>
  )
  };
