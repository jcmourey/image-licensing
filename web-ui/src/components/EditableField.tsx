import React, { useState, useEffect } from 'react';
import type { SaveStatus} from '../types/shared'
import {getDomain} from "../utils/string.ts";

interface EditableFieldProps {
  value: string | null;
  options: string[] | null;
  saveStatus: SaveStatus;
  onEdit: () => void;
  onSave: (value: string | null) => void;
  placeholder: string;
  emptyText: string;
  isLink: boolean
}

const EditableField: React.FC<EditableFieldProps> = (
    {
        value,
        options,
        saveStatus,
        onEdit,
        onSave,
        placeholder = "Enter text here...",
        emptyText = "No text",
        isLink,
    }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editValue, setEditValue] = useState(value || '');
    const isSaving = saveStatus.status === 'saving';
    const isError = saveStatus.status === 'error';
    const isSuccess = saveStatus.status === 'success';

    useEffect(() => {
        if (isSuccess) {
            setIsEditing(false);
            setEditValue(value || '');
        }
    }, [saveStatus.status, value]);

    if (isEditing) {
        return (
            <div className="flex flex-col">
                {/* Simple text input field */}
                <textarea
                    className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={editValue}
                    rows={3}
                    placeholder={placeholder}
                    onChange={(e) => setEditValue(e.target.value)}
                    autoFocus
                />

                  {/* Option buttons */}
                {options && (
                    <div className="flex flex-wrap gap-2 mt-2">
                        {options.map((option, index) => (
                            <button
                                key={index}
                                type="button"
                                onClick={() => {
                                    console.log(`[UsedInSection] Option clicked: "${option}" (${typeof option})`);
                                    onSave(option);
                                }}
                                className="px-3 py-1 text-sm bg-blue-50 text-blue-700 border border-blue-200 rounded-full
                         hover:bg-blue-100 hover:border-blue-300 transition-colors duration-150
                         shadow-sm"
                            >
                                {option}
                            </button>
                        ))}
                    </div>
                )}

                <div className="flex justify-end mt-2 w-full space-x-2">
                    <button
                        onClick={() => setIsEditing(false)}
                        className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                    >
                        Cancel
                    </button>

                    <button
                        onClick={() => onSave(null)}
                        className="px-3 py-1 bg-red-500 text-white rounded-md hover:bg-red-600"
                        disabled={isSaving}
                    >
                        {isSaving ? 'Clearing...' : 'Clear'}
                    </button>

                    <button
                        onClick={() => onSave(editValue)}
                        className="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                        disabled={isSaving}
                    >
                        {isSaving ? 'Saving...' : 'Save'}
                    </button>
                </div>
                {isError && (
                    <div className="text-red-500 text-sm mt-1">saveStatus.error || "unknown error"</div>
                )}
            </div>
        );
    }

    return (
        <div className="flex items-start w-full">
            <button
                onClick={() => {
                    setIsEditing(true);
                    setEditValue(value || '');
                    onEdit();
                }}
                className="mr-2 text-gray-400 hover:text-blue-600 focus:outline-none"
                title={`Edit ${editValue}`}
            >
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none"
                     stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"
                     className="feather feather-edit-2">
                    <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                </svg>
            </button>
            <div className="text-gray-700 flex-1">
                {value ? (
                    isLink ? (
                        <a
                          href={value}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 underline font-medium hover:text-blue-800 visited:text-purple-600 transition-colors"
                        >
                            {getDomain(value)}/...
                        </a>
                    ): (
                        value
                    )
                ) : (
                    <span className="italic text-gray-400">{emptyText}</span>
                )}
            </div>
            {saveStatus.status === 'success' && (
                <div className="text-green-500 text-xs ml-2">
                    Saved ✓
                </div>
            )}
        </div>
    );
};

export default EditableField;
