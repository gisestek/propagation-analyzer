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
    onData(data);
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Own Locator: </label>
        <input value={locator} onChange={e => setLocator(e.target.value)} />
      </div>
      <div>
        <label>Distance Bin: </label>
        <select value={bin} onChange={e => setBin(e.target.value)}>
          <option value={100}>100 km</option>
          <option value={500}>500 km</option>
          <option value={1000}>1000 km</option>
        </select>
      </div>
      <div>
        <label>Log File: </label>
        <input type="file" onChange={e => setFile(e.target.files[0])} />
      </div>
      <button type="submit">Analyze</button>
    </form>
  );
}
