import { useState, useEffect } from 'react';
import type { ImageRow as ImageRowType } from '../types/generated';
import { config } from '../config';
import ImageRow from '../components/ImageRow';
import TableHeader from '../components/TableHeader';
import Statistics from '../components/Statistics';
import TailwindTest from "../components/TailwindTest.tsx";
import fetchImageRows from "../api/fetchImageRows.ts";

// Explicitly enable HMR for this component
if (import.meta.hot) {
  import.meta.hot.accept();
}

// Loading state component
const LoadingState = () => (
  <div className="flex justify-center items-center h-64">
    <div className="text-gray-600">Loading image rows...</div>
  </div>
);

// Error state component
const ErrorState = ({ message }: { message: string }) => (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
    <span className="block sm:inline">{message}</span>
  </div>
);

// Empty state component
const EmptyState = () => (
  <div className="bg-white shadow-md rounded-lg p-6 text-center text-gray-500">
    No image rows found
  </div>
);

export const ImageRows = () => {
  const [sortConfig, setSortConfig] = useState<{ column: string, direction: "asc" | "desc" }>({
    column: "selected_match", // default: backend order
    direction: "asc",
  });
  const [imageRows, setImageRows] = useState<ImageRowType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function sortRows(rows: ImageRowType[], config: typeof sortConfig) {
    const {column, direction} = config;
    let sorted: ImageRowType[];

    if (column === "selected_match" || column === "license") {
      sorted = [...rows].sort((a, b) => {
        const x = a.best_match_number;
        const y = b.best_match_number;
        return direction === "asc" ? x - y : y - x;
      });
    } else {
      sorted = [...rows].sort((a, b) => {
        const x = a[column as keyof ImageRowType] ?? "";
        const y = b[column as keyof ImageRowType] ?? "";
        if (typeof x === "string" && typeof y === "string") {
          return direction === "asc" ? x.localeCompare(y) : y.localeCompare(x);
        } else if (typeof x === "number" && typeof y === "number") {
          return direction === "asc" ? x - y : y - x;
        } else {
          return 0;
        }
      });
    }
    return sorted;
  }

  function handleSort(column: string) {
    setSortConfig((cur) => {
      const isSame = cur.column === column;
      const direction = isSame && cur.direction === "asc" ? "desc" : "asc";
      return {column, direction};
    });
  }

  useEffect(() => {
    fetchImageRows(setImageRows, setLoading, setError);
  }, []);


  // Update displayed rows on sort change**
  useEffect(() => {
    setImageRows(sortRows(imageRows, sortConfig));
  }, [sortConfig]);


  useEffect(() => {
    document.title = "Image Collection";
  }, []);

  // Render content based on state
  const renderRows = () => {
    if (loading) {
      return <LoadingState/>;
    }

    if (error) {
      return <ErrorState message={error}/>;
    }

    if (!imageRows || imageRows.length === 0) {
      return <EmptyState/>;
    }

    return (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          <TableHeader onSort={handleSort} sortConfig={sortConfig} />
          <div className="divide-y">
            {imageRows.map((row) => (
                <ImageRow
                    row={row}
                    onRowsChange={setImageRows}
                />
            ))}
          </div>
        </div>
    );
  };

  return (
      <div className="max-w-8xl py-8 px-6 md:px-10 bg-gray-50 min-h-screen" style={{marginLeft: "50px"}}>
        <h1 className="text-3xl font-bold mb-10 text-gray-800 ml-2">Image Collection</h1>

        {config.showTailwindTest && <TailwindTest/>}

        <Statistics imageRows={imageRows}/>

        {renderRows()}
      </div>
  );
};

export default ImageRows;
