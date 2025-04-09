import React from 'react';
import Slider from 'react-rangeslider';
import 'react-rangeslider/lib/index.css';
import styles from './RatingCountSlider.module.css';

interface RatingCountSliderProps {
    value: number;
    onChange: (value: number) => void;
}

const RatingCountSlider: React.FC<RatingCountSliderProps> = ({ value, onChange }) => {
    const formatRatingCount = (count: number) => {
        if (count >= 1000000) return '1M+';
        if (count >= 1000) return `${(count / 1000).toFixed(0)}K`;
        return count.toString();
    };

    const handleChange = (newValue: number) => {
        onChange(newValue);
    };

    return (
        <div className={styles.filterSection}>
            <h3>Minimalna ilość ocen</h3>
            <div className={styles.sliderContainer}>
                <div className={styles.sliderValue}>
                    Min: {formatRatingCount(value)}
                </div>
                <Slider
                    min={0}
                    max={1000000}
                    value={value}
                    onChange={handleChange}
                    tooltip={false}
                />
                <div className={styles.sliderLabels}>
                    <span>0</span>
                    <span>1M+</span>
                </div>
            </div>
        </div>
    );
};

export default RatingCountSlider;
