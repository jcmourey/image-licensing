import React from "react";

interface LicenseListProps {
  licenseUrls: string[];
  maxLicenses?: number;
}

const LicenseList: React.FC<LicenseListProps> = ({ licenseUrls, maxLicenses = 5 }) => {
  if (!licenseUrls || licenseUrls.length === 0) {
    return null;
  }

  const formatDisplayUrl = (licenseUrl: string): string => {
    let displayUrl = licenseUrl;
    try {
      const url = new URL(licenseUrl);
      displayUrl = url.hostname + (url.pathname !== "/" ? url.pathname : "");
      // For Creative Commons, make it more readable
      if (displayUrl.includes("creativecommons.org")) {
        const parts = url.pathname.split("/");
        const licenseType = parts.filter(p => p).join(" ");
        displayUrl = `CC ${licenseType}`.toUpperCase();
      }
    } catch (e) {
      // If URL parsing fails, use the truncated version
      displayUrl = licenseUrl.length > 45
        ? `${licenseUrl.substring(0, 25)}...${licenseUrl.substring(licenseUrl.length - 20)}`
        : licenseUrl;
    }
    return displayUrl;
  };

  return (
    <div className="md:w-1/4 p-4">
      <h3 className="text-sm font-medium text-gray-700 mb-2">
        License{licenseUrls.length > 1 ? "s" : ""}:
      </h3>
      <div className="space-y-2">
        {licenseUrls.slice(0, maxLicenses).map((licenseUrl, index) => {
          const displayUrl = formatDisplayUrl(licenseUrl);

          return (
            <div key={index} className="text-xs bg-gray-50 rounded-md p-2 border border-gray-100">
              <a
                href={licenseUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 hover:underline block truncate"
                title={licenseUrl}
              >
                {displayUrl}
              </a>
            </div>
          );
        })}
        {licenseUrls.length > maxLicenses && (
          <div className="text-xs text-gray-500 mt-1">
            +{licenseUrls.length - maxLicenses} more license
            {licenseUrls.length - maxLicenses > 1 ? "s" : ""}
          </div>
        )}
      </div>
    </div>
  );
};

export default LicenseList;
