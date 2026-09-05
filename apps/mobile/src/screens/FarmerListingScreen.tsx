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
      >
        <View style={styles.banner}>
          <Text style={styles.bannerTitle}>🌾 Direct Farmer Marketplace</Text>
          <Text style={styles.bannerSubtitle}>
            Sell your produce directly to consumers, restaurants, and bulk buyers with zero middlemen markups.
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
  banner: {
    backgroundColor: "#DCFCE7",
    marginHorizontal: 16,
    marginBottom: 4,
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#BBF7D0",
  },
  bannerTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#166534",
    marginBottom: 4,
  },
  bannerSubtitle: {
    fontSize: 13,
    color: "#334155",
    lineHeight: 18,
  },
});
