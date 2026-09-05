import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { createProduceListing } from "../services/api";
import { ProduceCreatePayload } from "../types/produce";

interface FarmerListingFormProps {
  onSuccess?: () => void;
}

const CATEGORIES = ["Cereals", "Vegetables", "Fruits", "Pulses", "Oilseeds"];
const UNITS = ["kg", "quintal", "ton", "box"];
// Default mock farmer seller ID for demo / prototype
const DEFAULT_SELLER_ID = "00000000-0000-0000-0000-000000000001";

export const FarmerListingForm: React.FC<FarmerListingFormProps> = ({
  onSuccess,
}) => {
  const [cropName, setCropName] = useState("");
  const [category, setCategory] = useState("Cereals");
  const [quantity, setQuantity] = useState("");
  const [unit, setUnit] = useState("kg");
  const [pricePerUnit, setPricePerUnit] = useState("");
  const [shelfLifeDays, setShelfLifeDays] = useState("30");
  const [pincode, setPincode] = useState("141001");
  const [district, setDistrict] = useState("Ludhiana");
  const [state, setState] = useState("Punjab");
  const [variety, setVariety] = useState("");
  const [isOrganic, setIsOrganic] = useState(false);
  const [sellerId, setSellerId] = useState(DEFAULT_SELLER_ID);

  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const handleSubmit = async () => {
    setStatusMessage(null);

    const parsedQty = parseFloat(quantity);
    const parsedPrice = parseFloat(pricePerUnit);
    const parsedShelfLife = parseInt(shelfLifeDays, 10);

    if (!cropName.trim()) {
      Alert.alert("Validation Error", "Please enter a crop name.");
      return;
    }
    if (isNaN(parsedQty) || parsedQty <= 0) {
      Alert.alert(
        "Validation Error",
        "Please enter a valid quantity greater than 0.",
      );
      return;
    }
    if (isNaN(parsedPrice) || parsedPrice <= 0) {
      Alert.alert(
        "Validation Error",
        "Please enter a valid price per unit greater than 0.",
      );
      return;
    }

    const payload: ProduceCreatePayload = {
      seller_id: sellerId.trim() || DEFAULT_SELLER_ID,
      crop_name: cropName.trim(),
      crop_category: category,
      quantity: parsedQty,
      unit,
      price_per_unit: parsedPrice,
      harvest_date: new Date().toISOString().split("T")[0],
      shelf_life_days: isNaN(parsedShelfLife) ? 7 : parsedShelfLife,
      location_pincode: pincode.trim(),
      location_district: district.trim(),
      location_state: state.trim(),
      attributes: {
        variety: variety.trim() || undefined,
        organic_certified: isOrganic,
      },
    };

    setSubmitting(true);
    try {
      await createProduceListing(payload);
      setStatusMessage({
        type: "success",
        text: `Successfully listed ${cropName}! Your produce is now live in the marketplace.`,
      });
      // Reset form
      setCropName("");
      setQuantity("");
      setPricePerUnit("");
      setVariety("");
      if (onSuccess) onSuccess();
    } catch (error) {
      setStatusMessage({
        type: "error",
        text:
          error instanceof Error
            ? error.message
            : "Failed to publish produce listing.",
      });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.sectionHeader}>List Your Harvest / अपनी फसल जोड़ें</Text>

      {statusMessage ? (
        <View
          style={[
            styles.banner,
            statusMessage.type === "success"
              ? styles.successBanner
              : styles.errorBanner,
          ]}
        >
          <Text
            style={[
              styles.bannerText,
              statusMessage.type === "success"
                ? styles.successBannerText
                : styles.errorBannerText,
            ]}
          >
            {statusMessage.text}
          </Text>
        </View>
      ) : null}

      <Text style={styles.label}>Crop Name / फसल का नाम *</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g. Sharbati Wheat, Alphonso Mango"
        placeholderTextColor="#94A3B8"
        value={cropName}
        onChangeText={setCropName}
      />

      <Text style={styles.label}>Crop Category / श्रेणी</Text>
      <View style={styles.optionsRow}>
        {CATEGORIES.map((cat) => (
          <Pressable
            key={cat}
            accessibilityRole="button"
            accessibilityLabel={`Select category ${cat}`}
            style={({ pressed }) => [
              styles.optionChip,
              category === cat && styles.activeOptionChip,
              pressed && styles.pressedChip,
            ]}
            onPress={() => setCategory(cat)}
          >
            <Text
              style={[
                styles.optionChipText,
                category === cat && styles.activeOptionChipText,
              ]}
            >
              {cat}
            </Text>
          </Pressable>
        ))}
      </View>

      <View style={styles.row}>
        <View style={styles.halfColumn}>
          <Text style={styles.label}>Quantity / मात्रा *</Text>
          <TextInput
            style={styles.input}
            placeholder="1000"
            placeholderTextColor="#94A3B8"
            keyboardType="numeric"
            value={quantity}
            onChangeText={setQuantity}
          />
        </View>

        <View style={styles.halfColumn}>
          <Text style={styles.label}>Unit / इकाई</Text>
          <View style={styles.unitRow}>
            {UNITS.map((u) => (
              <Pressable
                key={u}
                accessibilityRole="button"
                accessibilityLabel={`Unit ${u}`}
                style={({ pressed }) => [
                  styles.unitChip,
                  unit === u && styles.activeUnitChip,
                  pressed && styles.pressedChip,
                ]}
                onPress={() => setUnit(u)}
              >
                <Text
                  style={[
                    styles.unitChipText,
                    unit === u && styles.activeUnitChipText,
                  ]}
                >
                  {u}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>
      </View>

      <View style={styles.row}>
        <View style={styles.halfColumn}>
          <Text style={styles.label}>Price per {unit} (₹) *</Text>
          <TextInput
            style={styles.input}
            placeholder="35.00"
            placeholderTextColor="#94A3B8"
            keyboardType="numeric"
            value={pricePerUnit}
            onChangeText={setPricePerUnit}
          />
        </View>

        <View style={styles.halfColumn}>
          <Text style={styles.label}>Shelf Life (Days)</Text>
          <TextInput
            style={styles.input}
            placeholder="30"
            placeholderTextColor="#94A3B8"
            keyboardType="numeric"
            value={shelfLifeDays}
            onChangeText={setShelfLifeDays}
          />
        </View>
      </View>

      <Text style={styles.label}>Variety / किस्म (Optional)</Text>
      <TextInput
        style={styles.input}
        placeholder="e.g. Sharbati, Desi, Hybrid"
        placeholderTextColor="#94A3B8"
        value={variety}
        onChangeText={setVariety}
      />

      <Pressable
        accessibilityRole="checkbox"
        accessibilityState={{ checked: isOrganic }}
        style={({ pressed }) => [
          styles.organicCheckbox,
          pressed && styles.pressedChip,
        ]}
        onPress={() => setIsOrganic(!isOrganic)}
      >
        <Text style={styles.checkboxIcon}>{isOrganic ? "☑️" : "⬜"}</Text>
        <Text style={styles.checkboxLabel}>Organic Certified / जैविक प्रमाणित</Text>
      </Pressable>

      <Text style={styles.label}>Farm Location (District, State, Pincode)</Text>
      <View style={styles.locationRow}>
        <TextInput
          style={[styles.input, styles.locationInput]}
          placeholder="District"
          placeholderTextColor="#94A3B8"
          value={district}
          onChangeText={setDistrict}
        />
        <TextInput
          style={[styles.input, styles.locationInput]}
          placeholder="State"
          placeholderTextColor="#94A3B8"
          value={state}
          onChangeText={setState}
        />
        <TextInput
          style={[styles.input, styles.pincodeInput]}
          placeholder="Pincode"
          placeholderTextColor="#94A3B8"
          keyboardType="numeric"
          value={pincode}
          onChangeText={setPincode}
        />
      </View>

      <Text style={styles.label}>Seller ID (Farmer UUID)</Text>
      <TextInput
        style={styles.input}
        placeholder="Seller UUID"
        placeholderTextColor="#94A3B8"
        value={sellerId}
        onChangeText={setSellerId}
        autoCapitalize="none"
      />

      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Submit Produce Listing"
        disabled={submitting}
        style={({ pressed }) => [
          styles.submitButton,
          submitting && styles.submitButtonDisabled,
          pressed && styles.submitButtonPressed,
        ]}
        onPress={handleSubmit}
      >
        {submitting ? (
          <ActivityIndicator color="#FFFFFF" />
        ) : (
          <Text style={styles.submitButtonText}>
            🚀 Publish Produce Listing / फसल प्रकाशित करें
          </Text>
        )}
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: "#FFFFFF",
    borderRadius: 16,
    padding: 20,
    marginHorizontal: 16,
    marginVertical: 12,
    borderWidth: 1,
    borderColor: "#E2E8F0",
  },
  sectionHeader: {
    fontSize: 18,
    fontWeight: "700",
    color: "#166534",
    marginBottom: 16,
  },
  banner: {
    padding: 12,
    borderRadius: 10,
    marginBottom: 16,
  },
  successBanner: {
    backgroundColor: "#DCFCE7",
    borderWidth: 1,
    borderColor: "#86EFAC",
  },
  errorBanner: {
    backgroundColor: "#FEE2E2",
    borderWidth: 1,
    borderColor: "#FCA5A5",
  },
  bannerText: {
    fontSize: 13,
    lineHeight: 18,
  },
  successBannerText: {
    color: "#166534",
    fontWeight: "600",
  },
  errorBannerText: {
    color: "#991B1B",
    fontWeight: "600",
  },
  label: {
    fontSize: 12,
    fontWeight: "600",
    color: "#334155",
    marginBottom: 6,
    marginTop: 4,
  },
  input: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 14,
    color: "#0F172A",
    marginBottom: 12,
  },
  optionsRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 12,
  },
  optionChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: "#F1F5F9",
    borderWidth: 1,
    borderColor: "#CBD5E1",
  },
  activeOptionChip: {
    backgroundColor: "#DCFCE7",
    borderColor: "#16A34A",
  },
  optionChipText: {
    fontSize: 12,
    color: "#475569",
    fontWeight: "500",
  },
  activeOptionChipText: {
    color: "#166534",
    fontWeight: "700",
  },
  row: {
    flexDirection: "row",
    gap: 12,
  },
  halfColumn: {
    flex: 1,
  },
  unitRow: {
    flexDirection: "row",
    gap: 4,
  },
  unitChip: {
    flex: 1,
    paddingVertical: 10,
    alignItems: "center",
    borderRadius: 8,
    backgroundColor: "#F1F5F9",
    borderWidth: 1,
    borderColor: "#CBD5E1",
  },
  activeUnitChip: {
    backgroundColor: "#16A34A",
    borderColor: "#16A34A",
  },
  unitChipText: {
    fontSize: 12,
    color: "#475569",
    fontWeight: "600",
  },
  activeUnitChipText: {
    color: "#FFFFFF",
    fontWeight: "700",
  },
  organicCheckbox: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: 16,
    marginTop: 4,
  },
  checkboxIcon: {
    fontSize: 18,
    marginRight: 8,
  },
  checkboxLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: "#15803D",
  },
  locationRow: {
    flexDirection: "row",
    gap: 8,
    marginBottom: 4,
  },
  locationInput: {
    flex: 2,
  },
  pincodeInput: {
    flex: 1.5,
  },
  pressedChip: {
    opacity: 0.8,
  },
  submitButton: {
    backgroundColor: "#16A34A",
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 10,
  },
  submitButtonPressed: {
    backgroundColor: "#15803D",
  },
  submitButtonDisabled: {
    backgroundColor: "#86EFAC",
  },
  submitButtonText: {
    color: "#FFFFFF",
    fontSize: 15,
    fontWeight: "700",
  },
});
