import React from "react";
import { type Image } from "./types";
import HeaderCard from "./HeaderCard";
import ImageThumbnail from "./ImageThumbnail";
import LicenseList from "./LicenseList";
import MatchList from "./MatchList";

interface ImageCardProps {
  image: Image;
  maxLicenses?: number;
  maxMatches?: number;
}

const ImageCard: React.FC<ImageCardProps> = ({
  image,
  maxLicenses = 5,
  maxMatches = 4
}) => {
  return (
    <div
      className="bg-white rounded-lg shadow-md transition-all duration-300 hover:shadow-lg overflow-hidden"
      style={{
        borderLeft: image.is_approved ? '4px solid #10B981' : '1px solid #e5e7eb',
        borderTop: '20px solid #e5e7eb',
        borderRight: '1px solid #e5e7eb',
        borderBottom: '10px solid #ffffff',
      }}
    >
      <HeaderCard
        name={image.name}
        matchCount={image.match_count}
        licenseCount={image.license_urls.length}
      />

      <div className="flex flex-col">
        {/* Top row: ImageThumbnail and LicenseList horizontally */}
        <div className="flex flex-row items-start">
          <ImageThumbnail
            src={image.thumbnail_url}
            alt={image.name}
            isApproved={image.is_approved}
          />

          <LicenseList
            licenseUrls={image.license_urls}
            maxLicenses={maxLicenses}
          />
        </div>

        {/* Bottom row: MatchList */}
        <div className="w-full">
          <MatchList
            matchImageUrls={image.match_image_urls}
            matchPageUrls={image.match_page_urls}
            maxMatches={maxMatches}
          />
        </div>
      </div>

    </div>
  );
};

export default ImageCard;
