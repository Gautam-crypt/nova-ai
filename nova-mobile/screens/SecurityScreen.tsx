import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from 'react-native';
import { fetchFindings, fetchSystemStatus } from '../lib/api-client';

export default function SecurityScreen() {
    const [findings, setFindings] = useState<any[]>([]);
    const [status, setStatus] = useState<any>(null);
    const [refreshing, setRefreshing] = useState(false);

    const loadData = async () => {
        setRefreshing(true);
        const f = await fetchFindings();
        const s = await fetchSystemStatus();
        if (f) setFindings(f.findings || []);
        if (s) setStatus(s);
        setRefreshing(false);
    };

    useEffect(() => {
        loadData();
        const interval = setInterval(loadData, 10000); // Auto-refresh every 10s
        return () => clearInterval(interval);
    }, []);

    return (
        <View style={styles.container}>
            <View style={styles.header}>
                <Text style={styles.headerTitle}>KAVACH Security</Text>
                <Text style={styles.statusText}>
                    Status: {status ? status.status : 'Disconnected'}
                </Text>
            </View>
            
            <ScrollView 
                style={styles.content}
                refreshControl={<RefreshControl refreshing={refreshing} onRefresh={loadData} tintColor="#fff" />}
            >
                <Text style={styles.sectionTitle}>Active Alerts ({findings.length})</Text>
                
                {findings.length === 0 ? (
                    <Text style={styles.safeText}>System is secure. No active threats.</Text>
                ) : (
                    findings.map((finding, idx) => (
                        <View key={idx} style={styles.alertCard}>
                            <View style={[styles.priorityBadge, finding.priority === 3 ? styles.highPriority : styles.lowPriority]}>
                                <Text style={styles.priorityText}>{finding.priority === 3 ? 'HIGH' : 'LOW'}</Text>
                            </View>
                            <Text style={styles.alertTitle}>{finding.title}</Text>
                            <Text style={styles.alertDetail}>{finding.detail}</Text>
                        </View>
                    ))
                )}
            </ScrollView>
        </View>
    );
}

const styles = StyleSheet.create({
    container: { flex: 1, backgroundColor: '#121212' },
    header: { padding: 20, backgroundColor: '#1E1E1E', borderBottomWidth: 1, borderColor: '#333' },
    headerTitle: { color: 'white', fontSize: 24, fontWeight: 'bold' },
    statusText: { color: '#4CD964', fontSize: 14, marginTop: 5 },
    content: { flex: 1, padding: 16 },
    sectionTitle: { color: '#888', fontSize: 14, fontWeight: 'bold', marginBottom: 15, textTransform: 'uppercase' },
    safeText: { color: '#4CD964', fontSize: 16, textAlign: 'center', marginTop: 40 },
    alertCard: { backgroundColor: '#2C2C2E', padding: 16, borderRadius: 12, marginBottom: 15 },
    alertTitle: { color: 'white', fontSize: 16, fontWeight: 'bold', marginBottom: 5, marginTop: 10 },
    alertDetail: { color: '#BBB', fontSize: 14 },
    priorityBadge: { alignSelf: 'flex-start', paddingHorizontal: 8, paddingVertical: 4, borderRadius: 4 },
    highPriority: { backgroundColor: '#FF3B30' },
    lowPriority: { backgroundColor: '#FFCC00' },
    priorityText: { color: 'white', fontSize: 10, fontWeight: 'bold' }
});
