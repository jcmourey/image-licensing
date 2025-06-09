import React, {useState} from 'react';
import { getDomain } from "../utils/string";
import {Link} from "react-router-dom";
import ImagePopup from "./ImagePopup.tsx";

interface MatchCellProps {
    imageId: string | null;
    selectedMatchId: number | null;
    imageUrl: string;
    pageUrl: string;
    matchingType: string;
}

const MatchCell: React.FC<MatchCellProps> = (
    {
        imageId,
        selectedMatchId,
        imageUrl,
        pageUrl,
        matchingType,
    }) => {
    const [popupImage, setPopupImage] = useState<string | null>(null);

    if (!imageUrl || !pageUrl) {
        return <span>No match found</span>;
    }

    return (
        <div className="flex flex-col items-center text-center">
            {popupImage && <ImagePopup imageUrl={popupImage} alt="Full size image"/>}

            <div className="flex items-center gap-1 mb-1">
                    <span className="text-xs font-medium text-gray-500 inline-block px-2 py-1 bg-gray-100 rounded">
                        {matchingType}
                    </span>{pageUrl === imageUrl && (
                <span className="text-xs font-medium text-yellow-700 inline-block px-2 py-1 bg-yellow-100 rounded">
                            No webpage
                    </span>
            )}
            </div>
            <img
                src={imageUrl}
                alt="Matched Image"
                className="w-40 h-25 object-cover rounded cursor-zoom-in"
                onMouseEnter={() => setPopupImage(imageUrl)}
                onMouseLeave={() => setPopupImage(null)}
            />

            <a
                href={pageUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline mt-2"
            >
                {getDomain(pageUrl)}
            </a>

            {imageId && selectedMatchId && (
                <Link
                    to={`/image/${encodeURIComponent(imageId)}/${selectedMatchId}/matches`}
                    className="text-sm text-blue-500 mt-1 italic hover:text-blue-700"
                    target="_blank" // <-- Opens new browser tab/window
                    rel="noopener noreferrer"
                >
                    more ›
                </Link>
            )}

        </div>
    );
};

export default MatchCell;
