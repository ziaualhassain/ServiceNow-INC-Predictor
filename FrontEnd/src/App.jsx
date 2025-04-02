import { useState } from "react";
import axios from "axios";

function App() {
  const [date, setDate] = useState("");
  const [assignmentGroup, setAssignmentGroup] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/predict",
        {
          date,
          assignment_group: assignmentGroup,
        },
        {
          headers: { "Content-Type": "application/json" },
        }
      );
      setResponse(res.data);
    } catch (err) {
      setError("Failed to fetch data. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-6">
      <div className="bg-white p-6 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center text-gray-700 mb-6">Inc Prediction For Assignment Group</h1>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="flex flex-col">
            <label htmlFor="date" className="font-medium text-gray-700">Date</label>
            <input
              id="date"
              type="date"
              className="border border-gray-300 p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </div>

          <div className="flex flex-col">
            <label htmlFor="assignment-group" className="font-medium text-gray-700">Assignment Group</label>
            <input
              id="assignment-group"
              type="text"
              className="border border-gray-300 p-2 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter assignment group"
              value={assignmentGroup}
              onChange={(e) => setAssignmentGroup(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 hover:bg-blue-600 text-white font-semibold p-2 rounded-md transition-all duration-200"
            disabled={loading}
          >
            {loading ? "Submitting..." : "Submit"}
          </button>
        </form>

        {error && (
          <div className="mt-4 p-3 border border-red-300 rounded-md bg-red-50 text-red-600 text-center">
            {error}
          </div>
        )}

        {response && (
          <div className="mt-6 p-4 border rounded-md bg-gray-50 shadow-sm">
            <h2 className="text-lg font-semibold border-b pb-2 mb-3 text-gray-700">Prediction Results</h2>
            
            <div className="mb-4 text-gray-600">
              <p className="flex justify-between py-1">
                <span className="font-medium">Date:</span>
                <span>{response.date}</span>
              </p>
              <p className="flex justify-between py-1">
                <span className="font-medium">Assignment Group:</span>
                <span>{response.assignment_group}</span>
              </p>
            </div>

            <h3 className="font-semibold mb-2 text-gray-700">Predictions:</h3>
            <ul className="space-y-1">
              {Object.entries(response.predictions).map(([key, value]) => (
                <li key={key} className="flex justify-between px-2 py-1 border-b border-gray-200 text-gray-600">
                  <span className="font-medium">{key}:</span>
                  <span>{value}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
