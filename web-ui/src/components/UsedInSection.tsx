import React from 'react';

interface SaveStatus {
  id: string;
  status: 'saving' | 'success' | 'error' | null;
}

interface UsedInSectionProps {
  id: string;
  usedIn: string | null;
  isEditing: boolean;
  usedInText: string;
  usedInOptions: string[];
  saveStatus: SaveStatus;
  onUsedInChange: (value: string) => void;
  onToggleEdit: (id: string, usedIn: string | null) => void;
  onSaveField: (id: string, fieldName: 'comment' | 'usedIn') => void;
  onSelectAndSave?: (id: string, value: string) => void; // New prop for direct select-and-save
}

const UsedInSection: React.FC<UsedInSectionProps> = ({
  id,
  usedIn,
  isEditing,
  usedInText,
  usedInOptions,
  saveStatus,
  onUsedInChange,
  onToggleEdit,
  onSaveField,
  onSelectAndSave
}) => {
  const isCurrentSaving = saveStatus.id === id && saveStatus.status === 'saving';
  const isCurrentSuccess = saveStatus.id === id && saveStatus.status === 'success';
  const isCurrentError = saveStatus.id === id && saveStatus.status === 'error';
  
  if (isEditing) {
    return (
      <div className="w-full max-w-full">
        {/* Simple text input field */}
        <input
          type="text"
          value={usedInText}
          onChange={(e) => onUsedInChange(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter usage information..."
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              onSaveField(id, 'usedIn');
            }
          }}
          autoFocus
        />
        
        {/* Option buttons */}
        <div className="flex flex-wrap gap-2 mt-2">
          {(usedInOptions || []).map((option, index) => (
            <button
              key={index}
              type="button"
              onClick={() => {
                console.log(`[UsedInSection] Option clicked: "${option}" (${typeof option})`);
                
                // If we have the direct save function, use it; otherwise just update the state
                if (onSelectAndSave) {
                  onSelectAndSave(id, option);
                } else {
                  // Just update the text state when we don't have a direct save function
                  onUsedInChange(option);
                }
              }}
              className="px-3 py-1 text-sm bg-blue-50 text-blue-700 border border-blue-200 rounded-full 
                         hover:bg-blue-100 hover:border-blue-300 transition-colors duration-150 
                         shadow-sm"
            >
              {option}
            </button>
          ))}
        </div>
        
        {/* Action buttons */}
        <div className="flex justify-end mt-2 w-full space-x-2">
          <button
            onClick={() => onToggleEdit(id, usedIn)}
            className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            type="button"
          >
            Cancel
          </button>
          <button
            onClick={() => onSaveField(id, 'usedIn')}
            className="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            disabled={isCurrentSaving}
            type="button"
          >
            {isCurrentSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
        
        <div className="text-gray-500 text-xs mt-1">Press Enter to save or click an option button</div>
        
        {isCurrentError && (
          <div className="text-red-500 text-sm mt-1">
            <span className="font-bold">Error saving usage information.</span>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex items-start w-full">
      <button
        onClick={() => onToggleEdit(id, usedIn)}
        className="mr-2 text-gray-400 hover:text-blue-600 focus:outline-none"
        title="Edit usage information"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" 
            className="feather feather-edit-2">
          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
        </svg>
      </button>
      <div className="text-gray-700 flex-1 flex items-center">
        <span className="mr-auto">
          {usedIn ? (
            usedIn
          ) : (
            <span className="italic text-gray-400">Not specified</span>
          )}
        </span>
        {isCurrentSuccess && (
          <span className="text-green-500 text-xs ml-2">
            Saved ✓
          </span>
        )}
      </div>
    </div>
  );
};

export default UsedInSection;
