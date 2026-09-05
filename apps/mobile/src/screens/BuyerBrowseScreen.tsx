import React, { useCallback, useEffect, useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  RefreshControl,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { ListingCard } from "../components/ListingCard";
import { SearchBar } from "../components/SearchBar";
import { fetchListings } from "../services/api";
import { ProduceListing } from "../types/produce";

export const BuyerBrowseScreen: React.FC = () => {
  const [listings, setListings] = useState<ProduceListing[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const loadListings = useCallback(
    async (isRefresh = false) => {
      if (isRefresh) {
        setRefreshing(true);
      } else {
        setLoading(true);
      }
      setErrorMessage(null);

      try {
        const data = await fetchListings({
          crop_name: searchQuery.trim() || undefined,
          crop_category: selectedCategory || undefined,
        });
        setListings(data);
      } catch (error) {
        setErrorMessage(
          error instanceof Error ? error.message : "Could not load marketplace",
        );
      } finally {
        setLoading(false);
        setRefreshing(false);
      }
    },
    [searchQuery, selectedCategory],
  );

  useEffect(() => {
    loadListings();
  }, [loadListings]);

  const handleRefresh = useCallback(() => {
    loadListings(true);
  }, [loadListings]);

  const renderItem = useCallback(
    ({ item }: { item: ProduceListing }) => <ListingCard listing={item} />,
    [],
  );

  const keyExtractor = useCallback((item: ProduceListing) => item.id, []);

  return (
    <View style={styles.container}>
      <SearchBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedCategory={selectedCategory}
        onCategorySelect={setSelectedCategory}
      />

      {loading && !refreshing ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#166534" />
          <Text style={styles.loadingText}>Fetching fresh produce...</Text>
        </View>
      ) : errorMessage ? (
        <View style={styles.centerContainer}>
          <Text style={styles.errorEmoji}>⚠️</Text>
          <Text style={styles.errorText}>{errorMessage}</Text>
          <Text style={styles.errorSubtext}>
            Make sure the FastAPI backend is running on port 8000. Pull to retry.
          </Text>
        </View>
      ) : (
        <FlatList
          data={listings}
          keyExtractor={keyExtractor}
          renderItem={renderItem}
          contentContainerStyle={styles.listContent}
          refreshControl={
            <RefreshControl
              refreshing={refreshing}
              onRefresh={handleRefresh}
              tintColor="#166534"
              colors={["#166534"]}
            />
          }
          ListEmptyComponent={
            <View style={styles.emptyContainer}>
              <Text style={styles.emptyEmoji}>🌾</Text>
              <Text style={styles.emptyTitle}>No produce found</Text>
              <Text style={styles.emptySubtitle}>
                {searchQuery || selectedCategory
                  ? "Try changing your search or category filter."
                  : "No farmers have listed produce yet. Switch to Farmer mode to add one!"}
              </Text>
            </View>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8FAFC",
  },
  listContent: {
    paddingVertical: 8,
    flexGrow: 1,
  },
  centerContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingHorizontal: 32,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: "#64748B",
    fontWeight: "500",
  },
  errorEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  errorText: {
    fontSize: 16,
    fontWeight: "700",
    color: "#DC2626",
    textAlign: "center",
    marginBottom: 4,
  },
  errorSubtext: {
    fontSize: 12,
    color: "#64748B",
    textAlign: "center",
    lineHeight: 18,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    paddingVertical: 64,
    paddingHorizontal: 32,
  },
  emptyEmoji: {
    fontSize: 48,
    marginBottom: 12,
  },
  emptyTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 6,
  },
  emptySubtitle: {
    fontSize: 13,
    color: "#64748B",
    textAlign: "center",
    lineHeight: 20,
  },
});
