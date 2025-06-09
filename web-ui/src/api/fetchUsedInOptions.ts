export const fetchUsedInOptions = async (setUsedInOptions: (options: string[]) => void) =>  {
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
