import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView, StyleSheet } from 'react-native';
import { sendCommandToNova } from '../lib/api-client';

export default function ChatScreen() {
    const [messages, setMessages] = useState<{role: 'user' | 'nova', text: string}[]>([]);
    const [inputText, setInputText] = useState('');
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        if (!inputText.trim()) return;
        
        const userText = inputText;
        setMessages(prev => [...prev, { role: 'user', text: userText }]);
        setInputText('');
        setLoading(true);

        const result = await sendCommandToNova(userText);
        setMessages(prev => [...prev, { role: 'nova', text: result.response }]);
        setLoading(false);
    };

    return (
        <View style={styles.container}>
            <ScrollView style={styles.chatArea} contentContainerStyle={{ paddingBottom: 20 }}>
                {messages.map((msg, idx) => (
                    <View key={idx} style={[styles.messageBubble, msg.role === 'nova' ? styles.novaBubble : styles.userBubble]}>
                        <Text style={styles.messageText}>{msg.text}</Text>
                    </View>
                ))}
                {loading && <Text style={styles.loadingText}>NOVA is thinking...</Text>}
            </ScrollView>
            
            <View style={styles.inputArea}>
                <TextInput 
                    style={styles.input} 
                    value={inputText}
                    onChangeText={setInputText}
                    placeholder="Command NOVA..."
                    placeholderTextColor="#888"
                    onSubmitEditing={sendMessage}
                />
                <TouchableOpacity style={styles.sendButton} onPress={sendMessage} disabled={loading}>
                    <Text style={styles.sendButtonText}>Send</Text>
                </TouchableOpacity>
            </View>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#121212' },
    chatArea: { flex: 1, padding: 16 },
    messageBubble: { maxWidth: '80%', padding: 12, borderRadius: 16, marginBottom: 10 },
    userBubble: { alignSelf: 'flex-end', backgroundColor: '#0A84FF', borderBottomRightRadius: 4 },
    novaBubble: { alignSelf: 'flex-start', backgroundColor: '#2C2C2E', borderBottomLeftRadius: 4 },
    messageText: { color: 'white', fontSize: 16 },
    loadingText: { color: '#888', alignSelf: 'center', marginTop: 10 },
    inputArea: { flexDirection: 'row', padding: 10, backgroundColor: '#1E1E1E', borderTopWidth: 1, borderColor: '#333' },
    input: { flex: 1, backgroundColor: '#2C2C2E', color: 'white', padding: 12, borderRadius: 20, marginRight: 10 },
    sendButton: { justifyContent: 'center', alignItems: 'center', backgroundColor: '#0A84FF', borderRadius: 20, paddingHorizontal: 20 },
    sendButtonText: { color: 'white', fontWeight: 'bold' }
});
