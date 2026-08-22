import axios from 'axios';

// The IP address of the PC running the main.py server
// Make sure both PC and Mobile are on the same WiFi network
const API_BASE_URL = 'http://192.168.1.130:8080';

export const sendCommandToNova = async (command: string) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/chat`, {
            message: command
        });
        return response.data;
    } catch (error) {
        console.error("Error communicating with NOVA:", error);
        return {
            response: "Connection error. Make sure NOVA is running on your PC and the IP address is correct.",
            status: "error"
        };
    }
};

export const fetchSystemStatus = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/status`);
        return response.data;
    } catch (error) {
        console.error("Error fetching status:", error);
        return null;
    }
};

export const fetchFindings = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/findings`);
        return response.data;
    } catch (error) {
        console.error("Error fetching findings:", error);
        return null;
    }
};
