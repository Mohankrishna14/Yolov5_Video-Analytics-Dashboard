import React, { useState } from "react";
import axios from "axios";

export default function App() {
  const [file, setFile] = useState(null);
  const [useGpu, setUseGpu] = useState(false);
  const [loading, setLoading] = useState(false);
  const [resultUrl, setResultUrl] = useState(null);
  const [warnings, setWarnings] = useState([]);

  const onFileChange = (e) => {
    setFile(e.target.files[0]);
    setResultUrl(null);
    setWarnings([]);
  };

  const onSubmit = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("use_gpu", String(useGpu));

    try {
      const resp = await axios.post("http://localhost:8000/predict-image", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (resp.data.status === "ok") {
        setResultUrl(resp.data.output_url);
        setWarnings(resp.data.warnings || []);
      } else {
        alert("Error: " + JSON.stringify(resp.data));
      }
    } catch (err) {
      console.error(err);
      alert("Request failed: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <h1>YOLOv5 Image Inference</h1>

      <div style={{ marginBottom: 12 }}>
        <input type="file" accept="image/*" onChange={onFileChange} />
      </div>

      <div style={{ marginBottom: 12 }}>
        <label>
          <input type="checkbox" checked={useGpu} onChange={(e) => setUseGpu(e.target.checked)} />
          Use GPU if available
        </label>
      </div>

      <div>
        <button onClick={onSubmit} disabled={!file || loading}>
          {loading ? "Processing..." : "Run Inference"}
        </button>
      </div>

      {warnings && warnings.length > 0 && (
        <div style={{ marginTop: 12, color: "orange" }}>
          <strong>Warnings:</strong>
          <ul>
            {warnings.map((w, i) => (
              <li key={i}>{w}</li>
            ))}
          </ul>
        </div>
      )}

      {resultUrl && (
        <div style={{ marginTop: 20 }}>
          <h2>Annotated result</h2>
          <img src={resultUrl} alt="annotated" style={{ maxWidth: "100%" }} />
          <p>
            If the image does not display, open this URL in a new tab: <a href={resultUrl}>{resultUrl}</a>
          </p>
        </div>
      )}
    </div>
  );
}
