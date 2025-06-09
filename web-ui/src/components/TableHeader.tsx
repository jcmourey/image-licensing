import React from "react";

type SortConfig = {
  column: string;
  direction: "asc" | "desc";
};

interface TableHeaderProps {
  onSort: (column: string) => void;
  sortConfig: SortConfig;
}

const columns = [
  { key: "image", label: "Image", sortable: false },
  { key: "selected_match", label: "Best Match", sortable: true },
  { key: "license", label: "Best License", sortable: true },
  { key: "used_in", label: "Used In", sortable: true },
  { key: "comment", label: "Comment", sortable: true },
  { key: "replacement_page_url", label: "Replacement Image", sortable: true },
];

export const TableHeader: React.FC<TableHeaderProps> = ({ onSort, sortConfig }) => (
  <div className="grid grid-cols-6 bg-gray-100 font-medium">
    {columns.map(col => (
      <div
        key={col.key}
        className={`p-3 border-b border-r text-center${col.sortable ? " cursor-pointer select-none hover:bg-gray-200" : ""}`}
        onClick={col.sortable ? () => onSort(col.key) : undefined}
      >
        {col.label}
        {col.sortable && sortConfig.column === col.key && (
          <span className="ml-1">{sortConfig.direction === "asc" ? "▲" : "▼"}</span>
        )}
      </div>
    ))}
  </div>
);

export default TableHeader;
