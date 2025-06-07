import React from "react";

interface ImageThumbnailProps {
  src: string;
  alt: string;
  isApproved: boolean;
}

const ImageThumbnail: React.FC<ImageThumbnailProps> = ({ src, alt, isApproved }) => {
  return (
    <div className="md:w-1/4 p-4 bg-gray-50">
      <div className="flex flex-col items-center">
        <img
          src={src}
          alt={alt}
          className="max-h-32 max-w-full object-contain rounded shadow-sm mb-3"
          style={{ maxWidth: "256px" }}
        />
        <div className="text-xs text-center px-2 py-1 bg-gray-100 rounded-md">
          {isApproved ? (
            <span className="text-green-600 font-medium">Approved</span>
          ) : (
            <span className="text-gray-500">Pending</span>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImageThumbnail;
