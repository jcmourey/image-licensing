import React from 'react';
import {type SaveStatus, type SetImageRows, useSaveController} from "../types/shared.ts";
import saveField from "../api/saveField.ts";
import EditableField from "./EditableField.tsx";

interface ReplacementImageCellProps {
  id: string;
  url: string | null;
  onRowsChange: SetImageRows;
}

const ReplacementImageCell: React.FC<ReplacementImageCellProps> = (
    {
        id,
        url,
        onRowsChange,
    }) => {

    const saveMethod = (value: string | null, setSaveStatus: (saveStatus: SaveStatus) => void) => {
        return saveField(id, "replacement_page_url", value, onRowsChange, setSaveStatus);
    };

    const {saveStatus, onSave} = useSaveController(saveMethod);

    return (
        <EditableField
            value={url}
            options={null}
            saveStatus={saveStatus}
            onEdit={() => {}}
            onSave={onSave}
            placeholder="Paste a URL..."
            emptyText="No replacement"
            isLink={true}
        />
    );
};


export default ReplacementImageCell;