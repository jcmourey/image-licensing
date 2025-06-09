import React from 'react';
import { type ImageRow as ImageRowType } from '../types/generated';
import type {SetImageRows} from '../types/shared';
import ImageCell from './ImageCell';
import MatchCell from './MatchCell';
import AttributionCell from './AttributionCell';
import CommentSection from './CommentSection';
import UsedInSection from './UsedInSection';
import ReplacementImageCell from "./ReplacementImageCell.tsx";

interface ImageRowProps {
    row: ImageRowType;
    onRowsChange: SetImageRows
}

const ImageRow: React.FC<ImageRowProps> = (
    {
        row,
        onRowsChange,
    }) => {

    return (
        <div className="grid grid-cols-6 min-h-[150px]">
            {/* Image */}
            <div className="p-3 border-r flex flex-col items-center justify-center h-full">
                <ImageCell
                    imageUrl={row.thumbnail_url}
                    imageId={row.id}
                    imageNumber={row.best_match_number}
                    onRowsChange={onRowsChange}
                />
            </div>

            {/* Best Match */}
            <div className="p-3 border-r flex flex-col items-center text-center">
                <MatchCell
                    imageId={row.id}
                    selectedMatchId={row.selected_match_id}
                    imageUrl={row.image_url}
                    pageUrl={row.best_page_url}
                    matchingType={row.matching_type}
                />
            </div>

            {/* Attribution */}
            <div className="p-3 border-r flex items-center justify-center h-full overflow-hidden">
                <AttributionCell
                    attribution={row.attribution}
                    licenseUrl={row.license_url}
                    licensed_by={row.licensed_by}
                />
            </div>

            {/* Used In */}
            <div className="p-3 border-r flex items-center justify-center h-full relative">
                <UsedInSection
                    id={row.id}
                    usedIn={row.used_in}
                    onRowsChange={onRowsChange}
                />
            </div>

            {/* Comment */}
            <div className="p-3 border-r flex items-center justify-center h-full relative">
                <CommentSection
                    id={row.id}
                    comment={row.comment}
                    onRowsChange={onRowsChange}
                />
            </div>

            {/* Replacement Image */}
            <div className="p-3 border-r flex items-center justify-center h-full relative">
                <ReplacementImageCell
                    id={row.id}
                    url={row.replacement_page_url}
                    onRowsChange={onRowsChange}
                />
            </div>
        </div>
    );
};

export default ImageRow;
