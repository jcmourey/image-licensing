import React from "react";

interface MatchListProps {
  matchImageUrls: string[];
  matchPageUrls: string[];
  maxMatches?: number;
}

const MatchList: React.FC<MatchListProps> = ({
  matchImageUrls,
  matchPageUrls,
  maxMatches = 4
}) => {
  const formatDisplayUrl = (pageUrl: string): string => {
    let displayUrl: string;
    try {
      const url = new URL(pageUrl);
      displayUrl = url.hostname + (url.pathname !== "/" ? url.pathname : "");
    } catch (e) {
      // If URL parsing fails, use the truncated version
      displayUrl = pageUrl.length > 30
        ? `${pageUrl.substring(0, 15)}...${pageUrl.substring(pageUrl.length - 15)}`
        : pageUrl;
    }
    return displayUrl;
  };

  return (
    <div className="md:w-1/2 p-4">
      <div className="w-full">
        <h3 className="text-sm font-medium text-gray-700 mb-3">Matches:</h3>
        {(!matchImageUrls || matchImageUrls.length === 0) ? (
          <div className="bg-gray-50 border border-gray-200 rounded-md p-4 text-center text-gray-500 text-sm">
            No matches found
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-3 overflow-hidden">
            {matchImageUrls.slice(0, maxMatches).map((imageUrl, index) => {
              // Get corresponding page URL if available
              const pageUrl = matchPageUrls && index < matchPageUrls.length
                ? matchPageUrls[index]
                : imageUrl;

              const displayUrl = formatDisplayUrl(pageUrl);

              return (
                <div key={index} className="flex flex-row border border-gray-200 rounded shadow-sm overflow-hidden h-24">
                  <a
                    href={pageUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-gray-50 flex items-center justify-center p-2 w-24 h-24"
                  >
                    <img
                      src={imageUrl}
                      alt={`Match ${index + 1}`}
                      className="max-h-full max-w-full object-contain"
                      style={{ maxWidth: "128px" }}
                    />
                  </a>
                  <div className="flex-1 p-2 flex flex-col justify-center">
                    <a
                      href={pageUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline text-xs truncate"
                      title={pageUrl}
                    >
                      {displayUrl}
                    </a>
                  </div>
                </div>
              );
            })}
            {matchImageUrls.length > maxMatches && (
              <div className="text-xs text-gray-500 mt-1">
                +{matchImageUrls.length - maxMatches} more match
                {matchImageUrls.length - maxMatches > 1 ? "es" : ""}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default MatchList;
