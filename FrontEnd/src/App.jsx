import { useState } from "react";
import axios from "axios";
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";
import ChartDataLabels from "chartjs-plugin-datalabels";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ChartDataLabels);

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
    <div className="min-h-screen flex items-center justify-center bg-gray-100 p-6">
      <div className="w-full max-w-md bg-white shadow-lg rounded-2xl p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">Incident Prediction</h1>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-gray-700 text-sm font-medium mb-2">Date:</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              required
            />
          </div>

          <div>
            <label className="block text-gray-700 text-sm font-medium mb-2">Assignment Group:</label>
            <input
              type="text"
              value={assignmentGroup}
              onChange={(e) => setAssignmentGroup(e.target.value)}
              placeholder="Enter assignment group"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-800 transition-all font-semibold text-lg"
            disabled={loading}
          >
            {loading ? "Submitting..." : "Submit"}
          </button>
        </form>


        {error && <p className="text-red-500 text-sm mt-3 text-center">{error}</p>}

        {response && (
          <div className="mt-6 p-6 bg-gray-50 rounded-lg shadow-md">
            <h2 className="text-gray-700 font-semibold text-lg mb-2">Prediction Results</h2>
            <p className="text-gray-600"><strong>Date:</strong> {response.date}</p>
            <p className="text-gray-600"><strong>Assignment Group:</strong> {response.assignment_group}</p>

            <h3 className="text-gray-700 font-semibold mt-4">Predictions:</h3>
            <div className="w-full h-60 flex justify-center">
              <Bar
                data={{
                  labels: ["P1", "P2", "P3", "P4"],
                  datasets: [
                    {
                      label: "Predicted Incidents",
                      data: [
                        response.predictions.P1,
                        response.predictions.P2,
                        response.predictions.P3,
                        response.predictions.P4,
                      ],
                      backgroundColor: ["#FFDDDD", "#FF9999", "#FF6666", "#CC0000"],
                    },
                  ],
                }}
                options={{
                  responsive: true,
                  maintainAspectRatio: false,
                  scales: {
                    y: {
                      beginAtZero: true,
                    },
                  },
                  plugins: {
                    tooltip: {
                      enabled: true,
                    },
                    datalabels: {
                      anchor: "end",
                      align: "top",
                      formatter: (value) => `${value}%`,
                      color: "black",
                      font: {
                        weight: "bold",
                      },
                    },
                  },
                }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
