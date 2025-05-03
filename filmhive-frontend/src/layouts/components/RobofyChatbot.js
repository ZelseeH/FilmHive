// components/RobofyChatbot.js
import { useEffect } from 'react';

const RobofyChatbot = () => {
    useEffect(() => {
        if (document.getElementById('chatbotscript')) return;
        const script = document.createElement('script');
        script.id = 'chatbotscript';
        script.dataset.accountid = '4hdrjxoFRlauaZEzs+67Mw==';
        script.dataset.websiteid = 'xNElYjC0yEZ74ED01uXt3w==';
        script.src = 'https://app.robofy.ai/bot/js/common.js?v=' + new Date().getTime();
        document.head.appendChild(script);
    }, []);
    return null;
};

export default RobofyChatbot;
