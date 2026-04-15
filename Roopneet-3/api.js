const BASE_URL = 'http://localhost:8000';

const api = {
  async upload(file) {
    const fd = new FormData();
    fd.append('file', file);
    try {
      const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: fd });
      if (!res.ok) {
        const e = await res.json().catch(() => ({ detail: 'Upload failed' }));
        throw new Error(e.detail || `Upload failed with status ${res.status}`);
      }
      return res.json();
    } catch (err) {
      throw new Error(err.message || 'Upload failed - could not reach server');
    }
  },

  async profile(datasetId) {
    try {
      const res = await fetch(`${BASE_URL}/profile/${datasetId}`);
      if (!res.ok) {
        const e = await res.json().catch(() => ({ detail: 'Profile failed' }));
        throw new Error(e.detail || `Profile failed with status ${res.status}`);
      }
      const data = await res.json();
      return data;
    } catch (err) {
      throw new Error(err.message || 'Profile failed - could not reach server');
    }
  },

  async process(datasetId, config) {
    try {
      const res = await fetch(`${BASE_URL}/process/${datasetId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });
      if (!res.ok) {
        const e = await res.json().catch(() => ({ detail: 'Processing failed' }));
        throw new Error(e.detail || `Processing failed with status ${res.status}`);
      }
      return res.json();
    } catch (err) {
      throw new Error(err.message || 'Processing failed - could not reach server');
    }
  },

  downloadUrl(datasetId) { return `${BASE_URL}/download/${datasetId}`; },
  pipelineUrl(datasetId) { return `${BASE_URL}/download-pipeline/${datasetId}`; },
  reportUrl(datasetId) { return `${BASE_URL}/report/${datasetId}`; },
  downloadReportUrl(datasetId) { return `${BASE_URL}/download-report/${datasetId}`; },
};

window.api = api;
