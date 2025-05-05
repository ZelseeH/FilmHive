import { useState, useRef, useEffect } from 'react';

interface EditableField<T> {
    value: T;
    isEditing: boolean;
}

export function useInlineEdit<T extends Record<string, any>>(initialData: T) {
    const inputRefs = useRef<Record<string, HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | null>>({});

    const [fields, setFields] = useState<Record<keyof T, EditableField<any>>>(() => {
        const result: Record<string, EditableField<any>> = {};

        for (const key in initialData) {
            result[key] = {
                value: initialData[key],
                isEditing: false
            };
        }

        return result as Record<keyof T, EditableField<any>>;
    });

    const [lastEditedField, setLastEditedField] = useState<keyof T | null>(null);

    useEffect(() => {
        if (lastEditedField && inputRefs.current[lastEditedField as string]) {
            inputRefs.current[lastEditedField as string]?.focus();
        }
    }, [lastEditedField, fields]);

    const toggleEdit = (fieldKey: keyof T) => {
        const isCurrentlyEditing = fields[fieldKey].isEditing;

        if (!isCurrentlyEditing) {
            setLastEditedField(fieldKey);
        }

        setFields(prev => ({
            ...prev,
            [fieldKey]: {
                ...prev[fieldKey],
                isEditing: !isCurrentlyEditing
            }
        }));
    };

    const updateField = (fieldKey: keyof T, value: any) => {
        setFields(prev => ({
            ...prev,
            [fieldKey]: {
                ...prev[fieldKey],
                value
            }
        }));
    };

    const cancelEdit = (fieldKey: keyof T) => {
        setFields(prev => ({
            ...prev,
            [fieldKey]: {
                ...prev[fieldKey],
                isEditing: false,
                value: initialData[fieldKey]
            }
        }));
    };

    const getValues = () => {
        const result: Partial<T> = {};

        for (const key in fields) {
            result[key as keyof T] = fields[key as keyof T].value;
        }

        return result as T;
    };

    // Funkcja do ustawienia referencji
    const setInputRef = (fieldKey: keyof T, element: HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement | null) => {
        inputRefs.current[fieldKey as string] = element;
    };

    return {
        fields,
        toggleEdit,
        updateField,
        cancelEdit,
        getValues,
        setInputRef // Eksportujemy funkcję do ustawiania referencji
    };
}
