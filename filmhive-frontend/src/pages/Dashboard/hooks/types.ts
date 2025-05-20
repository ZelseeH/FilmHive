import { ReactNode } from 'react';

export interface SubMenuItem {
    label: string;
    path: string;
    icon?: ReactNode;
}

export interface MenuItem {
    label: string;
    icon: ReactNode;
    path?: string;
    subItems?: SubMenuItem[];
    adminOnly?: boolean;
}
