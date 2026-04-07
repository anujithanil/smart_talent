import { useEffect, useState } from "react";
import API from "../api";
import LoadingSpinner from "./LoadingSpinner";

export default function IntelligencePanel({ jobId }) {
  const [data, setData] = useState(null);
  const [candidates, setCandidates] = useState([]);

  useEffect(() => {
    if (jobId) {
      API.get(`/intelligence/${jobId}`).then((res) => setData(res.data));
      API.get(`/rank/${jobId}`)
        .then((res) => setCandidates(res.data))
        .catch(() => setCandidates([]));
    }
  }, [jobId]);

  if (!data) return <LoadingSpinner label="Loading recruiter intelligence..." />;

  const averageScore = candidates.length
    ? Math.round(candidates.reduce((sum, c) => sum + (c.score || 0), 0) / candidates.length)
    : 0;

  const totalCandidates = candidates.length;
  const topSkills = Object.entries(data.skill_distribution || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([name, value]) => ({ name, value }));

  return (
    <div className="rounded-3xl border border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-5 shadow-md shadow-blue-200/50 mt-4 text-blue-900">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="font-semibold text-lg text-blue-900">Recruiter Intelligence</h2>
          <p className="text-sm text-blue-600">Actionable insights for your talent stack.</p>
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 mt-5">
        <div className="rounded-3xl border border-blue-200 bg-white p-4">
          <p className="text-sm text-blue-700 font-medium">Candidates evaluated</p>
          <p className="mt-2 text-2xl font-semibold text-blue-900">{totalCandidates}</p>
        </div>

        <div className="rounded-3xl border border-blue-200 bg-white p-4">
          <p className="text-sm text-blue-700 font-medium">Average match</p>
          <p className="mt-2 text-2xl font-semibold text-blue-900">{averageScore}%</p>
        </div>
      </div>


      <div className="mt-4 space-y-4">
        <div className="rounded-3xl border border-blue-200 bg-white p-4">
          <p className="text-sm text-blue-700 uppercase tracking-[0.15em] mb-3 font-semibold">Missing skill risk</p>
          {data.missing_skills.length > 0 ? (
            <ul className="space-y-3 text-sm text-blue-800">
              {data.missing_skills.slice(0, 3).map((item, index) => (
                <li key={index} className="flex items-center justify-between gap-3">
                  <span>{item.skill}</span>
                  <span className="rounded-full bg-red-100 px-2 py-1 text-red-700 text-xs font-semibold">
                    {Math.round(item.severity * 100)}%
                  </span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-blue-600">No high-priority skill gaps detected.</p>
          )}
        </div>

        <div className="rounded-3xl border border-blue-200 bg-white p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-blue-700 font-semibold uppercase tracking-[0.15em]">Top skill coverage</p>
            <span className="text-xs text-blue-600">{topSkills.length} skills</span>
          </div>
          <div className="space-y-3 text-sm text-blue-900">
            {topSkills.length > 0 ? (
              topSkills.map((skill, i) => (
                <div key={i} className="flex items-center justify-between gap-3">
                  <span>{skill.name}</span>
                  <span className="text-blue-700 font-semibold">{skill.value} candidates</span>
                </div>
              ))
            ) : (
              <p className="text-blue-600">No skills data available yet.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}