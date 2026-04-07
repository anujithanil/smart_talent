export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 text-slate-300">
      <div className="h-12 w-12 rounded-full border-4 border-slate-700 border-t-cyan-400 animate-spin" />
      <p className="mt-3 text-sm text-slate-300">{label}</p>
    </div>
  );
}
