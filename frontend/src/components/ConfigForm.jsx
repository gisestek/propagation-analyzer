import { useState } from "react";
import { uploadFile } from "../api";

export default function ConfigForm({ onData }) {
  const [locator, setLocator] = useState("KP26vl");
  const [bin, setBin] = useState(1000);
  const [file, setFile] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    if (!file) return;
    const data = await uploadFile(file, locator, bin);
    // pass both results and selected bin to App
    onData({ data, bin: Number(bin), locator });
  }

  return (
    <form onSubmit={handleSubmit} style={{ display: "grid", gap: "0.5rem", maxWidth: 520 }}>
      <div>
        <label>Own Locator:&nbsp;</label>
        <input value={locator} onChange={e => setLocator(e.target.value)} />
      </div>
      <div>
        <label>Distance Bin:&nbsp;</label>
        <select value={bin} onChange={e => setBin(Number(e.target.value))}>
          <option value={100}>100 km</option>
          <option value={500}>500 km</option>
          <option value={1000}>1000 km</option>
        </select>
      </div>
      <div>
        <label>Log File:&nbsp;</label>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
      </div>
      <button type="submit">Analyze</button>
    </form>
  );
}
