import React, { useState } from 'react';
import { hideImage } from '../api/imageApi';

interface DeleteButtonProps {
  imageId: string;
  onDelete: () => void; // Callback for after successful deletion
}

const DeleteButton: React.FC<DeleteButtonProps> = ({ imageId, onDelete }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleDelete = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering any parent click handlers
    
    if (window.confirm('Are you sure you want to hide this image? This action cannot be undone.')) {
      setIsDeleting(true);
      setError(null);
      
      try {
        await hideImage(imageId);
        onDelete();
      } catch (err) {
        setError('Failed to hide image. Please try again.');
        console.error('Error hiding image:', err);
      } finally {
        setIsDeleting(false);
      }
    }
  };
  
  return (
    <button
      onClick={handleDelete}
      disabled={isDeleting}
      className="bg-red-600 hover:bg-red-700 text-white rounded-full p-1.5 m-1
                 shadow-md transition-colors duration-150 border-2 border-white"
      title="Hide this image"
      aria-label="Hide image"
    >
      {isDeleting ? (
        <span className="flex items-center justify-center w-5 h-5">
          <svg className="animate-spin h-4 w-4 text-red-700" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </span>
      ) : (
        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" 
             stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"
             className="drop-shadow-sm">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      )}
      
      {error && (
        <div className="absolute bottom-full left-0 bg-red-100 text-red-700 text-xs p-1 rounded shadow-md whitespace-nowrap">
          {error}
        </div>
      )}
    </button>
  );
};

export default DeleteButton;
