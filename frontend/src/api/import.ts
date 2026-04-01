import { api } from './client';
import type { ImportResult } from '../types/import';

const BASE_PATH = '/api/v1/import';

export const previewExcel = async (file: File): Promise<ImportResult> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<ImportResult>(
    `${BASE_PATH}/excel/preview`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );
  return response.data;
};

export const importExcel = async (file: File): Promise<ImportResult> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<ImportResult>(
    `${BASE_PATH}/excel`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );
  return response.data;
};

export const importSheet = async (
  file: File,
  sheetName: string,
): Promise<ImportResult> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post<ImportResult>(
    `${BASE_PATH}/excel/sheet`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      params: { sheet_name: sheetName },
    },
  );
  return response.data;
};
