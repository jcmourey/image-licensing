import React from "react";
import { useMemo } from "react";
import type { ImageRow  } from '../types/generated';

interface StatisticsProps {
  imageRows: ImageRow[];
}

const Statistics: React.FC<StatisticsProps> = ({ imageRows }) => {

    const summaryStats = useMemo(() => {
        // Count total images
        const total = imageRows.length;

        // Count attributions
        const attributions: Record<string, { license_url: string | null, count: number }> = {};

        // Count used_in
        const usedIn: Record<string, number> = {};

        // Count comments
        const comments: Record<string, number> = {};

        let replacementImages: number = 0;

        for (const row of imageRows) {
            // Attribution (License type or explanation string)
            const match = row.selected_match || row.best_match;
            if (match == null) { continue; }
            const attr = match.attribution || "Unknown";
            const lic = match.license_url || null;

            if (!(attr in attributions)) {
                attributions[attr] = {license_url: lic, count: 1};
            } else {
                attributions[attr].count += 1;
            }

            // Used_in
            const used = row.used_in;
            if (used != null) {
                usedIn[used] = (usedIn[used] || 0) + 1;
            }

            // Comment
            const comment = row.comment;
            if (comment != null && comment !== "") {
                comments[comment] = (comments[comment] || 0) + 1;
            }

            // Replacement Image
            if (row.replacement_page_url != null) {
                replacementImages += 1;
            }

        }

        return {total, attributions, usedIn, comments, replacementImages};
    }, [imageRows]);

    return (
        <div className="bg-gray-50 rounded p-3 mb-6 border">
            <div><strong>{summaryStats.total}</strong> images in collection</div>
            <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Left Column: Attributions */}
                <div>
                    <strong>Attributions:</strong>
                    <ul className="list-disc ml-6">
                        {Object.entries(summaryStats.attributions)
                            .sort(([a,], [b,]) => a.localeCompare(b))
                            .sort(([, a], [, b]) => b.count - a.count) // sort by count, descending
                            .map(([attrib, {license_url, count}]) => (
                                <li key={attrib}>
                                    {license_url ? (
                                        <a
                                            href={license_url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="text-blue-600 underline font-medium hover:text-blue-800 visited:text-purple-600 transition-colors"
                                        >
                                            {attrib}
                                        </a>
                                    ) : (
                                        attrib
                                    )}
                                    : <strong>{count}</strong>
                                </li>
                            ))}
                    </ul>
                </div>
                {/* Right Column: Used In and Comment */}

                <div>
                    <div className="mt-6">
                        <strong>Used In:</strong>
                        <ul className="list-disc ml-6">
                            {Object.entries(summaryStats.usedIn)
                                .sort(([a,], [b,]) => a.localeCompare(b))
                                .sort(([, a], [, b]) => b - a)
                                .map(([usedIn, count]) => (
                                <li key={usedIn}>
                                    {usedIn}: <strong>{count}</strong>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="mt-6">
                        <strong>Comments:</strong>
                        <ul className="list-disc ml-6">
                            {Object.entries(summaryStats.comments)
                                .sort(([, a], [, b]) => b - a)
                                .map(([comment, count]) => (
                                <li key={comment}>
                                    {comment}: <strong>{count}</strong>
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className="mt-6">
                        <strong>Replacement images: {summaryStats.replacementImages}</strong>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Statistics;