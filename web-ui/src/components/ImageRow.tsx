import React from 'react';
import { type ImageRow as ImageRowType } from './generated-types';
import ImageCell from './ImageCell';
import MatchCell from './MatchCell';
import AttributionCell from './AttributionCell';
import CommentSection from './CommentSection';
import UsedInSection from './UsedInSection';

interface SaveStatus {
  id: string;
  status: 'saving' | 'success' | 'error' | null;
  onImageDeleted?: (imageId: string) => void; // Add this prop
}

interface ImageRowProps {
    row: ImageRowType;
    editingFieldData: {
        id: string | null;
        fieldName: 'comment' | 'usedIn' | null;
    };
    commentText: string;
    usedInText: string;
    usedInOptions: string[];
    saveStatus: SaveStatus;
    onShowPopup: (imageUrl: string | null) => void;
    onHidePopup: () => void;
    onHideImage: (id: string) => void;
    onCommentChange: (value: string) => void;
    onUsedInChange: (value: string) => void;
    onToggleEdit: (id: string, value: string | null, fieldName: 'comment' | 'usedIn') => void;
    onSaveField: (id: string, fieldName: 'comment' | 'usedIn') => void;
}

const ImageRow: React.FC<ImageRowProps> = ({
    row,
    editingFieldData,
    commentText,
    usedInText,
    usedInOptions,
    saveStatus,
    onShowPopup,
    onHidePopup,
    onHideImage,
    onCommentChange,
    onUsedInChange,
    onToggleEdit,
    onSaveField
}) => {
    const isEditingComment = editingFieldData.id === row.id && editingFieldData.fieldName === 'comment';
    const isEditingUsedIn = editingFieldData.id === row.id && editingFieldData.fieldName === 'usedIn';

    return (
        <div className="grid grid-cols-5 min-h-[150px]">
            {/* Image */}
            <div className="p-3 border-r flex flex-col items-center justify-center h-full">
                <ImageCell
                    imageUrl={row.thumbnail_url}
                    imageId={row.id}
                    onShowPopup={onShowPopup}
                    onHidePopup={onHidePopup}
                    onHideImage={onHideImage}
                />
            </div>

            {/* Best Match */}
            <div className="p-3 border-r flex flex-col items-center text-center">
                <MatchCell
                    imageUrl={row.image_url}
                    pageUrl={row.best_page_url}
                    matchingType={row.matching_type}
                    // Temporarily remove the deletion props
                    // imageId={id}
                    onShowPopup={onShowPopup}
                    onHidePopup={onHidePopup}
                    // onImageDeleted={() => {
                    //   console.log(`Image ${id} deleted`);
                    //   // Notify parent component to refresh data
                    //   if (props.onImageDeleted) {
                    //     props.onImageDeleted(id);
                    //   }
                    // }}
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
                    isEditing={isEditingUsedIn}
                    usedInText={usedInText}
                    usedInOptions={usedInOptions}
                    saveStatus={saveStatus}
                    onUsedInChange={(value) => {
                        console.log(`UsedIn change in ImageRow: ${value}`);
                        onUsedInChange(value);
                    }}
                    onToggleEdit={(id, value) => onToggleEdit(id, value, 'usedIn')}
                    onSaveField={onSaveField}
                />
            </div>

            {/* Comment */}
            <div className="p-3 flex flex-col justify-center h-full w-full relative">
                <CommentSection
                    id={row.id}
                    comment={row.comment}
                    isEditing={isEditingComment}
                    commentText={commentText}
                    saveStatus={saveStatus}
                    onCommentChange={onCommentChange}
                    onToggleEdit={(id, value) => onToggleEdit(id, value, 'comment')}
                    onSaveField={(id, fieldName) => {
                        console.log(`Saving field in ImageRow: ${fieldName} for id: ${id}`);
                        onSaveField(id, fieldName);
                    }}
                />
            </div>
        </div>
    );
};

export default ImageRow;
