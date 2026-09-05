import React from "react";
import { StyleSheet, Text, View, TextInput, ScrollView, Pressable } from "react-native";

interface SearchBarProps {
  searchQuery: string;
  onSearchChange: (text: string) => void;
  selectedCategory: string;
  onCategorySelect: (category: string) => void;
}

const CATEGORIES = [
  "All",
  "Cereals",
  "Vegetables",
  "Fruits",
  "Pulses",
  "Oilseeds",
];

export const SearchBar: React.FC<SearchBarProps> = React.memo(
  ({ searchQuery, onSearchChange, selectedCategory, onCategorySelect }) => {
    return (
      <View style={styles.container}>
        <View style={styles.inputContainer}>
          <Text style={styles.searchIcon}>🔍</Text>
          <TextInput
            style={styles.input}
            placeholder="Search crop (e.g. Wheat, Tomato, Mango)..."
            placeholderTextColor="#94A3B8"
            value={searchQuery}
            onChangeText={onSearchChange}
            clearButtonMode="while-editing"
            autoCorrect={false}
          />
        </View>

        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={styles.categoryList}
        >
          {CATEGORIES.map((cat) => {
            const isSelected =
              cat === "All" ? !selectedCategory : selectedCategory === cat;
            return (
              <Pressable
                key={cat}
                accessibilityRole="button"
                accessibilityLabel={`Filter by ${cat}`}
                style={({ pressed }) => [
                  styles.chip,
                  isSelected && styles.activeChip,
                  pressed && styles.pressedChip,
                ]}
                onPress={() => onCategorySelect(cat === "All" ? "" : cat)}
              >
                <Text
                  style={[
                    styles.chipText,
                    isSelected && styles.activeChipText,
                  ]}
                >
                  {cat}
                </Text>
              </Pressable>
            );
          })}
        </ScrollView>
      </View>
    );
  },
);

SearchBar.displayName = "SearchBar";

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    backgroundColor: "#FFFFFF",
  },
  inputContainer: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 10,
    paddingHorizontal: 12,
    height: 42,
    marginBottom: 10,
  },
  searchIcon: {
    fontSize: 14,
    marginRight: 8,
  },
  input: {
    flex: 1,
    fontSize: 14,
    color: "#0F172A",
    paddingVertical: 0,
  },
  categoryList: {
    paddingRight: 16,
    gap: 8,
  },
  chip: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: "#F1F5F9",
    borderWidth: 1,
    borderColor: "#E2E8F0",
  },
  activeChip: {
    backgroundColor: "#DCFCE7",
    borderColor: "#16A34A",
  },
  pressedChip: {
    opacity: 0.8,
  },
  chipText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#475569",
  },
  activeChipText: {
    color: "#166534",
    fontWeight: "700",
  },
});
