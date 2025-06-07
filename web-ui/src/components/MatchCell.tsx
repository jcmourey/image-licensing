import React from 'react';
import { getDomain } from "../utils/string";

interface MatchCellProps {
  imageUrl: string | null;
  pageUrl: string | null;
  matchingType: string | null;
  onShowPopup: (imageUrl: string | null) => void;
  onHidePopup: () => void;
}

const MatchCell: React.FC<MatchCellProps> = ({ 
  imageUrl, 
  pageUrl, 
  matchingType,
  onShowPopup, 
  onHidePopup 
}) => {
  if (!imageUrl || !pageUrl) {
    return <span>No match found</span>;
  }

  return (
    <div className="flex flex-col items-center text-center">
      {matchingType && (
        <span className="text-xs font-medium text-gray-500 mb-1 inline-block px-2 py-1 bg-gray-100 rounded">
          {matchingType}
        </span>
      )}
      <img
        src={imageUrl}
        alt="Matched Image"
        className="w-40 h-25 object-cover rounded cursor-zoom-in"
        onMouseEnter={() => onShowPopup(imageUrl)}
        onMouseLeave={onHidePopup}
      />
      <a 
        href={pageUrl} 
        target="_blank" 
        rel="noopener noreferrer" 
        className="text-blue-600 hover:underline mt-2"
      >
        {getDomain(pageUrl)}
      </a>
    </div>
  );
};

export default MatchCell;
