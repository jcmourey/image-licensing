import type {ImageRow} from "../types/generated.ts";

const fetchImageRows = (setImageRows: (rows: ImageRow[]) => void, setLoading: (loading: boolean) => void, setError: (error: string) => void) => {
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
}

export default fetchImageRows;