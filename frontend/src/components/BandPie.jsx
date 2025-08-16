import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend } from "recharts";
import { PALETTE } from "../colors";

export default function BandPie({ bands }) {
  if (!bands || Object.keys(bands).length === 0) return null;
  const data = Object.entries(bands)
    .map(([name, value]) => ({ name, value: Number(value) || 0 }))
    .sort((a, b) => b.value - a.value);

  const TOP = 10;
  const top = data.slice(0, TOP);
  const rest = data.slice(TOP);
  if (rest.length) top.push({ name: "Others", value: rest.reduce((s, d) => s + d.value, 0) });

  return (
    <div style={{ height: 360 }}>
      <h3>Band distribution</h3>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie data={top} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius="80%" label>
            {top.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

