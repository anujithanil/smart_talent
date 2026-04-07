export default function Navbar({ setPage, token }) {
  return (
    <div className="w-full bg-white border-b border-blue-200 px-8 py-4 backdrop-blur-md flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between shadow-sm shadow-blue-200/50">

      <div className="flex items-center gap-3">
        
        <div>
          <h1 className="text-xl font-semibold text-blue-900 cursor-pointer" onClick={() => setPage("landing")}>CYMONIC.AI</h1>
          <p className="text-sm text-blue-600">Talent Intelligence Portal</p>
        </div>
      </div>

      {/* NAV */}
      <div className="flex gap-4">

        <button
          onClick={() => setPage("jobs")}
          className="rounded-2xl border border-blue-300 bg-white px-4 py-2 text-sm text-blue-700 transition hover:bg-blue-50"
        >
          Applicant View
        </button>

        <button
          onClick={() => setPage("adminLogin")}
          className="rounded-2xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-blue-700"
        >
          Admin View
        </button>

      </div>
    </div>
  );
}