import { useEffect, useState } from "react";
import API from "../api";
import LoadingSpinner from "./LoadingSpinner";
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

export default function InsightsPanel({ jobId }) {
  const [data, setData] = useState(null);

  useEffect(() => {
    if (jobId) {
      API.get(`/insights/${jobId}`).then((res) => setData(res.data));
    }
  }, [jobId]);

  if (!data) return <LoadingSpinner label="Loading insights..." />;

  const chartData = [
    { name: "Avg Score", value: data.average_score },
    { name: "Max Score", value: data.max_score },
    { name: "Min Score", value: data.min_score },
  ];

  return (
    <div className="rounded-3xl border border-blue-200 bg-gradient-to-br from-blue-50 to-blue-100 p-6 shadow-md shadow-blue-200/50 mt-4 text-blue-900">
      <h2 className="font-bold text-lg mb-4 text-blue-900">Hiring Insights</h2>

     

      

      {data.missing_skills?.length > 0 && (
        <div className="mt-4 rounded-3xl border border-blue-200 bg-white p-4">
          <p className="font-semibold text-blue-900 mb-2">Potential Gaps</p>
          <p className="text-sm text-blue-700">{data.missing_skills.map((m) => m.skill).join(", ")}</p>
        </div>
      )}

      <p className="mt-4 italic text-blue-700">{data.summary}</p>
      <div className="mt-4 overflow-hidden rounded-3xl border border-blue-200 bg-white p-4">
        <BarChart width={250} height={200} data={chartData}>
          <XAxis dataKey="name" stroke="#3b82f6" />
          <YAxis stroke="#3b82f6" />
          <Tooltip contentStyle={{ backgroundColor: '#eff6ff', borderColor: '#93c5fd' }} />
          <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
        </BarChart>
      </div>
    </div>
  );
}