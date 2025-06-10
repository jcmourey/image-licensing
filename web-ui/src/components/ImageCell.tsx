import React, {useState} from 'react';
import hideImage from "../api/hideImage.ts";
import ImagePopup from "./ImagePopup.tsx";

interface ImageCellProps {
  id: string;
  number: number;
  url: string;
  onChange: (id: string) => void;
}

const ImageCell: React.FC<ImageCellProps> = (
    {
        id,
        number,
        url,
        onChange,
    }) => {

    const [popupImage, setPopupImage] = useState<string | null>(null);

    return (
        <div className="flex items-center justify-center h-full relative">
            {popupImage && <ImagePopup imageUrl={popupImage} alt="Full size image"/>}

            <div className="flex flex-col items-center justify-center mr-2">
                {/* Image number */}
                <span className="text-xs text-gray-500 mb-1">{`#${number}`}</span>

                {/* Hide button */}
                <button
                    onClick={() => hideImage(id, onChange)}
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
            </div>

            <div className="flex flex-col items-center justify-center">
                <img
                    src={url}
                    alt={id}
                    className="w-40 h-40 object-cover rounded cursor-zoom-in"
                    onMouseEnter={() => setPopupImage(url)}
                    onMouseLeave={() => setPopupImage(null)}
                />
            </div>
        </div>
    );
};

export default ImageCell;

