import React from 'react';

// Remove the DeleteButton import temporarily to restore functionality
// import DeleteButton from './DeleteButton';

interface ImageCellProps {
  imageUrl: string | null;
  alt?: string;
  imageId: string;
  onShowPopup: (imageUrl: string | null) => void;
  onHidePopup: () => void;
  onHideImage: (id: string) => void;
}

const ImageCell: React.FC<ImageCellProps> = (
    {
      imageUrl,
      alt = "Image",
      imageId,
      onShowPopup,
      onHidePopup,
      onHideImage
    }) => {
  if (!imageUrl) {
    return <div className="text-gray-500">No image available</div>;
  }

  return (
    <div className="flex items-center justify-center h-full relative">
      {/* Hide button */}
      <button
          onClick={() => onHideImage(imageId)}
          className="mr-2 p-1 bg-gray-200 hover:bg-gray-300 rounded-full flex items-center justify-center h-8 w-8 transition-colors"
          title="Hide image"
        >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5 text-gray-600"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>

      <div className="flex flex-col items-center justify-center">
        <img
          src={imageUrl}
          alt={alt}
          className="w-40 h-25 object-cover rounded cursor-zoom-in"
          onMouseEnter={() => onShowPopup(imageUrl)}
          onMouseLeave={onHidePopup}
        />
      </div>
    </div>
  );
};

export default ImageCell;
