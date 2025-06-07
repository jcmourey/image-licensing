import { useState, useEffect } from 'react';
import { type ImageRow as ImageRowType } from '../components/generated-types';
import { config } from '../config';
import ImagePopup from '../components/ImagePopup';
import ImageRow from '../components/ImageRow';

// Explicitly enable HMR for this component
if (import.meta.hot) {
  import.meta.hot.accept();
}

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

// Loading state component
const LoadingState = () => (
  <div className="flex justify-center items-center h-64">
    <div className="text-gray-600">Loading image rows...</div>
  </div>
);

// Error state component
const ErrorState = ({ message }: { message: string }) => (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
    <span className="block sm:inline">{message}</span>
  </div>
);

// Empty state component
const EmptyState = () => (
  <div className="bg-white shadow-md rounded-lg p-6 text-center text-gray-500">
    No image rows found
  </div>
);

// Table header component
const TableHeader = () => (
  <div className="grid grid-cols-5 bg-gray-100 font-medium">
    <div className="p-3 border-b border-r text-center">Image</div>
    <div className="p-3 border-b border-r text-center">Selected Match</div>
    <div className="p-3 border-b border-r text-center">License</div>
    <div className="p-3 border-b border-r text-center">Used In</div>
    <div className="p-3 border-b border-r text-center">Comment</div>
  </div>
);

