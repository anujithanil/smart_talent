import { useState } from "react";

const fitLabel = (score) => {
  if (score >= 85) return "Top fit";
  if (score >= 70) return "Strong fit";
  if (score >= 55) return "Good fit";
  return "Needs attention";
};

const summaryColor = (score) => {
  if (score >= 85) return "bg-emerald-50 text-emerald-700 border-emerald-300";
  if (score >= 70) return "bg-blue-50 text-blue-700 border-blue-300";
  if (score >= 55) return "bg-amber-50 text-amber-700 border-amber-300";
  return "bg-rose-50 text-rose-700 border-rose-300";
};

const scaleExperience = (years) => Math.min(Math.round((years || 0) * 12), 100);

const getInsightTexts = (candidate) => {
  const { semantic = 0, skills = 0, experience = 0 } = candidate.breakdown || {};
  const dimensions = [
    { key: "skills", label: "Skill fit", value: skills, scaled: skills },
    { key: "semantic", label: "Semantic fit", value: semantic, scaled: semantic },
    { key: "experience", label: "Experience", value: experience, scaled: scaleExperience(experience) },
  ];

  const sorted = [...dimensions].sort((a, b) => b.scaled - a.scaled);
  const strongest = sorted[0];
  const weakest = sorted[sorted.length - 1];

  const strength =
    strongest.key === "skills"
      ? `Strongest asset is skill alignment at ${skills}%, showing the candidate can handle the technology stack.`
      : strongest.key === "semantic"
      ? `Best fit is conceptual alignment (${semantic}%), meaning the candidate's profile matches the role narrative well.`
      : `Best asset is experience (${experience} yrs), offering practical exposure and domain context.`;

  const opportunity =
    weakest.key === "skills"
      ? `Opportunity: skill fit is the biggest gap at ${skills}%; validate depth in core tools and frameworks.`
      : weakest.key === "semantic"
      ? `Opportunity: semantic match is the lowest area at ${semantic}%; review the candidate's role-context and phrasing.`
      : `Opportunity: experience is the smallest dimension at ${experience} yrs; assess level, seniority, or growth potential.`;

  return { strength, opportunity };
};

