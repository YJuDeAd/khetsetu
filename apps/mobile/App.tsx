import React, { useCallback, useState } from "react";
import { SafeAreaView, StyleSheet, View } from "react-native";
import { StatusBar } from "expo-status-bar";
import { Header } from "./src/components/Header";
import { BuyerBrowseScreen } from "./src/screens/BuyerBrowseScreen";
import { FarmerListingScreen } from "./src/screens/FarmerListingScreen";

export default function App() {
  const [activeTab, setActiveTab] = useState<"buyer" | "farmer">("buyer");

  const handleListingCreated = useCallback(() => {
    // Automatically navigate to buyer marketplace view to see the newly published produce
    setActiveTab("buyer");
  }, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar style="dark" />
      <View style={styles.container}>
        <Header activeTab={activeTab} onTabChange={setActiveTab} />
        {activeTab === "buyer" ? (
          <BuyerBrowseScreen />
        ) : (
          <FarmerListingScreen onListingCreated={handleListingCreated} />
        )}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: "#FFFFFF",
  },
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
  },
});
