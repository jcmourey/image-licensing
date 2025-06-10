import React, {useState} from 'react';
import { getDomain } from "../utils/string";
import {Link} from "react-router-dom";
import ImagePopup from "./ImagePopup.tsx";
import type {MatchRow} from "../types/generated.ts";

interface MatchCellProps {
    imageId: string | null;
    match: MatchRow;
}

const MatchCell: React.FC<MatchCellProps> = (
    {
        imageId,
        match,
    }) => {
    const [popupImage, setPopupImage] = useState<string | null>(null);

    if (!match.image_url || !match.page_url) {
        return <span>No match found</span>;
    }


    return (
        <div className="relative flex flex-col items-center text-center h-full justify-center">
            {popupImage && <ImagePopup imageUrl={popupImage} alt="Full size image"/>}

            {/* Rank */}
            <span className="absolute top-2 left-2 bg-gray-800 text-white text-xs font-bold px-2 py-1 rounded shadow z-10">
              {match.rank}
            </span>

            <div className="flex flex-col justify-center items-center flex-1">
                <img
                    src={match.image_url}
                    alt="Matched Image"
                    className="w-40 h-40 object-cover rounded cursor-zoom-in"
                    onMouseEnter={() => setPopupImage(match.image_url)}
                    onMouseLeave={() => setPopupImage(null)}
                />
            </div>

            <a
                href={match.page_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline mt-2"
            >
                {getDomain(match.page_url)}
            </a>

            {imageId && (
                <Link
                    to={`/image/${encodeURIComponent(imageId)}/matches`}
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
