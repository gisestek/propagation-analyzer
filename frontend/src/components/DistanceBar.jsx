import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid } from "recharts";

export default function DistanceBar({ hist, binKm, color }) {
  if (!hist || Object.keys(hist).length === 0) return null;
  const keys = Object.keys(hist).map(Number).sort((a,b)=>a-b);
  const inferred = binKm || (keys.length>1 ? keys[1]-keys[0] : 1000);
  const data = keys.map(k => ({ bin: `${k}-${k+inferred-1}`, start: k, count: Number(hist[k])||0 }));

  return (
    <div style={{ height: 360 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="bin" interval={0} tick={{ fontSize: 11 }} />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill={color || undefined} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

