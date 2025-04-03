// src/components/Navbar/MobileMenu/MobileMenu.tsx
import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import SearchBar from '../SearchBar/SearchBar';
import styles from './MobileMenu.module.css';

interface MobileMenuProps {
    isOpen: boolean;
}

const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen }) => {
    const menuVariants = {
        open: {
            opacity: 1,
            height: 'auto',
            y: 0,
            transition: {
                duration: 0.3,
                ease: 'easeOut',
                when: 'beforeChildren',
                staggerChildren: 0.1,
            },
        },
        closed: {
            opacity: 0,
            height: 0,
            y: -10,
            transition: {
                duration: 0.3,
                ease: 'easeIn',
                when: 'afterChildren',
            },
        },
    };

    const childVariants = {
        open: {
            opacity: 1,
            y: 0,
            transition: {
                duration: 0.2,
                ease: 'easeOut',
            },
        },
        closed: {
            opacity: 0,
            y: 10,
            transition: {
                duration: 0.2,
                ease: 'easeIn',
            },
        },
    };

    return (
        <motion.div
            className={styles['mobile-links']}
            initial="closed"
            animate={isOpen ? "open" : "closed"}
            exit="closed"
            variants={menuVariants}
        >
            <motion.div variants={childVariants}>
                <SearchBar />
            </motion.div>
            <motion.div variants={childVariants}>
                <Link to="/movies" className={styles['movies-link']}>
                    Filmy
                </Link>
            </motion.div>
        </motion.div>
    );
};

export default MobileMenu;
