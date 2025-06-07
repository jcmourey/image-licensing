import React from 'react';

interface SaveStatus {
  id: string;
  status: 'saving' | 'success' | 'error' | null;
}

interface EditableFieldProps {
  id: string;
  value: string | null;
  fieldName: 'comment' | 'usedIn';
  isEditing: boolean;
  editValue: string;
  saveStatus: SaveStatus;
  onValueChange: (value: string) => void;
  onToggleEdit: (id: string, value: string | null) => void;
  onSave: (id: string, fieldName: 'comment' | 'usedIn') => void;
  placeholder?: string;
  emptyText?: string;
}

const EditableField: React.FC<EditableFieldProps> = ({
  id,
  value,
  fieldName,
  isEditing,
  editValue,
  saveStatus,
  onValueChange,
  onToggleEdit,
  onSave,
  placeholder = "Enter text here...",
  emptyText = "No text"
}) => {
  const isCurrentSaving = saveStatus.id === id && saveStatus.status === 'saving';
  const isCurrentSuccess = saveStatus.id === id && saveStatus.status === 'success';
  const isCurrentError = saveStatus.id === id && saveStatus.status === 'error';

  if (isEditing) {
    return (
      <>
        <textarea
          className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={editValue}
          onChange={(e) => onValueChange(e.target.value)}
          rows={3}
          placeholder={placeholder}
          autoFocus
        />
        <div className="flex justify-end mt-2 w-full space-x-2">
          <button
            onClick={() => onToggleEdit(id, value)}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
          <button
            onClick={() => onSave(id, fieldName)}
            className="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            disabled={isCurrentSaving}
          >
            {isCurrentSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
        {isCurrentError && (
          <div className="text-red-500 text-sm mt-1">Error saving {fieldName}</div>
        )}
      </>
    );
  }

  return (
    <div className="flex items-start w-full">
      <button
        onClick={() => onToggleEdit(id, value)}
        className="mr-2 text-gray-400 hover:text-blue-600 focus:outline-none"
        title={`Edit ${fieldName}`}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" 
            className="feather feather-edit-2">
          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
        </svg>
      </button>
      <div className="text-gray-700 flex-1">
        {value ? (
          value
        ) : (
          <span className="italic text-gray-400">{emptyText}</span>
        )}
      </div>
      {isCurrentSuccess && (
        <div className="text-green-500 text-xs ml-2">
          Saved ✓
        </div>
      )}
    </div>
  );
};

export default EditableField;
