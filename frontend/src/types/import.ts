export interface ImportError {
  sheet: string;
  row: number;
  column: string;
  message: string;
}

export interface SheetResult {
  sheet: string;
  rows_parsed: number;
  rows_imported: number;
  rows_skipped: number;
  errors: ImportError[];
}

export interface ImportResult {
  sheets: SheetResult[];
  total_errors: number;
  is_preview: boolean;
}
