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
        if (count >= 1000) return '1k+';
        if (count >= 1) return `${(count / 1).toFixed(0)}`;
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
                    max={1000}
                    value={value}
                    onChange={handleChange}
                    tooltip={false}
                />
                <div className={styles.sliderLabels}>
                    <span>0</span>
                    <span>10K+</span>
                </div>
            </div>
        </div>
    );
};

export default RatingCountSlider;
