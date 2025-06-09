import type {ImageRow as ImageRowType} from "../types/generated";
import { useState } from "react";

export type SetImageRows = (
    value: ImageRowType[] | ((prev: ImageRowType[]) => ImageRowType[])
) => void;

export type SaveStatus = {
  id: string;
  status: 'saving' | 'success' | 'error' | null;
  error: string | null;
};


export function useSaveController(
  saveMethod: (value: string | null, setSaveStatus: (saveStatus: SaveStatus) => void) => Promise<void>
) {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>({
    id: '',
    status: null,
    error: null,
  });

  const onSave = async (value: string | null) => {
    await saveMethod(value, setSaveStatus);
  };

  return { saveStatus, onSave };
}

