import { useState, useEffect, ChangeEvent } from 'react';
import { userService } from '../services/userService';

interface UserData {
    username: string;
    name: string;
    bio: string;
    email: string;
}

interface EditModeState {
    username: boolean;
    bio: boolean;
    email: boolean;
    password: boolean;
    name: boolean;
}

interface FormValues {
    username: string;
    name: string;
    bio: string;
    email: string;
    currentPassword: string;
    newPassword: string;
    confirmPassword: string;
}

interface MessageState {
    type: string;
    text: string;
}

interface ModalErrors {
    username: string;
    bio: string;
    email: string;
    password: string;
    name: string;
}

export const useUserSettings = () => {
    const [userData, setUserData] = useState<UserData>({
        username: '',
        name: '',
        bio: '',
        email: '',
    });

    const [editMode, setEditMode] = useState<EditModeState>({
        username: false,
        bio: false,
        email: false,
        password: false,
        name: false
    });

    const [formValues, setFormValues] = useState<FormValues>({
        username: '',
        name: '',
        bio: '',
        email: '',
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
    });

    const [message, setMessage] = useState<MessageState>({ type: '', text: '' });
    const [modalErrors, setModalErrors] = useState<ModalErrors>({
        username: '',
        bio: '',
        email: '',
        password: '',
        name: ''
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchUserData();
    }, []);

    const fetchUserData = async () => {
        try {
            setLoading(true);
            const data = await userService.getUserProfile();
            setUserData({
                username: data.username || '',
                name: data.name || '',
                bio: data.bio || '',
                email: data.email || ''
            });
        } catch (error: unknown) {
            setMessage({ type: 'error', text: 'Wystąpił błąd podczas pobierania danych.' });
        } finally {
            setLoading(false);
        }
    };

    const handleEdit = (field: keyof EditModeState) => {
        setFormValues({
            ...formValues,
            [field]: userData[field as keyof UserData] || ''
        });

        const resetEditMode: EditModeState = {
            username: false,
            bio: false,
            email: false,
            password: false,
            name: false
        };

        setEditMode({
            ...resetEditMode,
            [field]: true
        });

        setMessage({ type: '', text: '' });
        setModalErrors({
            username: '',
            bio: '',
            email: '',
            password: '',
            name: ''
        });
    };

    const handleCancel = () => {

        const resetEditMode: EditModeState = {
            username: false,
            bio: false,
            email: false,
            password: false,
            name: false
        };

        setEditMode(resetEditMode);

        setFormValues({
            username: '',
            name: '',
            bio: '',
            email: '',
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
        });

        setModalErrors({
            username: '',
            bio: '',
            email: '',
            password: '',
            name: ''
        });
    };

    const handleChange = (e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormValues(prev => ({
            ...prev,
            [name]: value
        }));
    };

    return {
        userData,
        editMode,
        formValues,
        message,
        modalErrors,
        loading,
        handleEdit,
        handleCancel,
        handleChange,
        setModalErrors,
        setMessage,
        setUserData,
        setLoading
    };
};
