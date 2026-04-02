import { type DragEvent, type ChangeEvent, useCallback, useRef, useState } from 'react';

interface FileUploadProps {
  accept?: string;
  onFile: (file: File) => void;
  isLoading?: boolean;
  label?: string;
  description?: string;
}

function Spinner() {
  return (
    <svg
      className="animate-spin h-6 w-6 text-primary"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  );
}

function UploadIcon() {
  return (
    <svg
      className="h-10 w-10 text-on-surface-variant"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
      />
    </svg>
  );
}

function FileIcon() {
  return (
    <svg
      className="h-5 w-5 text-primary"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth={1.5}
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
      />
    </svg>
  );
}

function extractAcceptedExtensions(accept: string): string[] {
  return accept
    .split(',')
    .map((ext) => ext.trim().toLowerCase())
    .filter(Boolean);
}

function isAcceptedFile(file: File, accept: string): boolean {
  const accepted = extractAcceptedExtensions(accept);
  const fileName = file.name.toLowerCase();
  const mimeType = file.type.toLowerCase();

  return accepted.some((token) => {
    if (token.startsWith('.')) {
      return fileName.endsWith(token);
    }
    if (token.includes('/')) {
      if (token.endsWith('/*')) {
        return mimeType.startsWith(token.replace('/*', '/'));
      }
      return mimeType === token;
    }
    return false;
  });
}

export function FileUpload({
  accept = '.xlsx',
  onFile,
  isLoading = false,
  label = 'Deposer un fichier',
  description = 'Glissez-deposez ou cliquez pour selectionner',
}: FileUploadProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(
    (file: File) => {
      setError(null);

      if (!isAcceptedFile(file, accept)) {
        const extensions = extractAcceptedExtensions(accept).join(', ');
        setError(`Type de fichier non accepte. Formats attendus : ${extensions}`);
        setSelectedFile(null);
        return;
      }

      setSelectedFile(file);
      onFile(file);
    },
    [accept, onFile],
  );

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragOver(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile],
  );

  const handleChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFile(file);
      }
      if (inputRef.current) {
        inputRef.current.value = '';
      }
    },
    [handleFile],
  );

  const handleClick = useCallback(() => {
    if (!isLoading) {
      inputRef.current?.click();
    }
  }, [isLoading]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        handleClick();
      }
    },
    [handleClick],
  );

  return (
    <div className="flex flex-col gap-2">
      <div
        role="button"
        tabIndex={0}
        aria-label={label}
        onClick={handleClick}
        onKeyDown={handleKeyDown}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={[
          'relative rounded-lg p-8 text-center transition-colors duration-150 cursor-pointer',
          'ring-2 ring-dashed',
          isDragOver
            ? 'bg-primary/10 ring-primary/40'
            : 'bg-surface-container-high/50 ring-outline-variant/15',
          isLoading ? 'pointer-events-none' : '',
        ].join(' ')}
      >
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center rounded-lg bg-surface-container-high/80">
            <Spinner />
          </div>
        )}

        <div className="flex flex-col items-center gap-3">
          {selectedFile ? (
            <>
              <FileIcon />
              <p className="font-sans text-sm font-medium text-on-surface">
                {selectedFile.name}
              </p>
              <p className="font-sans text-xs text-on-surface-variant">
                Cliquez ou deposez pour remplacer
              </p>
            </>
          ) : (
            <>
              <UploadIcon />
              <p className="font-sans text-lg text-on-surface">{label}</p>
              <p className="text-sm text-on-surface-variant font-sans">
                {description}
              </p>
            </>
          )}
        </div>

        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={handleChange}
          className="hidden"
          aria-hidden="true"
          tabIndex={-1}
        />
      </div>

      {error && (
        <p className="text-sm text-error font-sans" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
