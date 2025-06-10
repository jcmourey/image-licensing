import {useEffect, useState} from 'react';
import type {ImageRow} from '../types/generated';
import {config} from '../config';
import ImageRowView from '../components/ImageRowView.tsx';
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
  const [imageRows, setImageRows] = useState<ImageRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  function sortRows(rows: ImageRow[], config: typeof sortConfig) {
    const {column, direction} = config;

    return [...rows].sort((a, b) => {
      const x = a[column as keyof ImageRow] ?? "";
      const y = b[column as keyof ImageRow] ?? "";
      if (typeof x === "string" && typeof y === "string") {
        return direction === "asc" ? x.localeCompare(y) : y.localeCompare(x);
      } else if (typeof x === "number" && typeof y === "number") {
        return direction === "asc" ? x - y : y - x;
      } else {
        return 0;
      }
    });
  }

  function handleSort(column: string) {
    setSortConfig((cur) => {
      const isSame = cur.column === column;
      const direction = isSame && cur.direction === "asc" ? "desc" : "asc";
      return {column, direction};
    });
  }

  const handleRowChange = async (id: string) => {
    try {
      console.log(`Updating image row with id: ${id}`);
      const encodedId = encodeURIComponent(id);
      const response = await fetch(`/api/image/${encodedId}/get`);
      if (!response.ok) {
        throw new Error(`Could not fetch image with id: ${id}`);
      }
      const updatedRow: ImageRow = await response.json();
      setImageRows((prevRows) =>
        prevRows.map(row => {
          if (row.id == id) {
            updatedRow.rank = row.rank
            return updatedRow
        } else {}
            return row
        })
      );
    } catch (error) {
      console.error("Failed to update image row:", error);
    }
  };



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
                <ImageRowView
                    row={row}
                    onChange={handleRowChange}
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
