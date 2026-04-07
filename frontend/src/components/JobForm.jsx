import { useState } from "react";
import API from "../api";

export default function JobForm({ onJobCreated }) {
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");

  const handleSubmit = async () => {
    if (!name.trim() || !desc.trim()) {
      alert("Please fill all fields");
      return;
    }

    try {
      const res = await API.post("/jobs", {
        name,
        description: desc,
      });

      alert("Job Created");

      // ✅ Reset form (NOW it will work)
      setName("");
      setDesc("");

      // ✅ Update UI instantly
      onJobCreated(res.data);

    } catch (err) {
      console.error(err);
      alert("Error creating job");
    }
  };

  return (
    <div className="rounded-3xl border border-slate-700 bg-slate-950/95 p-6 mb-6 shadow-xl shadow-black/20">

  <input
    value={name}
    placeholder="Job Title"
    className="border border-slate-700 bg-slate-900 text-slate-100 p-3 w-full mb-3 rounded-2xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
    onChange={(e) => setName(e.target.value)}
  />

  <textarea
    value={desc}
    placeholder="Job Description"
    className="border border-slate-700 bg-slate-900 text-slate-100 p-3 w-full mb-3 rounded-2xl focus:outline-none focus:ring-2 focus:ring-cyan-500"
    onChange={(e) => setDesc(e.target.value)}
  />

  <button
    onClick={handleSubmit}
    className="bg-blue-600 hover:bg-blue-700 text-white w-full py-2 rounded-2xl font-medium"
  >
    Post Job
  </button>
</div>
  );
}