import React from 'react';

// Remove the DeleteButton import temporarily to restore functionality
// import DeleteButton from './DeleteButton';

interface ImageCellProps {
  imageUrl: string | null;
  alt?: string;
  imageId?: string;
  onShowPopup: (imageUrl: string | null) => void;
  onHidePopup: () => void;
  onImageDeleted?: () => void;
}

const ImageCell: React.FC<ImageCellProps> = ({ 
  imageUrl, 
  alt = "Image",
  // imageId,
  onShowPopup, 
  onHidePopup,
  // onImageDeleted
}) => {
  if (!imageUrl) {
    return <div className="text-gray-500">No image available</div>;
  }

  return (
    <div className="flex flex-col items-center justify-center h-full relative">
      {/* Temporarily remove the delete button to restore functionality */}
      {/* {imageId && onImageDeleted && (
        <div className="absolute top-0 left-0 z-10 w-full">
          <DeleteButton 
            imageId={imageId} 
            onDelete={onImageDeleted} 
          />
        </div>
      )} */}
      <img
        src={imageUrl}
        alt={alt}
        className="w-40 h-25 object-cover rounded cursor-zoom-in"
        onMouseEnter={() => onShowPopup(imageUrl)}
        onMouseLeave={onHidePopup}
      />
    </div>
  );
};

export default ImageCell;
