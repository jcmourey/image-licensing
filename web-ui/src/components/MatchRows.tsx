import React, {useEffect, useState} from "react";
import type {MatchRow} from "../types/generated.ts";
import {useParams} from "react-router-dom";
import AttributionCell from "./AttributionCell.tsx";
import MatchCell from "./MatchCell.tsx";

const MatchRows: React.FC = () => {
    const {imageId, selectedMatchId} = useParams();
    const [matchRows, setMatchRows] = useState<MatchRow[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedMatchIdNumber, setSelectedMatchIdNumber] = useState(selectedMatchId ? parseInt(selectedMatchId, 10) : null);

    const fetchMatchRows = () => {
        fetch(`/api/image/${imageId}/match_rows`)
            .then(res => res.json())
            .then(data => {
                setMatchRows(data);
                setLoading(false);
            });
    }

    useEffect(() => {
        console.log("MatchRows imageId", imageId);
        setLoading(true);
        fetchMatchRows()
    }, [imageId]);

    useEffect(() => {
        document.title = "Matches";
    }, []);

    const postSelectedMatchId = async (matchId: number) => {
        try {
            if (imageId === undefined) return;
            const encodedId = encodeURIComponent(imageId);
            const endpoint = `/api/image/${encodedId}/selected_match_id`;
            const requestBody = JSON.stringify({["selected_match_id"]: matchId});
            const response = await fetch(endpoint, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: requestBody
            });

            if (!response.ok) {
                throw new Error(`Request failed: ${response.statusText}`);
            }
            setSelectedMatchIdNumber(matchId);
        } catch (err) {
            console.error(`Failed to post selected_match_id ${matchId} for image: ${imageId}`, err);
        }
    };


    if (loading) return <div className="p-6">Loading matches...</div>;
    else if (matchRows.length === 0) return <div className="p-6">No matches found...</div>;


    return (
        <div className="max-w-5xl mx-auto py-12 px-4 bg-white shadow-md rounded-lg mt-10">
            <h1 className="text-3xl font-bold mb-10 text-gray-800 ml-2">{matchRows.length} matches for image</h1>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {matchRows.map(match => (
                    <div className={`
                        relative border-2 p-4 rounded
                        ${match.id === selectedMatchIdNumber ? 'border-green-500' : 'border-gray-300'}
                        hover:border-blue-400 hover:bg-blue-50 transition-colors
                    `}>
                        {match.id === selectedMatchIdNumber && (
                            <div className="absolute top-2 right-2 bg-white rounded-full p-1 shadow">
                                {/* SVG Checkmark */}
                                <svg className="w-6 h-6 text-green-500" fill="none" stroke="currentColor"
                                     strokeWidth="3" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
                                </svg>
                            </div>
                        )}

                        <div className="flex items-center gap-1 mb-1">
                            <span className="text-xs font-medium text-gray-500 inline-block px-2 py-1 bg-gray-100 rounded">
                                {match.matching_type}
                            </span>{match.page_url === match.image_url && (
                                <span className="text-xs font-medium text-yellow-700 inline-block px-2 py-1 bg-yellow-100 rounded">
                                    No webpage
                                </span>
                            )}
                        </div>
                        <div
                            key={match.id}
                            onClick={() => postSelectedMatchId(match.id)}
                            className={`
                                
                            `}
                            style={{cursor: "pointer"}}
                        >
                            <MatchCell
                                imageId={null}
                                match={match}
                            />
                            <AttributionCell
                                attribution={match.attribution}
                                licenseUrl={match.license_url}
                                licensed_by={match.licensed_by}
                            />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default MatchRows;
