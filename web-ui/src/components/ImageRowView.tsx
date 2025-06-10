import React from 'react';
import type { ImageRow } from '../types/generated';
import ImageCell from './ImageCell';
import MatchCell from './MatchCell';
import AttributionCell from './AttributionCell';
import CommentSection from './CommentSection';
import UsedInSection from './UsedInSection';
import ReplacementImageCell from "./ReplacementImageCell.tsx";

interface ImageRowProps {
    row: ImageRow;
    onChange: (id: string) => void;
}

const ImageRowView: React.FC<ImageRowProps> = (
    {
        row,
        onChange,
    }) => {

    const match = row.selected_match || row.best_match;

    return (
        <div className="grid grid-cols-6 min-h-[150px]">
            {/* Image */}
            <div className="p-3 border-r flex flex-col items-center justify-center h-full">
                <ImageCell
                    id={row.id}
                    number={row.number}
                    url={row.thumbnail_url}
                    onChange={onChange}
                />
            </div>

            {/* Best Match */}
            <div className="p-3 border-r flex flex-col items-center text-center">
                {match ? (
                    <MatchCell
                        imageId={row.id}
                        match={match}
                    />
                    ) : (
                    <span className="text-gray-500">No match found</span>
                )}
            </div>

            {/* Attribution */}
            <div className="p-3 border-r flex items-center justify-center h-full overflow-hidden">
                {match ? (
                    <AttributionCell
                        attribution={match.attribution}
                        licenseUrl={match.license_url}
                        licensed_by={match.licensed_by}
                />) : (
                    <span className="text-gray-500">No match found</span>
                )}
            </div>

            {/* Used In */}
            <div className="p-3 border-r flex items-center justify-center h-full relative">
                <UsedInSection
                    id={row.id}
                    usedIn={row.used_in}
                    onChange={onChange}
                />
            </div>

            {/* Comment */}
            <div className="p-3 border-r flex items-center justify-center h-full relative">
                <CommentSection
                    id={row.id}
                    comment={row.comment}
                    onChange={onChange}
                />
            </div>

            {/* Replacement Image */}
            <div className="p-3 border-r flex items-center justify-center h-full relative">
                <ReplacementImageCell
                    id={row.id}
                    url={row.replacement_page_url}
                    onChange={onChange}
                />
            </div>
        </div>
    );
};

export default ImageRowView;
