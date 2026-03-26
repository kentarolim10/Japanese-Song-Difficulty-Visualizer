import { useParams, Link } from "react-router-dom";

export default function SongDashboard() {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="space-y-6">
      <Link
        to="/"
        className="inline-flex items-center text-blue-600 hover:text-blue-800"
      >
        <svg
          className="w-4 h-4 mr-2"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        Back to song list
      </Link>

      <div className="bg-white rounded-lg shadow-sm border p-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Song Dashboard
        </h2>
        <p className="text-gray-600 mb-6">Song ID: {id}</p>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            D3 Visualizations Coming Soon
          </h3>
          <p className="mt-2 text-gray-500">
            This dashboard will display detailed analysis charts and visualizations for this song.
          </p>
        </div>
      </div>
    </div>
  );
}
