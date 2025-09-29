import React, { useState, useRef, useEffect } from 'react';
import styles from './ImageSelector.module.css';

interface ImageSelectorProps {
    currentImage?: string;
    onImageChange: (file: File | null, url: string | null) => void;
    onPreviewChange?: (preview: string | null) => void;
    placeholder?: string;
    acceptedFormats?: string;
    maxFileSize?: number; // w MB
    label?: string;
    required?: boolean;
    error?: string;
    disabled?: boolean;
    className?: string;
}

export const ImageSelector: React.FC<ImageSelectorProps> = ({
    currentImage,
    onImageChange,
    onPreviewChange,
    placeholder = "Brak zdjęcia",
    acceptedFormats = "image/*",
    maxFileSize = 5,
    label = "Zdjęcie",
    required = false,
    error,
    disabled = false,
    className
}) => {
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [imageUrl, setImageUrl] = useState<string>('');
    const [preview, setPreview] = useState<string | null>(currentImage || null);
    const [mode, setMode] = useState<'file' | 'url'>('file');
    const [dragOver, setDragOver] = useState(false);
    const [urlError, setUrlError] = useState<string>('');
    const [isValidatingUrl, setIsValidatingUrl] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Initialize with current image
    useEffect(() => {
        if (currentImage) {
            setPreview(currentImage);
            if (currentImage.startsWith('http')) {
                setMode('url');
                setImageUrl(currentImage);
            }
        }
    }, [currentImage]);

    // Walidacja URL-a obrazu
    const isValidImageUrl = (url: string): boolean => {
        try {
            const urlObj = new URL(url.trim());

            // Sprawdź czy URL jest prawidłowy
            if (!['http:', 'https:'].includes(urlObj.protocol)) {
                return false;
            }

            // Sprawdź czy URL kończy się rozszerzeniem obrazu lub zawiera parametry obrazu
            const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'];
            const pathname = urlObj.pathname.toLowerCase();
            const hasImageExtension = imageExtensions.some(ext => pathname.endsWith(ext));
            const hasImageParam = url.includes('image-type') || url.includes('format=') || url.includes('media/catalog');

            return hasImageExtension || hasImageParam;
        } catch {
            return false;
        }
    };

    // Testuj czy obraz można załadować
    const testImageLoad = (url: string): Promise<boolean> => {
        return new Promise((resolve) => {
            const img = new Image();
            img.onload = () => resolve(true);
            img.onerror = () => resolve(false);
            img.src = url;

            // Timeout po 10 sekundach
            setTimeout(() => resolve(false), 10000);
        });
    };

    const handleFileSelect = (file: File) => {
        // Validate file size
        if (file.size > maxFileSize * 1024 * 1024) {
            alert(`Plik jest za duży. Maksymalny rozmiar to ${maxFileSize}MB`);
            return;
        }

        // Validate file type
        if (!file.type.startsWith('image/')) {
            alert('Wybierz prawidłowy plik obrazu');
            return;
        }

        setSelectedFile(file);
        setImageUrl('');
        setUrlError('');

        // Create preview
        const reader = new FileReader();
        reader.onloadend = () => {
            const result = reader.result as string;
            setPreview(result);
            onPreviewChange?.(result);
        };
        reader.readAsDataURL(file);

        onImageChange(file, null);
    };

    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files && e.target.files[0]) {
            handleFileSelect(e.target.files[0]);
        }
    };

    const handleUrlChange = async (url: string) => {
        setImageUrl(url);
        setSelectedFile(null);
        setUrlError('');

        if (url.trim()) {
            // Podstawowa walidacja URL
            if (!isValidImageUrl(url.trim())) {
                setUrlError('URL nie wygląda na adres obrazu');
                setPreview(null);
                onPreviewChange?.(null);
                onImageChange(null, null);
                return;
            }

            // Sprawdź czy obraz można załadować
            setIsValidatingUrl(true);
            const isValidImage = await testImageLoad(url.trim());
            setIsValidatingUrl(false);

            if (isValidImage) {
                setPreview(url.trim());
                onPreviewChange?.(url.trim());
                onImageChange(null, url.trim());
                setUrlError('');
            } else {
                setUrlError('Nie można załadować obrazu z tego URL-a');
                setPreview(null);
                onPreviewChange?.(null);
                onImageChange(null, null);
            }
        } else {
            setPreview(null);
            onPreviewChange?.(null);
            onImageChange(null, null);
        }
    };

    const switchMode = (newMode: 'file' | 'url') => {
        setMode(newMode);
        setSelectedFile(null);
        setImageUrl('');
        setPreview(currentImage || null);
        setUrlError('');
        onImageChange(null, null);
    };

    const triggerFileSelect = () => {
        if (fileInputRef.current && !disabled) {
            fileInputRef.current.click();
        }
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        if (!disabled) {
            setDragOver(true);
        }
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setDragOver(false);

        if (disabled) return;

        const files = e.dataTransfer.files;
        if (files && files[0]) {
            handleFileSelect(files[0]);
        }
    };

    const removeImage = () => {
        setSelectedFile(null);
        setImageUrl('');
        setPreview(null);
        setUrlError('');
        onPreviewChange?.(null);
        onImageChange(null, null);

        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className={`${styles.imageSelector} ${className || ''}`}>
            {label && (
                <h3 className={styles.sectionTitle}>
                    {label}
                    {required && <span className={styles.required}>*</span>}
                </h3>
            )}

            {/* Mode Selector */}
            <div className={styles.modeSelector}>
                <button
                    type="button"
                    className={`${styles.modeButton} ${mode === 'file' ? styles.active : ''}`}
                    onClick={() => switchMode('file')}
                    disabled={disabled}
                >
                    📁 Plik lokalny
                </button>
                <button
                    type="button"
                    className={`${styles.modeButton} ${mode === 'url' ? styles.active : ''}`}
                    onClick={() => switchMode('url')}
                    disabled={disabled}
                >
                    🔗 Link z internetu
                </button>
            </div>

            {/* Image Container */}
            <div className={styles.imageContainer}>
                {preview ? (
                    <div className={styles.imagePreview}>
                        <img
                            src={preview}
                            alt="Podgląd"
                            className={styles.previewImage}
                            onError={() => {
                                console.log('Błąd ładowania obrazu:', preview);
                                setPreview(null);
                                onPreviewChange?.(null);
                                if (mode === 'url') {
                                    setUrlError('Błąd ładowania obrazu');
                                }
                            }}
                        />
                        {/* Remove button overlay */}
                        <div className={styles.imageOverlay}>
                            <button
                                type="button"
                                className={styles.removeImageButton}
                                onClick={removeImage}
                                disabled={disabled}
                                title="Usuń zdjęcie"
                            >
                                ✕
                            </button>
                        </div>
                    </div>
                ) : (
                    <div
                        className={`${styles.imagePlaceholder} ${dragOver ? styles.dragOver : ''} ${disabled ? styles.disabled : ''}`}
                        onClick={mode === 'file' ? triggerFileSelect : undefined}
                        onDragOver={mode === 'file' ? handleDragOver : undefined}
                        onDragLeave={mode === 'file' ? handleDragLeave : undefined}
                        onDrop={mode === 'file' ? handleDrop : undefined}
                    >
                        <i className="pi pi-image" style={{ fontSize: '3rem', color: '#ccc' }}></i>
                        <p>{placeholder}</p>
                        {mode === 'file' && !disabled && (
                            <small>Kliknij lub przeciągnij plik tutaj</small>
                        )}
                    </div>
                )}
            </div>

            {/* URL Input dla trybu URL */}
            {mode === 'url' && (
                <div className={styles.formField}>
                    <label className={styles.fieldLabel}>
                        URL zdjęcia{required && <span className={styles.required}>*</span>}:
                    </label>
                    <div className={styles.urlInputContainer}>
                        <input
                            type="url"
                            value={imageUrl}
                            onChange={(e) => handleUrlChange(e.target.value)}
                            placeholder="https://example.com/image.jpg"
                            className={`${styles.formInput} ${(error || urlError) ? styles.inputError : ''}`}
                            disabled={disabled || isValidatingUrl}
                        />
                        {isValidatingUrl && (
                            <div className={styles.validatingIndicator}>
                                <span className={styles.spinner}></span>
                                Sprawdzam...
                            </div>
                        )}
                    </div>
                    <div className={styles.fieldHint}>
                        Podaj pełny URL zdjęcia (JPG, PNG, WebP)
                    </div>
                    {urlError && (
                        <div className={styles.fieldError}>{urlError}</div>
                    )}
                </div>
            )}

            {/* File Actions dla trybu pliku */}
            {mode === 'file' && !preview && (
                <div className={styles.imageActions}>
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileChange}
                        accept={acceptedFormats}
                        style={{ display: 'none' }}
                        disabled={disabled}
                    />

                    <button
                        type="button"
                        className={styles.selectImageButton}
                        onClick={triggerFileSelect}
                        disabled={disabled}
                    >
                        Wybierz zdjęcie
                    </button>
                </div>
            )}

            {/* File Info */}
            {selectedFile && (
                <div className={styles.fileInfo}>
                    <span className={styles.fileName}>{selectedFile.name}</span>
                    <span className={styles.fileSize}>
                        ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                    </span>
                </div>
            )}

            {/* Error Message */}
            {error && (
                <div className={styles.fieldError}>{error}</div>
            )}

            {/* Hints */}
            <div className={styles.fieldHint}>
                Obsługiwane formaty: JPG, PNG, WebP. Maksymalny rozmiar: {maxFileSize}MB
            </div>
        </div>
    );
};

export default ImageSelector;
