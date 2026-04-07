import { useState, useRef } from "react";
import API from "../api";

export default function ApplyForm({ jobId }) {
  const [name, setName] = useState("");
  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async () => {
    if (!name.trim()) {
      alert("Please enter your name.");
      return;
    }

    if (!file) {
      alert("Please attach your resume.");
      return;
    }

    const formData = new FormData();
    formData.append("name", name);
    formData.append("job_id", jobId);
    formData.append("resume", file);

    try {
      setIsSubmitting(true);
      await API.post("/apply", formData);
      alert("Applied!");
      setName("");
      setFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = null;
      }
    } catch (error) {
      console.error(error);
      alert("Application failed. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="flex flex-col gap-4">
      <input
        placeholder="Your Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="w-full rounded-2xl border border-blue-300 bg-blue-50 px-4 py-3 text-blue-900 placeholder:text-blue-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 outline-none"
      />

      <div className="rounded-3xl border border-blue-300 bg-blue-50 p-4 text-sm text-blue-800 shadow-inner">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-semibold text-blue-900">Resume Upload</p>
            <p className="text-xs text-blue-600">PDF, DOC, or DOCX files accepted.</p>
          </div>

          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            className="rounded-full bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            {file ? "Change file" : "Choose file"}
          </button>
        </div>

        <input
          type="file"
          ref={fileInputRef}
          className="hidden"
          onChange={handleFileChange}
        />

        <div className="mt-4 flex items-center justify-between text-sm text-blue-600">
          <span>{file ? file.name : "No file selected yet."}</span>
          {file && (
            <button
              type="button"
              onClick={() => {
                setFile(null);
                if (fileInputRef.current) fileInputRef.current.value = null;
              }}
              className="text-blue-600 hover:text-blue-900"
            >
              Remove
            </button>
          )}
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={isSubmitting}
        className="rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-blue-400"
      >
        {isSubmitting ? "Submitting..." : "Apply"}
      </button>
    </div>
  );
}