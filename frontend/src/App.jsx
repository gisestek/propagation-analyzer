import { useState } from "react";
import LoginForm from "./components/LoginForm";
import ConfigForm from "./components/ConfigForm";
import FileUpload from "./components/FileUpload";
import Results from "./components/Results";
import { analyzeFile } from "./api";

function App() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [results, setResults] = useState(null);

  if (!loggedIn) return <LoginForm onLogin={() => setLoggedIn(true)} />;

  return (
    <div className="p-4">
      <h1 className="text-xl font-bold">FT8 Web Analyzer</h1>
      <ConfigForm onAnalyze={async (config, file) => {
        const res = await analyzeFile(config, file);
        setResults(res);
      }} />
      {results && <Results data={results} />}
    </div>
  );
}

export default App;
