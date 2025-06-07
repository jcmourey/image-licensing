import { useState, useEffect } from 'react';
import { type ImageRow } from '../components/generated-types';
import { config } from '../config';
import ImagePopup from '../components/ImagePopup';
import { getDomain } from "../utils/string.ts";

// Explicitly enable HMR for this component
if (import.meta.hot) {
  import.meta.hot.accept();
}

export const ImageRows = () => {
  const [imageRows, setImageRows] = useState<ImageRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [popupImage, setPopupImage] = useState<string | null>(null);
  const [editingCommentId, setEditingCommentId] = useState<string | null>(null);
  const [commentText, setCommentText] = useState<string>("");
  const [saveStatus, setSaveStatus] = useState<{id: string, status: 'saving' | 'success' | 'error' | null}>({id: '', status: null});

  // Show popup with the full image
  const showPopup = (imageUrl: string | null) => {
    if (imageUrl) {
      console.log("Showing popup for:", imageUrl);
      setPopupImage(imageUrl);
    }
  };

  // Hide the popup
  const hidePopup = () => {
    console.log("Hiding popup");
    setPopupImage(null);
  };
  
  // Save updated comment to backend
  const saveComment = async (id: string) => {
    setSaveStatus({id, status: 'saving'});
    try {
      // Encode the ID to handle slashes and special characters
      const encodedId = encodeURIComponent(id);
      console.log(`Sending comment update to: /api/image/${encodedId}/comment`);
      const response = await fetch(`/api/image/${encodedId}/comment`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ comment: commentText }),
      });
  
      if (!response.ok) {
        console.error(`Failed to update comment: ${response.status} ${response.statusText}`);
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
  
      // Update the local state
      setImageRows(prevRows => 
        prevRows.map(row => 
          row.id === id ? {...row, comment: commentText} : row
        )
      );
      
      setSaveStatus({id, status: 'success'});
      setTimeout(() => {
        setSaveStatus({id: '', status: null});
        setEditingCommentId(null);
      }, 2000);
    } catch (err) {
      console.error("Failed to update comment:", err);
      setSaveStatus({id, status: 'error'});
      setTimeout(() => {
        setSaveStatus({id: '', status: null});
      }, 3000);
    }
  };
  
  // Toggle edit mode for a comment
  const toggleEditComment = (id: string, currentComment: string | null) => {
    if (editingCommentId === id) {
      // Exit edit mode
      setEditingCommentId(null);
      setCommentText("");
    } else {
      // Enter edit mode
      setEditingCommentId(id);
      setCommentText(currentComment || "");
    }
  };
  
  // Save updated comment to backend

  useEffect(() => {
    // Fetch image rows from the API
    fetch("/api/image_rows")
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        setImageRows(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch image rows:", err);
        setError("Failed to load image rows. Please try again later.");
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    document.title = "Image Collection";
    console.log("ImageRows component mounted/updated:", new Date().toISOString());
  }, []);

  // Component to test Tailwind CSS
  const TailwindTestComponent = () => (
    <div className="mb-6 border-4 border-red-500 p-4">
      <h2 className="text-lg font-semibold mb-2 text-red-600">Tailwind CSS Test (Should have red border)</h2>
      <div className="p-4 bg-gradient-to-r from-red-500 via-yellow-500 to-green-500 text-white rounded-lg shadow-xl">
        <p className="font-bold text-xl">This element uses Tailwind classes</p>
        <p className="text-sm mt-1">If you can see this colorful gradient background, Tailwind is working!</p>
        <div className="flex space-x-4 mt-4">
          <button className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors">
            Blue Button
          </button>
          <button className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 transition-colors">
            Green Button
          </button>
          <button className="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 transition-colors">
            Purple Button
          </button>
        </div>
      </div>
      <div className="mt-4 grid grid-cols-3 gap-4">
        <div className="bg-pink-200 p-3 rounded-lg text-center">Pink</div>
        <div className="bg-teal-200 p-3 rounded-lg text-center">Teal</div>
        <div className="bg-orange-200 p-3 rounded-lg text-center">Orange</div>
      </div>
    </div>
  );

  return (
    <div className="max-w-7xl py-8 px-6 md:px-10 bg-gray-50 min-h-screen" style={{marginLeft: "50px"}}>
      {popupImage && <ImagePopup imageUrl={popupImage} alt="Full size image" />}

      <h1 className="text-3xl font-bold mb-10 text-gray-800 ml-2">Image Rows</h1>

      {/* Conditionally render the Tailwind CSS Test Component based on flag */}
      {config.showTailwindTest && <TailwindTestComponent />}

      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="text-gray-600">Loading image rows...</div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <span className="block sm:inline">{error}</span>
        </div>
      ) : imageRows.length === 0 ? (
        <div className="bg-white shadow-md rounded-lg p-6 text-center text-gray-500">
          No image rows found
        </div>
      ) : (
        <div className="bg-white shadow-md rounded-lg overflow-hidden">
          {/* Table Header */}
          <div className="grid grid-cols-5 bg-gray-100 font-medium">
            <div className="p-3 border-b border-r text-center">Image</div>
            <div className="p-3 border-b border-r text-center">Selected Match</div>
            <div className="p-3 border-b border-r text-center">License</div>
            <div className="p-3 border-b border-r text-center">Used In</div>
            <div className="p-3 border-b border-r text-center">Comment</div>
          </div>

          {/* Table Body */}
          <div className="divide-y">
            {imageRows.map((row) => (
              <div key={row.id} className="grid grid-cols-5 min-h-[150px]">
                {/* Image */}
                <div className="p-3 border-r flex flex-col items-center justify-center h-full">
                  <img
                    src={row.thumbnail_url}
                    alt="Image"
                    className="w-40 h-25 object-cover rounded cursor-zoom-in"
                    onMouseEnter={() => showPopup(row.thumbnail_url)}
                    onMouseLeave={hidePopup}
                  />
                </div>

                {/* Best Match with link to page URL */}
                <div className="p-3 border-r flex flex-col items-center text-center">
                  {row.image_url && row.best_page_url ? (
                      <>
                        {row.matching_type && (
                          <span className="text-xs font-medium text-gray-500 mb-1 inline-block px-2 py-1 bg-gray-100 rounded">
                            {row.matching_type}
                          </span>
                        )}
                        <img
                          src={row.image_url}
                          alt="Image"
                          className="w-40 h-25 object-cover rounded cursor-zoom-in"
                          onMouseEnter={() => showPopup(row.image_url)}
                          onMouseLeave={hidePopup}
                        />
                        <a href={row.best_page_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline mt-2">
                          {getDomain(row.best_page_url)}
                        </a>
                      </>
                    ) : (
                      <span>No match found</span>
                    )
                  }
                </div>
                
                {/* Attribution with license link */}
                <div className="p-3 border-r flex items-center justify-center h-full">
                  {row.license_url && row.attribution ? (
                    <a href={row.license_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                      {row.attribution}
                    </a>
                  ) : (
                    <span>{row.attribution || "None found"}</span>
                  )}
                </div>
                
                {/* Used In */}
                <div className="p-3 border-r flex items-center justify-center h-full">
                  {row.used_in || "Not specified"}
                </div>
                
                {/* Comment */}
                <div className="p-3 flex flex-col justify-center h-full w-full relative">
                  {editingCommentId === row.id ? (
                    <>
                      <textarea
                        className="w-full p-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        rows={3}
                        placeholder="Enter comment here..."
                        autoFocus
                      />
                      <div className="flex justify-end mt-2 w-full space-x-2">
                        <button
                          onClick={() => toggleEditComment(row.id, row.comment)}
                          className="px-3 py-1 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
                        >
                          Cancel
                        </button>
                        <button
                          onClick={() => saveComment(row.id)}
                          className="px-3 py-1 bg-blue-500 text-white rounded-md hover:bg-blue-600"
                          disabled={saveStatus.id === row.id && saveStatus.status === 'saving'}
                        >
                          {saveStatus.id === row.id && saveStatus.status === 'saving' 
                            ? 'Saving...' 
                            : 'Save'}
                        </button>
                      </div>
                      {saveStatus.id === row.id && saveStatus.status === 'error' && (
                        <div className="text-red-500 text-sm mt-1">Error saving comment</div>
                      )}
                    </>
                  ) : (
                    <div className="flex items-start w-full">
                      <button
                        onClick={() => toggleEditComment(row.id, row.comment)}
                        className="mr-2 text-gray-400 hover:text-blue-600 focus:outline-none"
                        title="Edit comment"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" 
                            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" 
                            className="feather feather-edit-2">
                          <path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"></path>
                        </svg>
                      </button>
                      <div className="text-gray-700 flex-1">
                        {row.comment || "No comment"}
                      </div>
                      {saveStatus.id === row.id && saveStatus.status === 'success' && (
                        <div className="absolute right-2 top-2 text-green-500 text-xs">
                          Saved ✓
                        </div>
                      )}
                    </div>
                  )}
                </div>

              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageRows;
