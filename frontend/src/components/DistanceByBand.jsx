import DistanceBar from "./DistanceBar";
import { PALETTE } from "../colors";

export default function DistanceByBand({ byBand, binKm }) {
  if (!byBand || Object.keys(byBand).length === 0) return null;

  // Sort bands by total counts desc
  const entries = Object.entries(byBand)
    .map(([band, hist]) => [band, Object.values(hist).reduce((s,v)=>s+Number(v||0),0), hist])
    .sort((a,b)=>b[1]-a[1]);

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
      {entries.map(([band, _, hist], i) => (
        <div key={band}>
          <h3 style={{ marginBottom: 8 }}>{band}</h3>
          <DistanceBar hist={hist} binKm={binKm} color={PALETTE[i % PALETTE.length]} />
        </div>
      ))}
    </div>
  );
}
