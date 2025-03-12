import React, { useState } from "react";
import { Loader2 } from "lucide-react";
import { PieChart, Pie, Cell, Legend, Tooltip, ResponsiveContainer } from "recharts";
import ReactWordCloud from "react-d3-cloud";
import "./index.css";
import "./App.css";

export default function App() {
  const [videoLink, setVideoLink] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [resultMessage, setResultMessage] = useState("");
  const [sentimentData, setSentimentData] = useState([]);
  const [keywordsSummary, setKeywordsSummary] = useState({
    positive: [],
    negative: [],
    neutral: [],
    mixed: [],
  });
  const [selectedSentiment, setSelectedSentiment] = useState("positive");
  const [contentSuggestions, setContentSuggestions] = useState([]);
  const [executiveSummary, setExecutiveSummary] = useState("");

  const handleSubmit = async () => {
    if (!videoLink.trim()) {
      alert("Please enter a YouTube link.");
      return;
    }

    setIsLoading(true);
    setResultMessage("");
    setSentimentData([]);
    setKeywordsSummary({ positive: [], negative: [], neutral: [], mixed: [] });
    setContentSuggestions([]);
    setExecutiveSummary("");

    const url = `${import.meta.env.VITE_API_URL}/run-etl?videoLink=${videoLink}`;

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP status ${response.status}`);

      const data = await response.json();

      if (data.status === "Success") {
        setSentimentData([
          { name: "Positive", value: data.sentiment_breakdown.positive },
          { name: "Negative", value: data.sentiment_breakdown.negative },
          { name: "Neutral", value: data.sentiment_breakdown.neutral },
          { name: "Mixed", value: data.sentiment_breakdown.mixed },
        ]);

        setKeywordsSummary(data.keywords_summary || {});
        setContentSuggestions(data.content_suggestions || []);
        setExecutiveSummary(data.executive_summary || "No executive summary available.");
      } else {
        setResultMessage(`Error: ${data.error}`);
      }
    } catch (error) {
      setResultMessage(`Failed to execute ETL pipeline. Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const COLORS = ["#0088FE", "#FF8042", "#00C49F", "#FFBB28"];

  const rawKeywords = keywordsSummary[selectedSentiment] || {};
  const wordCloudData = Object.entries(rawKeywords).map(([text, value]) => ({ text, value }));

  const fontSizeMapper = (word) => Math.log2(word.value) * 30;
  const rotate = () => 0;

  const summaryBulletPoints = executiveSummary
    ? executiveSummary.split("\n").map((line) => line.trim()).filter(Boolean)
    : [];

  return (
    <div className="min-h-screen bg-gray-50 p-6 flex justify-center items-start">
      <div className="w-full max-w-4xl bg-white rounded-md shadow-lg p-6 space-y-6 flex flex-col">
        <h1 className="text-3xl font-bold text-center">YouTube Sentiment Analysis</h1>

        {/* Input Section */}
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <input
            type="text"
            placeholder="Enter YouTube video link"
            value={videoLink}
            onChange={(e) => setVideoLink(e.target.value)}
            className="flex-1 w-full max-w-sm border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />

          <button
            onClick={handleSubmit}
            disabled={isLoading}
            className="inline-flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? <Loader2 className="animate-spin mr-2 w-5 h-5" /> : "Run"}
          </button>
        </div>

        {/* Status Message */}
        {resultMessage && (
          <p
            className={`text-center font-semibold p-2 rounded ${
              resultMessage.startsWith("Success")
                ? "text-green-800 bg-green-100"
                : "text-red-800 bg-red-100"
            }`}
          >
            {resultMessage}
          </p>
        )}

        {/* Main Content */}
        <div className="overflow-y-auto h-96 space-y-4">
          
          {/* Sentiment Pie Chart */}
          {sentimentData.length > 0 && (
            <div className="sentiment-chart">
              <h3 className="text-lg font-semibold text-center">Sentiment Breakdown</h3>
              <ResponsiveContainer width="100%" height={350}>
                <PieChart>
                  <Pie
                    data={sentimentData}
                    cx="36%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {sentimentData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}

          {/* Keyword Highlights */}
          <div className="bg-gray-50 border border-gray-200 rounded p-4">
            <h3 className="text-xl font-semibold mb-4">Keyword Highlights ({selectedSentiment} comments)</h3>

            <div className="flex items-center space-x-3 mb-4">
              <label htmlFor="sentimentSelect" className="font-medium">Select sentiment:</label>
              <select
                id="sentimentSelect"
                onChange={(e) => setSelectedSentiment(e.target.value)}
                defaultValue="positive"
                className="border border-gray-300 rounded p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="positive">Positive</option>
                <option value="negative">Negative</option>
                <option value="neutral">Neutral</option>
                <option value="mixed">Mixed</option>
              </select>
            </div>

            <div className="mx-auto flex justify-center">
              <ReactWordCloud data={wordCloudData} fontSizeMapper={fontSizeMapper} rotate={rotate} padding={2} width={500} height={300} />
            </div>
          </div>

          {/* Content Suggestions */}
          <div className="bg-gray-50 border border-gray-200 rounded p-4">
            <h3 className="text-xl font-semibold mb-2">Content Suggestions</h3>
            {contentSuggestions.length > 0 ? (
              <ul className="list-disc ml-6 space-y-1">
                {contentSuggestions.map((suggestion, idx) => <li key={idx}>{suggestion}</li>)}
              </ul>
            ) : (
              <p>No content suggestions available.</p>
            )}
          </div>

          {/* Executive Summary */}
          <div id="executive-summary" className="bg-gray-50 border border-gray-200 rounded p-4">
            <h3 className="text-xl font-semibold mb-2">Executive Summary</h3>
            {summaryBulletPoints.length > 0 ? (
              <ul className="list-disc ml-6 space-y-1">
                {summaryBulletPoints.map((point, index) => <li key={index}>{point}</li>)}
              </ul>
            ) : (
              <p>No executive summary available.</p>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
