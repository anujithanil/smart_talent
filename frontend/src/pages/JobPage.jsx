import { useEffect, useState } from "react";
import API from "../api";
import JobCard from "../components/JobCard";
import LoadingSpinner from "../components/LoadingSpinner";
import { motion } from "framer-motion";

export default function JobPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    API.get("/jobs")
      .then((res) => setJobs(res.data))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen bg-blue-50 px-4 py-8">
      <div className="mx-auto max-w-6xl rounded-3xl border border-blue-300 bg-white p-6 shadow-md shadow-blue-200/50">

        <h2 className="text-3xl font-semibold text-blue-900 mb-6 text-center">
          Open Positions
        </h2>

        {loading ? (
          <LoadingSpinner label="Loading open positions..." />
        ) : (
          <div className="grid gap-6 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
            {jobs.map((job) => (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
              >
                <JobCard job={job} />
              </motion.div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}