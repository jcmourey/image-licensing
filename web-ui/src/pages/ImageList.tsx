import { useEffect, useState } from "react"
import { type Image } from "../components/types"
import ImageCard from "../components/ImageCard"

const MAX_LICENSE_URLS = 5;
const MAX_MATCH_IMAGES = 4;

export default function ImageList() {
    const [images, setImages] = useState<Image[]>([]);

    useEffect(() => {
        fetch("/api/images")
            .then(res => res.json())
            .then(data => setImages(data));
    }, []);

    useEffect(() => {
        document.title = "Image Collection";
    }, []);

    return (
        <div className="max-w-7xl py-8 px-6 md:px-10 bg-gray-50 min-h-screen" style={{marginLeft: "50px"}}>
            <h1 className="text-3xl font-bold mb-10 text-gray-800 ml-2">Image Collection</h1>
            <div className="space-y-6">
                {images.map(img => (
                    <ImageCard
                        key={img.id}
                        image={img}
                        maxLicenses={MAX_LICENSE_URLS}
                        maxMatches={MAX_MATCH_IMAGES}
                    />
                ))}
            </div>
        </div>
    );
}