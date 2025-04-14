import { useState, useRef, useEffect } from 'react';
import { profileService } from '../services/profileService';

export const useBackgroundImage = (onImageUpdate?: () => void) => {
    const [tempBackgroundImage, setTempBackgroundImage] = useState<string | null>(null);
    const [backgroundPosition, setBackgroundPosition] = useState({ x: 50, y: 50 });
    const [isDragging, setIsDragging] = useState(false);
    const [uploadingBgImage, setUploadingBgImage] = useState(false);
    const [selectedBackgroundFile, setSelectedBackgroundFile] = useState<File | null>(null);

    const backgroundRef = useRef<HTMLDivElement>(null);
    const backgroundImageInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            if (isDragging && tempBackgroundImage && backgroundRef.current) {
                const rect = backgroundRef.current.getBoundingClientRect();
                const x = ((e.clientX - rect.left) / rect.width) * 100;
                const y = ((e.clientY - rect.top) / rect.height) * 100;

                const clampedX = Math.max(0, Math.min(100, x));
                const clampedY = Math.max(0, Math.min(100, y));

                setBackgroundPosition({ x: clampedX, y: clampedY });
            }
        };

        const handleMouseUp = () => {
            setIsDragging(false);
        };

        if (isDragging) {
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        }

        return () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, tempBackgroundImage]);

    const handleBackgroundClick = () => {
        if (!uploadingBgImage && !tempBackgroundImage) {
            backgroundImageInputRef.current?.click();
        }
    };

    const handleBackgroundChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files || e.target.files.length === 0) return;

        const file = e.target.files[0];
        setSelectedBackgroundFile(file);
        const objectUrl = URL.createObjectURL(file);
        setTempBackgroundImage(objectUrl);
        setBackgroundPosition({ x: 50, y: 50 });
    };

    const handleBackgroundMouseDown = (e: React.MouseEvent) => {
        if (tempBackgroundImage) {
            setIsDragging(true);
        }
    };

    const handleSaveBackground = async () => {
        if (!selectedBackgroundFile || !tempBackgroundImage) return;

        setUploadingBgImage(true);
        try {
            await profileService.uploadBackgroundImage(selectedBackgroundFile, backgroundPosition);
            URL.revokeObjectURL(tempBackgroundImage);
            onImageUpdate?.();
        } catch (error) {
            console.error('Błąd podczas przesyłania zdjęcia w tle:', error);
        } finally {
            setUploadingBgImage(false);
            setTempBackgroundImage(null);
            setSelectedBackgroundFile(null);
            setIsDragging(false);
        }
    };

    const handleCancelBackground = () => {
        if (tempBackgroundImage) {
            URL.revokeObjectURL(tempBackgroundImage);
        }
        setTempBackgroundImage(null);
        setSelectedBackgroundFile(null);
    };

    return {
        tempBackgroundImage,
        backgroundPosition,
        isDragging,
        uploadingBgImage,
        backgroundRef,
        backgroundImageInputRef,
        handleBackgroundClick,
        handleBackgroundChange,
        handleBackgroundMouseDown,
        handleSaveBackground,
        handleCancelBackground
    };
};