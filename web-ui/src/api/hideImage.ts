import type { SetImageRows } from '../types/shared.ts'; // adjust the path accordingly

const hideImage = async (
    imageId: string,
    onChange: SetImageRows
) => {
    try {
        const encodedId = encodeURIComponent(imageId);
        const endpoint = `/api/image/${encodedId}/hide`;
        const response = await fetch(endpoint, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`Failed to hide image: ${response.statusText}`);
        }
        onChange(prev => prev.filter(row => row.id !== imageId)); // update the visible rows in state

    } catch (err) {
        console.error(`Failed to hide image: ${imageId}`, err);
    }
};

export default hideImage;