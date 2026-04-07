export default function LandingPage({ setPage }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200 text-blue-900 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-3xl rounded-[2rem] border border-blue-300 bg-white p-10 shadow-lg shadow-blue-200/40 text-center">
        <p className="text-sm uppercase tracking-[0.3em] text-blue-600 mb-6">AI Hiring Intelligence</p>
        <h1 className="text-5xl font-semibold leading-tight text-blue-900 mb-6">Find the best talent faster with smarter candidate insights.</h1>
        <p className="mx-auto max-w-2xl text-blue-700 mb-10">A modern recruitment dashboard that turns resumes into high-value recommendations, skill gap intelligence, and actionable candidate summaries.</p>

        <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
          <button
            onClick={() => setPage("jobs")}
            className="rounded-2xl bg-blue-600 px-8 py-4 text-sm font-semibold text-white transition hover:bg-blue-700"
          >
            View as Applicant
          </button>
          <button
            onClick={() => setPage("adminLogin")}
            className="rounded-2xl border border-blue-600 bg-white px-8 py-4 text-sm font-semibold text-blue-700 transition hover:bg-blue-50"
          >
            View as Admin
          </button>
        </div>
      </div>
    </div>
  );
}