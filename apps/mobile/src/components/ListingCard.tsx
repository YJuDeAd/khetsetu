import React from "react";
import { StyleSheet, Text, View, Pressable } from "react-native";
import { ProduceListing } from "../types/produce";

interface ListingCardProps {
  listing: ProduceListing;
  onPress?: (listing: ProduceListing) => void;
}

export const ListingCard: React.FC<ListingCardProps> = React.memo(
  ({ listing, onPress }) => {
    const handlePress = () => {
      if (onPress) onPress(listing);
    };

    const isOrganic = listing.attributes?.organic_certified;
    const variety = listing.attributes?.variety;
    const grade = listing.attributes?.grade;

    return (
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`${listing.crop_name}, ₹${listing.price_per_unit} per ${listing.unit}`}
        style={({ pressed }) => [styles.card, pressed && styles.cardPressed]}
        onPress={handlePress}
      >
        <View style={styles.headerRow}>
          <View style={styles.titleColumn}>
            <Text style={styles.cropName}>{listing.crop_name}</Text>
            <Text style={styles.category}>{listing.crop_category}</Text>
          </View>
          <View style={styles.priceColumn}>
            <Text style={styles.price}>₹{listing.price_per_unit}</Text>
            <Text style={styles.unit}>per {listing.unit}</Text>
          </View>
        </View>

        <View style={styles.badgeRow}>
          {isOrganic ? (
            <View style={styles.organicBadge}>
              <Text style={styles.organicText}>🌱 Organic Certified</Text>
            </View>
          ) : null}
          {variety ? (
            <View style={styles.attributeBadge}>
              <Text style={styles.attributeText}>{String(variety)}</Text>
            </View>
          ) : null}
          {grade ? (
            <View style={styles.gradeBadge}>
              <Text style={styles.gradeText}>Grade {String(grade)}</Text>
            </View>
          ) : null}
        </View>

        <View style={styles.divider} />

        <View style={styles.footerRow}>
          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Available</Text>
            <Text style={styles.infoValue}>
              {listing.quantity} {listing.unit}
            </Text>
          </View>

          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Location</Text>
            <Text style={styles.infoValue} numberOfLines={1}>
              📍 {listing.location_district}, {listing.location_state}
            </Text>
          </View>

          <View style={styles.infoItem}>
            <Text style={styles.infoLabel}>Freshness</Text>
            <Text style={styles.infoValue}>
              ⏱️ {listing.shelf_life_days}d
            </Text>
          </View>
        </View>
      </Pressable>
    );
  },
);

ListingCard.displayName = "ListingCard";

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 16,
    marginHorizontal: 16,
    marginVertical: 6,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardPressed: {
    backgroundColor: "#F8FAFC",
    borderColor: "#CBD5E1",
  },
  headerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  titleColumn: {
    flex: 1,
    marginRight: 8,
  },
  cropName: {
    fontSize: 17,
    fontWeight: "700",
    color: "#0F172A",
    marginBottom: 2,
  },
  category: {
    fontSize: 12,
    fontWeight: "500",
    color: "#64748B",
  },
  priceColumn: {
    alignItems: "flex-end",
  },
  price: {
    fontSize: 18,
    fontWeight: "800",
    color: "#166534",
  },
  unit: {
    fontSize: 11,
    fontWeight: "500",
    color: "#64748B",
  },
  badgeRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginTop: 8,
  },
  organicBadge: {
    backgroundColor: "#DCFCE7",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  organicText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#15803D",
  },
  attributeBadge: {
    backgroundColor: "#F1F5F9",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  attributeText: {
    fontSize: 11,
    fontWeight: "500",
    color: "#475569",
  },
  gradeBadge: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  gradeText: {
    fontSize: 11,
    fontWeight: "600",
    color: "#B45309",
  },
  divider: {
    height: 1,
    backgroundColor: "#F1F5F9",
    marginVertical: 12,
  },
  footerRow: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  infoItem: {
    flex: 1,
  },
  infoLabel: {
    fontSize: 10,
    fontWeight: "500",
    color: "#94A3B8",
    textTransform: "uppercase",
    marginBottom: 2,
  },
  infoValue: {
    fontSize: 12,
    fontWeight: "600",
    color: "#334155",
  },
});
