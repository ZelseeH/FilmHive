// Define interfaces for the data structures
interface EditModeState {
    [key: string]: boolean;
}

interface ErrorsState {
    [key: string]: string;
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

export const settingsUtils = {
    resetEditMode: (fields: EditModeState): EditModeState => {
        return Object.keys(fields).reduce<EditModeState>((acc, key) => ({ ...acc, [key]: false }), {} as EditModeState);
    },

    resetErrors: (fields: ErrorsState): ErrorsState => {
        return Object.keys(fields).reduce<ErrorsState>((acc, key) => ({ ...acc, [key]: '' }), {} as ErrorsState);
    },

    resetFormValues: (): FormValues => {
        return {
            username: '',
            name: '',
            bio: '',
            email: '',
            currentPassword: '',
            newPassword: '',
            confirmPassword: ''
        };
    }
};
