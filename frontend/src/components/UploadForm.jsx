// frontend/src/components/UploadForm.jsx
import { useState } from "react";

export default function UploadForm({ onResult }) {
  const [locator, setLocator] = useState("KP26vl");
  const [binKm, setBinKm] = useState(1000);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append("locator", locator);
    formData.append("bin_km", binKm);
    formData.append("file", file);

    setLoading(true);
    try {
      // ✅ relative path → works whether you access through :8000 or via nginx domain
      const res = await fetch("/api/analyze", { method: "POST", body: formData });

      // Better error detail
      if (!res.ok) {
        const msg = await res.text().catch(() => "");
        throw new Error(msg || `HTTP ${res.status}`);
      }
      const data = await res.json();
      onResult(data);
    } catch (err) {
      console.error(err);
      alert(`Error analyzing file:\n${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="p-4 border rounded bg-white shadow mb-4 space-y-2">
      <div>
        <label className="block font-medium">Locator:</label>
        <input className="border rounded p-1 w-full" value={locator} onChange={(e) => setLocator(e.target.value)} />
      </div>
      <div>
        <label className="block font-medium">Bin size (km):</label>
        <input className="border rounded p-1 w-full" type="number" value={binKm} onChange={(e) => setBinKm(e.target.value)} />
      </div>
      <div>
        <input type="file" accept=".csv,.txt" onChange={(e) => setFile(e.target.files[0])} />
      </div>
      <button type="submit" disabled={loading} className="px-4 py-2 bg-blue-600 text-white rounded">
        {loading ? "Analyzing..." : "Upload & Analyze"}
      </button>
    </form>
  );
}

