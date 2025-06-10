import React, {useState} from 'react';
import EditableField from './EditableField';
import {useSaveController, type SaveStatus} from '../types/shared';
import saveField from '../api/saveField';
import {fetchUsedInOptions} from '../api/fetchUsedInOptions';

interface UsedInSectionProps {
    id: string;
    usedIn: string | null;
    onChange: (id: string) => void;
}

const UsedInSection: React.FC<UsedInSectionProps> = (
    {
        id,
        usedIn,
        onChange,
    }) => {

    const [usedInOptions, setUsedInOptions] = useState<string[]>([]);

    const saveMethod = async (value: string | null, setSaveStatus: (saveStatus: SaveStatus) => void) => {
        await saveField(id, "used_in", value, onChange, setSaveStatus);
        await fetchUsedInOptions(setUsedInOptions);
    };

    const {saveStatus, onSave} = useSaveController(saveMethod);

    return (
        <EditableField
            value={usedIn}
            options={usedInOptions}
            saveStatus={saveStatus}
            onEdit={() => {
                fetchUsedInOptions(setUsedInOptions).then
            }}
            onSave={onSave}
            placeholder="Write a usage..."
            emptyText="Not defined"
            isLink={false}
        />
    );
};

export default UsedInSection;
