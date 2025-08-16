import { useState } from "react";
import ConfigForm from "./components/ConfigForm";
import BandPie from "./components/BandPie";
import DistanceBar from "./components/DistanceBar";
import DistanceByBand from "./components/DistanceByBand";

export default function App() {
  const [payload, setPayload] = useState(null);
  const data = payload?.data;
  const binKm = payload?.bin;
  const total = (data && (data.total_qsos || data.total_spots)) || 0;

  return (
    <div style={{ fontFamily: "sans-serif", padding: "1rem", maxWidth: 1200, margin: "0 auto" }}>
      <h1>Propagation Analyzer</h1>
      <ConfigForm onData={setPayload} />

      {data && (
        <>
          <div style={{ marginTop: "1rem", padding: "0.75rem", background: "#f4f4f4", borderRadius: 8 }}>
            <strong>Source:</strong> {data.source || "-"} &nbsp;|&nbsp;
            <strong>Total:</strong> {total.toLocaleString()} &nbsp;|&nbsp;
            <strong>Locator:</strong> {payload?.locator || "-"}
          </div>

          <div style={{ marginTop: "1rem", display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <BandPie bands={data.bands} />
            <div>
              <h3>Distance histogram (bin ≈ {binKm} km)</h3>
              <DistanceBar hist={data.distance_histogram} binKm={binKm} />
            </div>
          </div>

          <div style={{ marginTop: "1.25rem" }}>
            <h2>Per-band distance histograms</h2>
            <DistanceByBand byBand={data.distance_histograms_by_band} binKm={binKm} />
          </div>

          <details style={{ marginTop: "1rem" }}>
            <summary>Raw JSON (debug)</summary>
            <pre style={{ background: "#eee", padding: "1rem" }}>
              {JSON.stringify(data, null, 2)}
            </pre>
          </details>
        </>
      )}
    </div>
  );
}

