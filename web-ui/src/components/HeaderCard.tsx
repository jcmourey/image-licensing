import React from "react";

interface HeaderCardProps {
  name: string;
  matchCount: number;
  licenseCount: number;
}

const HeaderCard: React.FC<HeaderCardProps> = ({ name, matchCount, licenseCount }) => {
  return (
    <div className="bg-gray-100 flex items-center justify-between px-4" style={{ height: "36px" }}>
      <h2 className="font-medium text-gray-800 truncate" title={name}>
        {name}
      </h2>
      <div className="flex space-x-3">
        <div className="px-2 py-1 bg-gray-50 rounded-md text-xs">
          <span className="font-medium">{matchCount}</span> matches
        </div>
        <div className="px-2 py-1 bg-gray-50 rounded-md text-xs">
          <span className="font-medium">{licenseCount}</span> licenses
        </div>
      </div>
    </div>
  );
};

export default HeaderCard;
