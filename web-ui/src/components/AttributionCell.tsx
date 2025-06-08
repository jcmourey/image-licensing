import React from 'react';

interface AttributionCellProps {
  attribution: string | null;
  licenseUrl: string | null;
  licensed_by: string | null;
}

const AttributionCell: React.FC<AttributionCellProps> = ({ attribution, licenseUrl, licensed_by }) => {
  // Determine the display text
  const displayText = attribution || 'No license information';

  // Function to format URL for display by adding word breaks
  const formatUrlForDisplay = (url: string): string => {
    // Break after common URL parts like https://, www., .com/, etc.
    return url
        .replace(/(https?:\/\/)/, '$1\u200B') // Add zero-width space after protocol
        .replace(/(\/)(?!$)/g, '$1\u200B') // Add zero-width space after each slash (except last one)
        .replace(/(\.)(?!\s|$)/g, '$1\u200B'); // Add zero-width space after each dot (except last one)
  };

  return (
      <div className="w-full text-center">
        {licenseUrl ? (
            <div>
              {/*<div className="font-medium text-blue-700 mb-1">{displayText}</div>*/}
              <a
                  href={licenseUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-blue-500 hover:underline break-all overflow-wrap-anywhere"
                  style={{
                    overflowWrap: 'break-word',
                    wordWrap: 'break-word',
                    wordBreak: 'break-word',
                    hyphens: 'auto',
                    display: 'inline-block',
                    maxWidth: '100%'
                  }}
              >
                {formatUrlForDisplay(displayText)}
              </a>
            </div>
        ) : (
            <span className="text-gray-500">{displayText}</span>
        )}
        {licensed_by && (
          <div className="text-xs text-gray-400 mt-1">License: {licensed_by}</div>
        )}
      </div>
  );
};

export default AttributionCell;

