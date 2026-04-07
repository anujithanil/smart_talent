import { useState, useEffect } from "react";
import axios from "axios";
import CandidateCard from "../components/CandidateCard";
import InsightsPanel from "../components/InsightsPanel";
import IntelligencePanel from "../components/IntelligencePanel";
import LoadingSpinner from "../components/LoadingSpinner";

export default function Dashboard() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [jobsLoading, setJobsLoading] = useState(true);
  const [candidatesLoading, setCandidatesLoading] = useState(false);

  useEffect(() => {
    axios.get("http://localhost:5000/jobs")
      .then((res) => setJobs(res.data))
      .finally(() => setJobsLoading(false));
  }, []);

  const loadCandidates = async (jobId) => {
    setCandidatesLoading(true);
    const res = await axios.get(`http://localhost:5000/rank/${jobId}`);
    const data = res.data?.candidates ?? res.data;
    setCandidates(data);
    setCandidatesLoading(false);
  };

  return (
    <div className="min-h-screen bg-blue-50 px-6 py-8">
      <div className="max-w-7xl mx-auto">
      <select
        onChange={(e) => {
          setSelectedJob(e.target.value);
          loadCandidates(e.target.value);
        }}
        className="w-full mb-6 rounded-2xl border border-blue-300 bg-white px-4 py-3 text-blue-900 focus:ring-2 focus:ring-blue-400/20 outline-none"
      >
        <option>Select Job</option>
        {jobs.map((j) => (
          <option key={j.id} value={j.id}>
            {j.name}
          </option>
        ))}
      </select>

      <div className="flex gap-6">
        {/* LEFT: Candidates */}
        <div className="w-2/3">
          <h2 className="font-bold mb-4 text-blue-900 text-2xl">Candidates</h2>

            {candidatesLoading ? (
              <LoadingSpinner label="Loading candidates..." />
            ) : (
              <div className="grid gap-4">
                {candidates.map((c, i) => (
                  <CandidateCard key={i} candidate={c} />
                ))}
              </div>
            )}
        </div>
        <div className="w-1/3">
          {selectedJob && (
            <>
              <InsightsPanel jobId={selectedJob} />
              <IntelligencePanel jobId={selectedJob} />
            </>
          )}
        </div>
      </div>
    </div>
    </div>
  );
}