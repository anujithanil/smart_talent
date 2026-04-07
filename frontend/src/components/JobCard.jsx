import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ApplyForm from "./ApplyForm";

export default function JobCard({ job }) {
  const [showForm, setShowForm] = useState(false);
  const [expanded, setExpanded] = useState(false);

  const shortText =
    job.description.length > 150
      ? job.description.slice(0, 150) + "..."
      : job.description;

  return (
    <motion.div
      layout
      whileHover={{
        scale: 1.03,
        y: -8,
      }}
      transition={{ type: "spring", stiffness: 200 }}
      className={`${
        expanded ? "h-auto" : "h-[280px]"
      } flex flex-col justify-between bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-3xl p-6 shadow-md shadow-blue-200/50 transition-all text-blue-900`}
      style={{ transformStyle: "preserve-3d" }}
    >
      {/* TITLE */}
      <h2 className="text-xl font-semibold mb-2 text-blue-900">
        {job.name || "Untitled Job"}
      </h2>

      {/* DESCRIPTION */}
      <motion.p
        layout
        className="text-sm text-blue-800 whitespace-pre-line leading-6 overflow-hidden"
      >
        {expanded ? job.description : shortText}
      </motion.p>

      {/* SEE MORE */}
      {job.description.length > 150 && (
        <button
          onClick={() => setExpanded((prev) => !prev)}
          className="mt-3 text-blue-600 text-sm font-medium hover:text-blue-900 transition"
        >
          {expanded ? "See Less" : "See More"}
        </button>
      )}

      {/* APPLY BUTTON */}
      <div className="mt-5">
        <button
          onClick={() => setShowForm((prev) => !prev)}
          className="inline-flex w-full items-center justify-center rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          {showForm ? "Hide Application" : "Apply Now"}
        </button>
      </div>

      {/* APPLY FORM (ANIMATED) */}
      <AnimatePresence>
        {showForm && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.25 }}
            className="mt-4 rounded-3xl border border-blue-200 bg-blue-50 p-4"
          >
            <ApplyForm jobId={job.id} />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}