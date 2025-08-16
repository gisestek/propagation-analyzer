import { useState } from "react";
import UploadForm from "./components/UploadForm";
import BandPie from "./components/BandPie";
import DistanceBar from "./components/DistanceBar";
import DistanceByBand from "./components/DistanceByBand";
import UserGuide from "./components/UserGuide";

export default function App() {
  const [result, setResult] = useState(null);
  const [view, setView] = useState("guide");

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">📡 Propagation Analyzer</h1>

      <div className="flex gap-4 mb-4">
        <button
          onClick={() => setView("guide")}
          className={`px-3 py-1 rounded ${view === "guide" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
        >
          User Guide
        </button>
        <button
          onClick={() => setView("analyze")}
          className={`px-3 py-1 rounded ${view === "analyze" ? "bg-blue-600 text-white" : "bg-gray-200"}`}
        >
          Analyze
        </button>
      </div>

      {view === "guide" && <UserGuide />}
      {view === "analyze" && (
        <>
          <UploadForm onResult={setResult} />
          
          {result && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <BandPie bands={result.bands} />
              <DistanceBar hist={result.distance_histogram} />  {/* <- hist, not histogram */}
            </div>
          )}

          {result && (
            <div className="mt-6">
              <h2 className="text-xl font-semibold mb-2">Per-band distance histograms</h2>
              <DistanceByBand byBand={result.distance_histograms_by_band} /> {/* <- correct key + prop */}
            </div>
          )}
        </>
      )}
    </div>
  );
}

