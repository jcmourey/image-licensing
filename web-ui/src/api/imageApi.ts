/**
 * API functions for image data
 */

/**
 * Hide an image by setting its show field to false
 * 
 * @param imageId - The ID of the image to hide
 * @returns Promise with the result of the operation
 */
export const hideImage = async (imageId: string): Promise<{ success: boolean }> => {
  try {
    const response = await fetch(`/api/image/${encodeURIComponent(imageId)}/hide`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error(`Failed to hide image: ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error hiding image:', error);
    throw error;
  }
};
