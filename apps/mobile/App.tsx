import React from "react";
import { StyleSheet, Text, View, Pressable, SafeAreaView } from "react-native";
import { StatusBar } from "expo-status-bar";

export default function App() {
  const handleVoicePress = () => {
    // Voice recognition will trigger here in Phase 6
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <View style={styles.header}>
        <Text style={styles.title}>KhetSetu (खेतसेतु)</Text>
        <Text style={styles.subtitle}>Direct Farmer & FPO Marketplace</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardHeader}>Farmer Voice Portal</Text>
        <Text style={styles.cardBody}>
          Tap below to speak and query live mandi prices or list produce.
        </Text>

        <Pressable
          style={({ pressed }) => [
            styles.voiceButton,
            pressed && styles.voiceButtonPressed,
          ]}
          onPress={handleVoicePress}
          accessibilityRole="button"
          accessibilityLabel="Record Voice Command"
        >
          <Text style={styles.voiceButtonText}>🎙️ Speak / बोलें</Text>
        </Pressable>
      </View>

      <View style={styles.footer}>
        <Text style={styles.footerText}>SIH 2026 • PS ID 26033</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
    paddingHorizontal: 20,
    justifyContent: "space-between",
  },
  header: {
    marginTop: 24,
    alignItems: "center",
  },
  title: {
    fontSize: 28,
    fontWeight: "bold",
    color: "#166534",
  },
  subtitle: {
    fontSize: 14,
    color: "#64748B",
    marginTop: 4,
  },
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 24,
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 3,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    alignItems: "center",
  },
  cardHeader: {
    fontSize: 20,
    fontWeight: "600",
    color: "#1E293B",
    marginBottom: 8,
  },
  cardBody: {
    fontSize: 14,
    color: "#64748B",
    textAlign: "center",
    marginBottom: 24,
    lineHeight: 20,
  },
  voiceButton: {
    backgroundColor: "#16A34A",
    paddingVertical: 14,
    paddingHorizontal: 28,
    borderRadius: 999,
    alignItems: "center",
    justifyContent: "center",
    width: "100%",
  },
  voiceButtonPressed: {
    backgroundColor: "#15803D",
    opacity: 0.9,
  },
  voiceButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "bold",
  },
  footer: {
    marginBottom: 16,
    alignItems: "center",
  },
  footerText: {
    fontSize: 12,
    color: "#94A3B8",
  },
});
