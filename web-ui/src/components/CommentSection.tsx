import React from 'react';
import EditableField from './EditableField';
import {useSaveController, type SaveStatus, type SetImageRows} from '../types/shared';
import saveField from '../api/saveField';

interface CommentSectionProps {
  id: string;
  comment: string | null;
  onRowsChange: SetImageRows;
}

const CommentSection: React.FC<CommentSectionProps> = (
    {
      id,
      comment,
      onRowsChange,
    }) => {

    const saveMethod = (value: string | null, setSaveStatus: (saveStatus: SaveStatus) => void) => {
        return saveField(id, "comment", value, onRowsChange, setSaveStatus);
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
