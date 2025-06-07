import React from 'react';
import EditableField from './EditableField';

interface SaveStatus {
  id: string;
  status: 'saving' | 'success' | 'error' | null;
}

interface CommentSectionProps {
  id: string;
  comment: string | null;
  isEditing: boolean;
  commentText: string;
  saveStatus: SaveStatus;
  onCommentChange: (value: string) => void;
  onToggleEdit: (id: string, comment: string | null) => void;
  onSaveField: (id: string, fieldName: 'comment' | 'usedIn') => void;
}

const CommentSection: React.FC<CommentSectionProps> = ({
  id,
  comment,
  isEditing,
  commentText,
  saveStatus,
  onCommentChange,
  onToggleEdit,
  onSaveField
}) => {
  return (
    <EditableField
      id={id}
      value={comment}
      fieldName="comment"
      isEditing={isEditing}
      editValue={commentText}
      saveStatus={saveStatus}
      onValueChange={onCommentChange}
      onToggleEdit={onToggleEdit}
      onSave={onSaveField}
      placeholder="Enter comment here..."
      emptyText="No comment"
    />
  );
};

export default CommentSection;
