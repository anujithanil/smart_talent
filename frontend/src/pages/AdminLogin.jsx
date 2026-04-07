import { useState } from "react";
import API from "../api";

export default function AdminLogin({ setToken, setPage }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const login = async () => {
    try {
      const res = await API.post("/admin/login", {
        username,
        password,
      });

      localStorage.setItem("token", res.data.token);
      setToken(res.data.token);
      setPage("adminDashboard");
    } catch {
      alert("Invalid login");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-blue-100 to-blue-200 px-4 py-12 text-blue-900 flex items-center justify-center">
      <div className="w-full max-w-md rounded-3xl border border-blue-300 bg-white p-8 shadow-lg shadow-blue-200/40">
        <div className="mb-8 text-center">
          <p className="text-sm uppercase tracking-[0.2em] text-blue-600">Secure Admin Access</p>
          <h2 className="mt-3 text-3xl font-semibold text-blue-900">Admin Login</h2>
          <p className="mt-2 text-sm text-blue-600">Manage jobs, view insights, and review top candidates.</p>
        </div>

        <div className="space-y-4">
          <input
            placeholder="Username"
            className="w-full rounded-2xl border border-blue-300 bg-blue-50 px-4 py-3 text-blue-900 placeholder:text-blue-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 outline-none"
            onChange={(e) => setUsername(e.target.value)}
          />

          <div className="relative">
            <input
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              className="w-full rounded-2xl border border-blue-300 bg-blue-50 px-4 py-3 pr-12 text-blue-900 placeholder:text-blue-500 focus:border-blue-400 focus:ring-2 focus:ring-blue-400/20 outline-none"
              onChange={(e) => setPassword(e.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowPassword((prev) => !prev)}
              className="absolute right-3 top-3 text-blue-600 hover:text-blue-900 transition"
            >
              {showPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-4.803m5.596-3.856a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>

          <button onClick={login} className="w-full rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-blue-700">
            Login
          </button>
        </div>
      </div>
    </div>
  );
}