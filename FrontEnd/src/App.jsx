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
      const res = await axios.post("http://127.0.0.1:8000/predict", {
        date,
        assignment_group: assignmentGroup,
      });
      setResponse(res.data);
    } catch (err) {
      setError("Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-400 to-blue-500 p-6">
      <div className="w-full max-w-lg bg-white shadow-xl rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-6 text-center">
          Incident Prediction
        </h1>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Date : </label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-medium mb-1">Assignment Group : </label>
            <input
              type="text"
              value={assignmentGroup}
              onChange={(e) => setAssignmentGroup(e.target.value)}
              placeholder="Enter assignment group"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500 outline-none"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-green-600 text-white pt-10 py-3 rounded-lg hover:bg-black transition-all font-semibold text-lg"
            disabled={loading}
          >
            {loading ? "Submitting..." : "Submit"}
          </button>
        </form>

        {error && <p className="text-red-500 text-sm mt-3 text-center">{error}</p>}

        {response && (
          <div className="mt-6 p-6 bg-gray-100 rounded-lg shadow-md">
            <h2 className="text-gray-700 font-semibold text-lg mb-2">Prediction Results</h2>
            <p className="text-gray-600"><strong>Date:</strong> {response.date}</p>
            <p className="text-gray-600"><strong>Assignment Group:</strong> {response.assignment_group}</p>

            <h3 className="text-gray-700 font-semibold mt-4">Predictions:</h3>
            <ul className="text-gray-600 text-sm mt-2 space-y-2">
              {Object.entries(response.predictions).map(([key, value]) => (
                <li key={key} className="flex justify-between bg-white p-2 rounded shadow-sm">
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
