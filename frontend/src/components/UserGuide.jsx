export default function UserGuide() {
  return (
    <div className="p-4 mb-4 bg-gray-100 rounded-lg shadow">
      <h2 className="text-lg font-bold mb-2">📖 User Guide</h2>
      <p>
        Upload your <code>ALL.TXT</code> (WSJT-X) or <code>.csv</code> (Log4OM) file,
        set your QTH locator and distance bin size, then click{" "}
        <strong>Upload & Analyze</strong>.
      </p>
      <p className="mt-2">
        The tool will show total QSOs/spots per band and a distance histogram.
        Switch between <strong>Raw Distances</strong> and{" "}
        <strong>By Band</strong> for more detail.
      </p>
    </div>
  );
}

