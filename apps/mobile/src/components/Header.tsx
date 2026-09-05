import React from "react";
import { StyleSheet, Text, View, Pressable } from "react-native";

interface HeaderProps {
  activeTab: "buyer" | "farmer";
  onTabChange: (tab: "buyer" | "farmer") => void;
}

export const Header: React.FC<HeaderProps> = React.memo(
  ({ activeTab, onTabChange }) => {
    return (
      <View style={styles.container}>
        <View style={styles.brandRow}>
          <Text style={styles.title}>KhetSetu</Text>
          <Text style={styles.hindiTitle}>खेतसेतु</Text>
        </View>

        <View style={styles.tabBar}>
          <Pressable
            accessibilityRole="tab"
            accessibilityLabel="Buyer Market View"
            style={({ pressed }) => [
              styles.tab,
              activeTab === "buyer" && styles.activeTab,
              pressed && styles.pressedTab,
            ]}
            onPress={() => onTabChange("buyer")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "buyer" && styles.activeTabText,
              ]}
            >
              🛒 Browse Market
            </Text>
          </Pressable>

          <Pressable
            accessibilityRole="tab"
            accessibilityLabel="Farmer Produce Listing View"
            style={({ pressed }) => [
              styles.tab,
              activeTab === "farmer" && styles.activeTab,
              pressed && styles.pressedTab,
            ]}
            onPress={() => onTabChange("farmer")}
          >
            <Text
              style={[
                styles.tabText,
                activeTab === "farmer" && styles.activeTabText,
              ]}
            >
              🌱 List Produce
            </Text>
          </Pressable>
        </View>
      </View>
    );
  },
);

Header.displayName = "Header";

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
    backgroundColor: "#FFFFFF",
    borderBottomWidth: 1,
    borderBottomColor: "#E2E8F0",
  },
  brandRow: {
    flexDirection: "row",
    alignItems: "baseline",
    justifyContent: "space-between",
    marginBottom: 10,
  },
  title: {
    fontSize: 22,
    fontWeight: "800",
    color: "#166534",
  },
  hindiTitle: {
    fontSize: 16,
    fontWeight: "600",
    color: "#475569",
  },
  tabBar: {
    flexDirection: "row",
    backgroundColor: "#F1F5F9",
    borderRadius: 10,
    padding: 4,
  },
  tab: {
    flex: 1,
    paddingVertical: 8,
    alignItems: "center",
    borderRadius: 8,
  },
  activeTab: {
    backgroundColor: "#FFFFFF",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  pressedTab: {
    opacity: 0.8,
  },
  tabText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#64748B",
  },
  activeTabText: {
    color: "#166534",
    fontWeight: "700",
  },
});
