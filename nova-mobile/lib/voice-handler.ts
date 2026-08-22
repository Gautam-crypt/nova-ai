import * as Speech from 'expo-speech';

export const speak = (text: string) => {
    Speech.speak(text, {
        pitch: 1.0,
        rate: 0.9,
    });
};

export const stopSpeaking = () => {
    Speech.stop();
};