export const ImageRows = () => {
  const [imageRows, setImageRows] = useState<ImageRowType[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [popupImage, setPopupImage] = useState<string | null>(null);
  const [editingFieldData, setEditingFieldData] = useState<{
    id: string | null;
    fieldName: 'comment' | 'usedIn' | null;
  }>({ id: null, fieldName: null });
  const [commentText, setCommentText] = useState<string>("");
  const [usedInText, setUsedInText] = useState<string>("");
  const [usedInOptions, setUsedInOptions] = useState<string[]>([]);
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
  
  /* Temporarily comment out the handleImageDeleted function to restore functionality
  const handleImageDeleted = (imageId: string) => {
    console.log(`Image deleted: ${imageId}`);
    // Update the local state to remove the deleted image
    setImageRows(prev => prev.filter(row => row.id !== imageId));
    // Alternatively, refetch all images
    // fetchImageRows();
  };
  */
  
  // Function to fetch used_in options
  const fetchUsedInOptions = async () => {
    console.log("Fetching used_in options...");
    try {
      const response = await fetch("/api/used_in_options");
      console.log("Used in options response status:", response.status);
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const data = await response.json();
      console.log("Used in options received:", data);
      
      // Make sure we have an array, and include some default options if empty
      if (!data || data.length === 0) {
        setUsedInOptions(["Website", "Blog", "Documentation", "Marketing", "Not Used"]);
      } else {
        setUsedInOptions(data);
      }
    } catch (err) {
      console.error("Failed to fetch used_in options:", err);
      // Set some default options rather than an empty array
      setUsedInOptions(["Website", "Blog", "Documentation", "Marketing", "Not Used"]);
    }
  };
  
  // Direct selection and save function for option buttons
  const selectAndSave = async (id: string, value: string) => {
    console.log(`[selectAndSave] Direct save with value: "${value}" (${typeof value})`);
    
    setSaveStatus({id, status: 'saving'});
    
    try {
      // Encode the ID to handle slashes and special characters
      const encodedId = encodeURIComponent(id);
      const endpoint = `/api/image/${encodedId}/used_in`;
      
      // Log what we're about to send
      console.log(`[selectAndSave] Sending to API: ${endpoint}`);
      console.log(`[selectAndSave] Value: "${value}"`);
      
      // Create the request body directly with the provided value
      const requestBody = JSON.stringify({ used_in: value });
      console.log(`[selectAndSave] Request body: ${requestBody}`);
      
      const response = await fetch(endpoint, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: requestBody,
      });
      
      // Log the response information
      console.log(`[selectAndSave] Response status: ${response.status} ${response.statusText}`);
      try {
        const responseText = await response.clone().text();
        console.log(`[selectAndSave] Response body: ${responseText}`);
      } catch (err) {
        console.log(`[selectAndSave] Could not read response body: ${err}`);
      }
      
      if (response.ok) {
        // Update local state to match what we sent
        setUsedInText(value);
        
        // Update the row data
        setImageRows(prev => 
          prev.map(row => 
            row.id === id ? { ...row, used_in: value } : row
          )
        );
        
        // If we updated a used_in value, refresh the used_in options to include new values
        setTimeout(async () => {
          await fetchUsedInOptions();
        }, 500);
        
        // Set success status
        setSaveStatus({id, status: 'success'});
        console.log(`[selectAndSave] Successfully saved: "${value}"`);
        
        // Close edit mode after successful save
        setEditingFieldData(prev => ({
          ...prev,
          id: null,
          fieldName: null
        }));
        
        // Clear status after a delay
        setTimeout(() => {
          setSaveStatus({id: '', status: null});
        }, 2000);
      } else {
        console.error(`[selectAndSave] Error saving: ${response.statusText}`);
        setSaveStatus({id, status: 'error'});
        
        // Clear error status after longer delay
        setTimeout(() => {
          setSaveStatus({id: '', status: null});
        }, 5000);
      }
    } catch (err) {
      console.error(`[selectAndSave] Exception:`, err);
      
      // Force console display by using console.warn as well
      console.warn(`[selectAndSave] Error details:`, {
        error: err,
        endpoint,
        requestBody: { used_in: value },
        id
      });
      
      // Show error status
      setSaveStatus({id, status: 'error'});
      setTimeout(() => {
        setSaveStatus({id: '', status: null});
      }, 5000); // Give more time to see the error message
    }
  };
  
  // Save field to backend
  const saveField = async (id: string, fieldName: 'comment' | 'usedIn') => {
    setSaveStatus({id, status: 'saving'});
    
    // Capture the current values at the moment of saving to ensure we use the most recent values
    const currentCommentText = commentText;
    const currentUsedInText = usedInText;
    
    console.log(`[saveField] Starting save for ${fieldName} on id: ${id}`);
    console.log(`[saveField] Current commentText: "${currentCommentText}"`);
    console.log(`[saveField] Current usedInText: "${currentUsedInText}"`);
    
    try {
      // Encode the ID to handle slashes and special characters
      const encodedId = encodeURIComponent(id);
      
      const endpoint = fieldName === 'comment' 
        ? `/api/image/${encodedId}/comment`
        : `/api/image/${encodedId}/used_in`;
      
      // Get the current value from captured state to avoid race conditions
      const fieldValue = fieldName === 'comment' ? currentCommentText : currentUsedInText;
      const fieldKey = fieldName === 'comment' ? 'comment' : 'used_in';
      
      console.log(`[saveField] Using value: "${fieldValue}" (${typeof fieldValue})`);
      
      // Log the actual value being sent to the API
      console.log(`Sending ${fieldName} update to: ${endpoint}, value: "${fieldValue}"`);
      console.log(`Value type: ${typeof fieldValue}`);
      
      // Use empty string if value is undefined or null (API might expect this)
      const valueToSend = fieldValue === undefined || fieldValue === null ? '' : fieldValue;
      
      // Log detailed information about the request
      console.log(`[API REQUEST] ${endpoint}`);
      console.log(`[API REQUEST] Field name: ${fieldName}`);
      console.log(`[API REQUEST] Field key: ${fieldKey}`);
      console.log(`[API REQUEST] Original value: "${fieldValue}" (${typeof fieldValue})`);
      console.log(`[API REQUEST] Value to send: "${valueToSend}" (${typeof valueToSend})`);
      console.log(`[API REQUEST] Request body: ${JSON.stringify({ [fieldKey]: valueToSend })}`);
      
      // Create the request body and log it once more to be absolutely sure what's being sent
      const requestBody = JSON.stringify({ [fieldKey]: valueToSend });
      console.log(`[API REQUEST] Final JSON body: ${requestBody}`);
      
      const response = await fetch(endpoint, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: requestBody,
      });
      
      // Log the response information
      console.log(`[API RESPONSE] Status: ${response.status} ${response.statusText}`);
      try {
        const responseText = await response.clone().text();
        console.log(`[API RESPONSE] Body: ${responseText}`);
      } catch (err) {
        console.log(`[API RESPONSE] Could not read response body: ${err}`);
      }
  
      if (response.ok) {
        // Update the imageRows state with the new value
        setImageRows(prev => 
          prev.map(row => 
            row.id === id 
              ? { 
                  ...row, 
                  [fieldName === 'comment' ? 'comment' : 'used_in']: fieldName === 'comment' ? currentCommentText : currentUsedInText 
                } 
              : row
          )
        );
        
        // If we updated a used_in value, refresh the used_in options to include new values
        if (fieldName === 'usedIn') {
          setTimeout(async () => {
            await fetchUsedInOptions();
          }, 500);
        }
        
        // Set success status
        setSaveStatus({id, status: 'success'});
        console.log(`[saveField] Successfully saved ${fieldName}`);
        
        // Clear status and exit edit mode after a delay
        setTimeout(() => {
          setEditingFieldData({ id: null, fieldName: null });
          setSaveStatus({id: '', status: null});
        }, 2000);
      } else {
        console.error(`[saveField] Error saving ${fieldName}: ${response.statusText}`);
        setSaveStatus({id, status: 'error'});
        
        // Clear error status after longer delay
        setTimeout(() => {
          setSaveStatus({id: '', status: null});
        }, 5000);
      }
          } catch (err) {
      console.error(`[saveField] Exception:`, err);
      setSaveStatus({id, status: 'error'});
      
      setTimeout(() => {
        setSaveStatus({id: '', status: null});
      }, 5000);
          }
        };
        
  // Toggle edit mode for a field
  const toggleEditField = (id: string, currentValue: string | null, fieldName: 'comment' | 'usedIn') => {
    console.log("Toggling edit for field:", fieldName, "id:", id, "current value:", currentValue);
    const isCurrentlyEditing = editingFieldData.id === id && editingFieldData.fieldName === fieldName;
    
    if (isCurrentlyEditing) {
      // Exit edit mode
      console.log("Exiting edit mode");
      setEditingFieldData({ id: null, fieldName: null });
    } else {
      // Enter edit mode
      console.log("Entering edit mode");
      setEditingFieldData({ id, fieldName });
      
      // Find the current row to get the most up-to-date value
      const currentRow = imageRows.find(row => row.id === id);
      
      if (fieldName === 'comment') {
        // Set comment text from the row data or from the passed value
        const newValue = currentRow?.comment || currentValue || "";
        console.log(`Setting commentText to: "${newValue}"`);
        setCommentText(newValue);
      } else {
        // Set used_in text from the row data or from the passed value
        const newValue = currentRow?.used_in || currentValue || "";
        console.log(`Setting usedInText to: "${newValue}"`);
        setUsedInText(newValue);
      }
    }
  };

  // Fetch image rows from the API
  useEffect(() => {
    console.log("Fetching image rows...");
    fetch("/api/image_rows")
      .then(response => {
        console.log("Image rows response status:", response.status);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log("Image rows data received:", data.length, "rows");
        setImageRows(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch image rows:", err);
        setError("Failed to load image rows. Please try again later.");
        setLoading(false);
      });
  }, []);

  // Fetch used_in options from the API on component mount
  useEffect(() => {
    fetchUsedInOptions();
  }, []);
  
  useEffect(() => {
    document.title = "Image Collection";
    console.log("ImageRows component mounted/updated:", new Date().toISOString());
  }, []);

  // Render content based on state
  const renderContent = () => {
    console.log("Rendering content with state:", { 
      loading, 
      error, 
      imageRowsCount: imageRows?.length || 0,
      editingFieldData,
      usedInOptions: usedInOptions?.length || 0
    });
    
    if (loading) {
      return <LoadingState />;
    }
    
    if (error) {
      return <ErrorState message={error} />;
    }
    
    if (!imageRows || imageRows.length === 0) {
      return <EmptyState />;
    }
    
    return (
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <TableHeader />
        <div className="divide-y">
          {imageRows.map((row) => (
            <ImageRow
              key={row.id}
              row={row}
              editingFieldData={editingFieldData}
              commentText={commentText}
              usedInText={usedInText}
              usedInOptions={usedInOptions}
              saveStatus={saveStatus}
              onShowPopup={showPopup}
              onHidePopup={hidePopup}
              onCommentChange={setCommentText}
              onUsedInChange={setUsedInText}
              onToggleEdit={toggleEditField}
              onSaveField={saveField}
              onSelectAndSave={selectAndSave}
              // Temporarily remove onImageDeleted prop to fix rendering
              // onImageDeleted={handleImageDeleted}
            />
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-7xl py-8 px-6 md:px-10 bg-gray-50 min-h-screen" style={{marginLeft: "50px"}}>
      {popupImage && <ImagePopup imageUrl={popupImage} alt="Full size image" />}

      <h1 className="text-3xl font-bold mb-10 text-gray-800 ml-2">Image Rows</h1>

      {/* Conditionally render the Tailwind CSS Test Component based on flag */}
      {config.showTailwindTest && <TailwindTestComponent />}

      {renderContent()}
    </div>
  );
};

export default ImageRows;
