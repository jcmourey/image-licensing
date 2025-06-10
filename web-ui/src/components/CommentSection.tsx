import React from 'react';
import EditableField from './EditableField';
import {useSaveController, type SaveStatus} from '../types/shared';
import saveField from '../api/saveField';

interface CommentSectionProps {
    id: string;
    comment: string | null;
    onChange: (id: string) => void;
}

const CommentSection: React.FC<CommentSectionProps> = (
    {
      id,
      comment,
      onChange,
    }) => {

    const saveMethod = (value: string | null, setSaveStatus: (saveStatus: SaveStatus) => void) => {
        return saveField(id, "comment", value, onChange, setSaveStatus);
    };

    const {saveStatus, onSave} = useSaveController(saveMethod);

    return (
        <EditableField
            value={comment}
            options={null}
            saveStatus={saveStatus}
            onEdit={() => {}}
            onSave={onSave}
            placeholder="Write a comment..."
            emptyText="No comment"
            isLink={false}
        />
    );
};


export default CommentSection;
