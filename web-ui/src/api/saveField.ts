import type { SetImageRows, SaveStatus } from "../types/shared.ts";

const saveField = async (
    id: string,
    fieldName: string,
    fieldValue: string | null,
    onChange: SetImageRows,
    setSaveStatus: (saveStatus: SaveStatus) => void
) => {
    setSaveStatus({id, status: 'saving', error: null});

    try {
        // Encode the ID to handle slashes and special characters
        const encodedId = encodeURIComponent(id);
        const endpoint = `/api/image/${encodedId}/${fieldName}`
        const valueToSend = fieldValue === undefined || fieldValue === null ? '' : fieldValue;

        console.log(`Sending ${fieldName} update to: ${endpoint}, value: "${valueToSend}"`);
        const requestBody = JSON.stringify({[fieldName]: valueToSend});
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
            onChange(prev =>
                prev.map(row =>
                    row.id === id
                        ? {
                            ...row,
                            [fieldName]: valueToSend
                        }
                        : row
                )
            );


            // Set success status
            setSaveStatus({id, status: 'success', error: null});
            console.log(`[saveField] Successfully saved ${fieldName}`);

            // Clear status and exit edit mode after a delay
            setTimeout(() => {
                setSaveStatus({id: '', status: null, error: null});
            }, 1000);
        } else {
            console.error(`[saveField] Error saving ${fieldName}: ${response.statusText}`);
            setSaveStatus({id, status: 'error', error: `Response: ${response.statusText}`});

            // Clear error status after a longer delay
            setTimeout(() => {
                setSaveStatus({id: '', status: null, error: null});
            }, 5000);
        }
    } catch (err) {
        console.error(`[saveField] Exception:`, err);
        setSaveStatus({id, status: 'error', error: `Exception: ${err}`});

        setTimeout(() => {
            setSaveStatus({id: '', status: null, error: null});
        }, 5000);
    }
};

export default saveField;