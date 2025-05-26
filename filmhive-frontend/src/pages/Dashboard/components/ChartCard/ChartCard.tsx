import React from 'react';
import styles from './ChartCard.module.css';

interface ChartData {
    label: string;
    value: number;
    color: string;
}

interface ChartCardProps {
    title: string;
    type: 'pie' | 'bar';
    data: ChartData[];
}

const ChartCard: React.FC<ChartCardProps> = ({ title, type, data }) => {
    const total = data.reduce((sum, item) => sum + item.value, 0);

    const renderPieChart = () => {
        let cumulativePercentage = 0;

        return (
            <div className={styles.pieChart}>
                <svg viewBox="0 0 42 42" className={styles.donut}>
                    {data.map((item, index) => {
                        const percentage = (item.value / total) * 100;
                        const strokeDasharray = `${percentage} ${100 - percentage}`;
                        const strokeDashoffset = -cumulativePercentage;
                        cumulativePercentage += percentage;

                        return (
                            <circle
                                key={index}
                                className={styles.donutSegment}
                                cx="21"
                                cy="21"
                                r="15.915"
                                fill="transparent"
                                stroke={item.color}
                                strokeWidth="3"
                                strokeDasharray={strokeDasharray}
                                strokeDashoffset={strokeDashoffset}
                            />
                        );
                    })}
                </svg>
                <div className={styles.chartLegend}>
                    {data.map((item, index) => (
                        <div key={index} className={styles.legendItem}>
                            <div
                                className={styles.legendColor}
                                style={{ backgroundColor: item.color }}
                            />
                            <span className={styles.legendLabel}>
                                {item.label}: {item.value}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className={styles.chartCard}>
            <h3 className={styles.chartTitle}>{title}</h3>
            <div className={styles.chartContent}>
                {type === 'pie' && renderPieChart()}
            </div>
        </div>
    );
};

export default ChartCard;
