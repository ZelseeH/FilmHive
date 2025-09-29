import React, { useState } from 'react';
import styles from './RecommendationScore.module.css';

interface RecommendationScoreProps {
    score: number;
    className?: string;
}

const RecommendationScore: React.FC<RecommendationScoreProps> = ({ score, className }) => {
    const [showTooltip, setShowTooltip] = useState(false);

    const formatScore = (score: number): number => {
        return Math.round(score * 100);
    };

    const getScoreColor = (score: number): string => {
        if (score >= 0.9) return '#2E7D32'; // ciemnozielony
        if (score >= 0.8) return '#4CAF50'; // zielony
        if (score >= 0.7) return '#8BC34A'; // jasnozielony
        if (score >= 0.6) return '#CDDC39'; // limonkowy
        if (score >= 0.5) return '#FFEB3B'; // żółty
        if (score >= 0.4) return '#FFC107'; // pomarańczowy
        if (score >= 0.3) return '#FF9800'; // ciemnopomarańczowy
        return '#F44336'; // czerwony
    };

    const getScoreDescription = (score: number): string => {
        const percentage = formatScore(score);

        if (score >= 0.9) return `Doskonałe dopasowanie (${percentage}%)`;
        if (score >= 0.8) return `Bardzo dobre dopasowanie (${percentage}%)`;
        if (score >= 0.7) return `Dobre dopasowanie (${percentage}%)`;
        if (score >= 0.6) return `Średnie dopasowanie (${percentage}%)`;
        if (score >= 0.5) return `Przeciętne dopasowanie (${percentage}%)`;
        if (score >= 0.4) return `Słabe dopasowanie (${percentage}%)`;
        return `Bardzo słabe dopasowanie (${percentage}%)`;
    };

    const getTextColor = (backgroundColor: string): string => {
        const darkColors = ['#2E7D32', '#4CAF50', '#F44336'];
        return darkColors.includes(backgroundColor) ? '#FFFFFF' : '#000000';
    };

    const backgroundColor = getScoreColor(score);
    const textColor = getTextColor(backgroundColor);
    const percentage = formatScore(score);

    return (
        <div
            className={`${styles.recommendationScore} ${className || ''}`}
            onMouseEnter={() => setShowTooltip(true)}
            onMouseLeave={() => setShowTooltip(false)}
        >
            <div
                className={styles.scoreCircle}
                style={{
                    backgroundColor: backgroundColor,
                    color: textColor
                }}
            >
                {percentage}%
            </div>

            {showTooltip && (
                <div className={styles.scoreTooltip}>
                    {getScoreDescription(score)}
                </div>
            )}
        </div>
    );
};

export default RecommendationScore;
