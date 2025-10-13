import React from 'react';
import { AllStatistics } from '../../types/statistics';
import StatCard from '../StatCard/StatCard';
import styles from './QuickStats.module.css';

interface QuickStatsProps {
    statistics: AllStatistics;
}

const QuickStats: React.FC<QuickStatsProps> = ({ statistics }) => {
    return (
        <div className={styles.quickStats}>
            <StatCard
                title="Łączna liczba użytkowników"
                value={statistics.users.total_users}
                icon="👥"
                color="blue"
                subtitle={`${statistics.users.account_status.active_users} aktywnych`}
            />
            <StatCard
                title="Łączna liczba filmów"
                value={statistics.movies.total_movies}
                icon="🎬"
                color="yellow"
                subtitle={`Ocena: ${statistics.movies.average_rating}/10`}
            />
            <StatCard
                title="Łączna liczba aktorów"
                value={statistics.actors.total_actors}
                icon="🎭"
                color="green"
                subtitle={`${statistics.actors.recent_actors_30_days} nowych`}
            />
            <StatCard
                title="Łączna liczba komentarzy"
                value={statistics.comments.total_comments}
                icon="💬"
                color="red"
                subtitle={`${statistics.comments.recent_comments_30_days} w miesiącu`}
            />
        </div>
    );
};

export default QuickStats;
