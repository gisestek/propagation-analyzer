export default function Results({ data }) {
  return (
    <div>
      <h2>Band Summary</h2>
      <table border="1">
        <thead>
          <tr><th>Band</th><th>Spots</th><th>Median</th><th>Mean</th><th>Max</th></tr>
        </thead>
        <tbody>
          {data.summary.map(s => (
            <tr key={s.band}>
              <td>{s.band}</td><td>{s.spots}</td><td>{s.median}</td><td>{s.mean}</td><td>{s.max}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2>Distance Histograms</h2>
      {Object.keys(data.histograms).map(b => (
        <div key={b}>
          <h3>{b}</h3>
          <pre>{JSON.stringify(data.histograms[b], null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}
