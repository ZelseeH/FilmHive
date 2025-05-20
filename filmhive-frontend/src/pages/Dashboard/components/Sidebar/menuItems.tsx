import React from 'react';
import {
    FaHome, FaChartBar, FaUsers, FaTags, FaTheaterMasks,
    FaChair, FaFilm, FaCog, FaList, FaUserPlus, FaPlus
} from 'react-icons/fa';
import { MenuItem } from '../../hooks/types';

export const menuItems: MenuItem[] = [
    { label: 'Dashboard', icon: <FaHome />, path: '/dashboardpanel' },
    { label: 'Statystyki', icon: <FaChartBar />, path: '/dashboardpanel/stats' },
    {
        label: 'Użytkownicy',
        icon: <FaUsers />,
        adminOnly: true,
        subItems: [
            { label: 'Zarządzaj', path: '/dashboardpanel/users/manage', icon: <FaList /> },
            { label: 'Dodaj', path: '/dashboardpanel/users/add', icon: <FaUserPlus /> }
        ]
    },
    { label: 'Gatunki', icon: <FaTags />, path: '/dashboardpanel/genres' },
    {
        label: 'Aktorzy',
        icon: <FaTheaterMasks />,
        subItems: [
            { label: 'Zarządzaj', path: '/dashboardpanel/actors/manage', icon: <FaList /> },
            { label: 'Dodaj', path: '/dashboardpanel/actors/add', icon: <FaPlus /> }
        ]
    },
    {
        label: 'Reżyserzy',
        icon: <FaChair />,
        subItems: [
            { label: 'Zarządzaj', path: '/dashboardpanel/directors/manage', icon: <FaList /> },
            { label: 'Dodaj', path: '/dashboardpanel/directors/add', icon: <FaPlus /> }
        ]
    },
    {
        label: 'Filmy',
        icon: <FaFilm />,
        subItems: [
            { label: 'Zarządzaj', path: '/dashboardpanel/movies/manage', icon: <FaList /> },
            { label: 'Dodaj', path: '/dashboardpanel/movies/add', icon: <FaPlus /> }
        ]
    },
    { label: 'Ustawienia', icon: <FaCog />, path: '/dashboardpanel/settings' },
];
