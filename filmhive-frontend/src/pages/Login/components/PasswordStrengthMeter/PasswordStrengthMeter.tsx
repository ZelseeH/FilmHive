// components/PasswordStrengthMeter.tsx
import React from 'react';
import styles from './PasswordStrengthMeter.module.css';

interface PasswordStrengthMeterProps {
    password: string;
}

const PasswordStrengthMeter: React.FC<PasswordStrengthMeterProps> = ({ password }) => {
    const calculateStrength = (password: string): { score: number; feedback: string[] } => {
        let score = 0;
        const feedback: string[] = [];

        if (password.length >= 8) {
            score += 1;
        } else {
            feedback.push('Minimum 8 znaków');
        }

        if (/[A-Z]/.test(password)) {
            score += 1;
        } else {
            feedback.push('Jedna wielka litera');
        }

        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
            score += 1;
        } else {
            feedback.push('Jeden znak specjalny');
        }

        if (/[0-9]/.test(password)) {
            score += 1;
        } else {
            feedback.push('Jedna cyfra');
        }

        return { score, feedback };
    };

    const { score, feedback } = calculateStrength(password);

    const getStrengthColor = (score: number): string => {
        if (score <= 1) return '#ff4757'; // Czerwony
        if (score <= 2) return '#ffa502'; // Żółty
        if (score <= 3) return '#2ed573'; // Zielony
        return '#1e90ff'; // Niebieski (bardzo silne)
    };

    const getStrengthText = (score: number): string => {
        if (score <= 1) return 'Słabe';
        if (score <= 2) return 'Średnie';
        if (score <= 3) return 'Silne';
        return 'Bardzo silne';
    };

    if (!password) return null;

    return (
        <div className={styles.container}>
            <div className={styles.strengthBar}>
                <div
                    className={styles.strengthFill}
                    style={{
                        width: `${(score / 4) * 100}%`,
                        backgroundColor: getStrengthColor(score)
                    }}
                />
            </div>
            <div className={styles.strengthText} style={{ color: getStrengthColor(score) }}>
                {getStrengthText(score)}
            </div>
            {feedback.length > 0 && (
                <ul className={styles.feedback}>
                    {feedback.map((item, index) => (
                        <li key={index}>{item}</li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default PasswordStrengthMeter;