export default function CandidateCard({ candidate }) {
  const [expanded, setExpanded] = useState(false);

  const stats = [
    { label: "Semantic", value: `${candidate.breakdown.semantic}%` },
    { label: "Skill Fit", value: `${candidate.breakdown.skills}%` },
    { label: "Experience", value: `${candidate.breakdown.experience} yrs` },
    { label: "Fit Band", value: fitLabel(candidate.score) },
  ];

  return (
    <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 rounded-3xl p-6 shadow-md shadow-blue-200/50 transition hover:shadow-lg">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-blue-900">{candidate.name}</h2>
            <p className="text-sm text-blue-600 mt-1">Smart match summary for this candidate.</p>
          </div>

          <div className="flex flex-col items-start gap-2 sm:items-end">
            <span className="rounded-full bg-blue-600 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-white">
              {candidate.score}% Match
            </span>
            {candidate.hidden_gem && (
              <span className="rounded-full bg-amber-500/10 border border-amber-400 text-amber-700 px-3 py-1 text-xs font-medium">
                Hidden Gem
              </span>
            )}
          </div>
        </div>

          <div className="grid grid-cols-2 gap-3">
            {stats.map((item) => (
              <div key={item.label} className="rounded-2xl border border-blue-200 bg-white p-4">
                <p className="text-xs uppercase tracking-[0.2em] text-blue-600">{item.label}</p>
                <p className="mt-2 text-lg font-semibold text-blue-900">{item.value}</p>
              </div>
            ))}
          </div>

          <div className="rounded-3xl border border-blue-200 bg-white p-4">
            <p className="text-sm leading-6 text-blue-800">
              {candidate.justification || "This candidate has been scored against the job requirements and shows a strong skill and experience alignment."}
            </p>
          </div>

          <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => window.open(`http://localhost:5000/resume/${candidate.resume}`)}
                className="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
              >
                View Resume
              </button>
              <button
                onClick={() => setExpanded((prev) => !prev)}
                className="rounded-2xl border border-blue-300 bg-white px-4 py-2 text-sm text-blue-700 transition hover:bg-blue-50"
              >
                {expanded ? "Hide Details" : "Analyze Deep"}
              </button>
            </div>

            <div className={`rounded-full px-3 py-1 text-xs font-semibold ${summaryColor(candidate.score)}`}>
              {fitLabel(candidate.score)} candidate
            </div>
          </div>

          {expanded && (
            <div className="mt-3 rounded-3xl border border-blue-200 bg-white p-5">
              <h3 className="text-sm font-semibold text-blue-900 mb-3">Candidate insight summary</h3>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-2xl bg-blue-50 p-4 border border-blue-200">
                  <p className="text-xs uppercase tracking-[0.18em] text-blue-600 font-semibold">Strength</p>
                  <p className="mt-2 text-sm text-blue-800">
                    {getInsightTexts(candidate).strength}
                  </p>
                </div>
                <div className="rounded-2xl bg-blue-50 p-4 border border-blue-200">
                  <p className="text-xs uppercase tracking-[0.18em] text-blue-600 font-semibold">Opportunity</p>
                  <p className="mt-2 text-sm text-blue-800">
                    {getInsightTexts(candidate).opportunity}
                  </p>
                </div>
              </div>
              <div className="mt-4 rounded-2xl border border-blue-200 bg-blue-50 p-4 text-sm text-blue-800">
                <div className="mb-3 text-blue-700 uppercase tracking-[0.15em] text-xs font-semibold">Quick candidate notes</div>
                <ul className="list-disc space-y-2 pl-5">
                  <li>
                    {candidate.hidden_gem
                      ? "Hidden gem with potential to outperform the initial score."
                      : "Data-driven match profile based on current resume analysis."}
                  </li>
                  <li>
                    {candidate.breakdown.skills >= 75
                      ? "Strong technical match, especially in key job skills."
                      : candidate.breakdown.skills >= 55
                      ? "Moderate skill fit; review the most relevant skill areas."
                      : "Skill coverage is the largest improvement area for this candidate."}
                  </li>
                  <li>
                    {candidate.breakdown.semantic >= 75
                      ? "Good conceptual fit to the job description."
                      : "Consider whether role phrasing matches candidate experience clearly."}
                  </li>
                  <li>
                    {candidate.breakdown.experience >= 5
                      ? "Experienced profile with strong time-in-role credibility."
                      : candidate.breakdown.experience >= 3
                      ? "Solid mid-level experience for the role."
                      : "Lower experience; treat this candidate as growth potential."}
                  </li>
                </ul>
              </div>
              {candidate.interview_guide && candidate.interview_guide.questions && (
                <div className="mt-5 rounded-2xl border border-blue-200 bg-white p-5 text-sm text-blue-800">
                  <h3 className="text-sm font-semibold text-blue-900 mb-3">Interview guide</h3>
                  <p className="text-sm text-blue-700 mb-3">{candidate.interview_guide.summary}</p>
                  {candidate.interview_guide.strengths?.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs uppercase tracking-[0.15em] text-blue-600 font-semibold mb-2">Strengths</p>
                      <ul className="list-disc pl-5 text-blue-800 space-y-1">
                        {candidate.interview_guide.strengths.map((item, index) => (
                          <li key={`strength-${index}`}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {candidate.interview_guide.concerns?.length > 0 && (
                    <div className="mb-3">
                      <p className="text-xs uppercase tracking-[0.15em] text-blue-600 font-semibold mb-2">Concerns to probe</p>
                      <ul className="list-disc pl-5 text-blue-800 space-y-1">
                        {candidate.interview_guide.concerns.map((item, index) => (
                          <li key={`concern-${index}`}>{item}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  <div>
                    <p className="text-xs uppercase tracking-[0.15em] text-blue-600 font-semibold mb-2">Sample questions</p>
                    <ul className="list-decimal pl-5 text-blue-800 space-y-2">
                      {candidate.interview_guide.questions.map((question, index) => (
                        <li key={`question-${index}`}>{question}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

    </div>
  );
}