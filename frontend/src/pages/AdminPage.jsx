import JobForm from "../components/JobForm";

export default function AdminPage() {
  const [jobs, setJobs] = useState([]);

const handleNewJob = (job) => {
  setJobs((prev) => [...prev, job]); // instant UI update
};
  return (
    <div>
      <h1 className="text-xl font-bold mb-4">Create Job</h1>
      <JobForm onJobCreated={handleNewJob} />
    </div>
  );
}