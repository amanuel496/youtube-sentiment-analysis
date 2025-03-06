import React, { useState } from 'react';
import { Loader2 } from 'lucide-react';

export default function App() {
  const [videoId, setVideoId] = useState('');
  const [outputFormat, setOutputFormat] = useState('json');
  const [isLoading, setIsLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState('');

  const handleSubmit = async () => {
    if (!videoId) {
      alert('Please enter a YouTube video ID.');
      return;
    }
    setIsLoading(true);
    setResultMessage('');

    try {
      const response = await fetch(`http://localhost:8000/run-etl?videoId=${videoId}&outputFormat=${outputFormat}`);
      const data = await response.json();

      if (response.ok) {
        setResultMessage(`ETL completed. Output saved to: ${data.filePath}`);
      } else {
        setResultMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      setResultMessage('Failed to execute ETL pipeline. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white shadow-md rounded-md max-w-md w-full p-4">
        <h2 className="text-2xl font-semibold mb-4">YouTube Sentiment Analysis</h2>

        <input
          type="text"
          placeholder="Enter YouTube video ID"
          value={videoId}
          onChange={(e) => setVideoId(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded mb-4"
        />

        <select
          onChange={(e) => setOutputFormat(e.target.value)}
          defaultValue="json"
          className="w-full p-2 border border-gray-300 rounded mb-4"
        >
          <option value="json">JSON</option>
          <option value="csv">CSV</option>
        </select>

        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className="w-full bg-blue-500 hover:bg-blue-600 text-white p-2 rounded disabled:bg-gray-400"
        >
          {isLoading ? <Loader2 className="animate-spin mr-2 inline" /> : 'Run ETL Pipeline'}
        </button>

        {resultMessage && <p className="text-sm text-gray-700 mt-4">{resultMessage}</p>}
      </div>
    </div>
  );
}
