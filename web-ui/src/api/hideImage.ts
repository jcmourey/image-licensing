const hideImage = async (
    id: string,
    onChange: (id: string) => void
) => {
    try {
        const encodedId = encodeURIComponent(id);
        const endpoint = `/api/image/${encodedId}/hide`;
        const response = await fetch(endpoint, {
            method: 'POST',
        });

        if (!response.ok) {
            throw new Error(`Failed to hide image: ${response.statusText}`);
        }
        onChange(id); // update the visible rows in state

    } catch (err) {
        console.error(`Failed to hide image: ${id}`, err);
    }
};

export default hideImage;