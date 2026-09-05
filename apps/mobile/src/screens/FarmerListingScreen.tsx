import React from "react";
import {
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { FarmerListingForm } from "../components/FarmerListingForm";

interface FarmerListingScreenProps {
  onListingCreated?: () => void;
}

export const FarmerListingScreen: React.FC<FarmerListingScreenProps> = ({
  onListingCreated,
}) => {
  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        {/* Header Hero Banner */}
        <View style={styles.heroBanner}>
          <Text style={styles.heroTitle}>List Produce & Sell Direct</Text>
          <Text style={styles.heroSubtitle}>
            Connect directly with verified wholesale buyers, FPOs, and retailers. 100% transparent pricing with escrow protection.
          </Text>

        </View>

        <FarmerListingForm onSuccess={onListingCreated} />
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
  },
  scrollContent: {
    paddingVertical: 12,
  },
  heroBanner: {
    backgroundColor: "#166534",
    marginHorizontal: 16,
    marginBottom: 16,
    padding: 18,
    borderRadius: 16,
    shadowColor: "#166534",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 3,
  },
  heroBadge: {
    alignSelf: "flex-start",
    backgroundColor: "rgba(220, 252, 231, 0.2)",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
    marginBottom: 8,
  },
  heroBadgeText: {
    color: "#DCFCE7",
    fontSize: 10,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  heroTitle: {
    fontSize: 20,
    fontWeight: "800",
    color: "#FFFFFF",
    marginBottom: 6,
  },
  heroSubtitle: {
    fontSize: 13,
    color: "#BBF7D0",
    lineHeight: 18,
    marginBottom: 14,
  },
  perksRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: "rgba(0, 0, 0, 0.15)",
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 10,
  },
  perkItem: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
  },
  perkIcon: {
    fontSize: 12,
  },
  perkText: {
    fontSize: 11,
    color: "#FFFFFF",
    fontWeight: "600",
  },
});
