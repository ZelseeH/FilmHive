import React from 'react';
import { Link } from 'react-router-dom';
import styles from './Sidebar.module.css';
import { useSidebar } from '../../hooks/useSidebar';
import { menuItems } from './menuItems';
import {
    FaUser, FaSignOutAlt, FaChevronDown, FaChevronUp,
    FaChevronLeft, FaChevronRight
} from 'react-icons/fa';

interface SidebarProps {
    collapsed: boolean;
    toggleSidebar: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ collapsed, toggleSidebar }) => {
    const {
        expandedItems,
        isMobile,
        user,
        isAdmin,
        isModerator,
        toggleSubmenu,
        isActive,
        isSubmenuActive
    } = useSidebar(collapsed, toggleSidebar);

    // Filtrowanie elementów menu w zależności od roli
    const filteredMenuItems = menuItems.filter(item => {
        if (item.adminOnly && !isAdmin()) {
            return false;
        }
        return true;
    });

    return (
        <div className={styles.sidebarWrapper}>
            <div className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''} ${isMobile && !collapsed ? styles.open : ''}`}>
                <div className={styles.sidebarHeader}>
                    <div className={styles.logo}>
                        {!collapsed && <span>PANEL</span>}
                    </div>
                </div>

                <div className={styles.userInfo}>
                    <div className={styles.avatar}>
                        <FaUser />
                    </div>
                    {!collapsed && (
                        <div className={styles.userDetails}>
                            <div className={styles.userName}>{user?.username || 'Użytkownik'}</div>
                            <div className={styles.userRole}>
                                {isAdmin() ? 'Administrator' : isModerator() ? 'Moderator' : 'Użytkownik'}
                            </div>
                        </div>
                    )}
                </div>

                <div className={styles.menuContainer}>
                    <ul className={styles.menu}>
                        {filteredMenuItems.map((item, idx) => (
                            <li
                                key={idx}
                                className={`
                                    ${styles.menuItem} 
                                    ${isActive(item.path) || isSubmenuActive(item.subItems) ? styles.active : ''}
                                `}
                            >
                                {item.subItems ? (
                                    <>
                                        <a
                                            href="#"
                                            className={styles.menuItemWithSubmenu}
                                            onClick={(e) => toggleSubmenu(item.label, e)}
                                        >
                                            <span className={styles.icon}>{item.icon}</span>
                                            {!collapsed && (
                                                <>
                                                    <span className={styles.label}>{item.label}</span>
                                                    <span className={styles.arrow}>
                                                        {expandedItems[item.label] ? <FaChevronUp /> : <FaChevronDown />}
                                                    </span>
                                                </>
                                            )}
                                        </a>
                                        <ul className={`${styles.submenu} ${expandedItems[item.label] ? styles.expanded : ''}`}>
                                            {item.subItems.map((subItem, subIdx) => (
                                                <li
                                                    key={subIdx}
                                                    className={`${styles.submenuItem} ${isActive(subItem.path) ? styles.active : ''}`}
                                                >
                                                    <Link to={subItem.path}>
                                                        {subItem.icon && <span className={styles.subIcon}>{subItem.icon}</span>}
                                                        <span className={styles.subLabel}>{subItem.label}</span>
                                                    </Link>
                                                </li>
                                            ))}
                                        </ul>
                                    </>
                                ) : (
                                    <Link to={item.path || '#'}>
                                        <span className={styles.icon}>{item.icon}</span>
                                        {!collapsed && <span className={styles.label}>{item.label}</span>}
                                    </Link>
                                )}
                            </li>
                        ))}
                    </ul>
                </div>

                <div className={styles.logout}>
                    <Link to="/logout" className={styles.logoutBtn}>
                        <span className={styles.icon}><FaSignOutAlt /></span>
                        {!collapsed && <span>Wyjdź</span>}
                    </Link>
                </div>
            </div>

            {/* Przycisk toggle poza sidebarem */}
            <button
                className={styles.toggleBtn}
                onClick={toggleSidebar}
                aria-label="Toggle sidebar width"
            >
                {collapsed ? <FaChevronRight /> : <FaChevronLeft />}
            </button>

            {isMobile && !collapsed && <div className={styles.overlay} onClick={toggleSidebar}></div>}
        </div>
    );
};

export default Sidebar;
