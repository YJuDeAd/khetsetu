import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  Platform,
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

const CATEGORIES = [
  { label: "Cereals", hindi: "अनाज", icon: "🌾" },
  { label: "Vegetables", hindi: "सब्जियां", icon: "🥦" },
  { label: "Fruits", hindi: "फल", icon: "🍎" },
  { label: "Pulses", hindi: "दालें", icon: "🫘" },
  { label: "Oilseeds", hindi: "तिलहन", icon: "🌻" },
];

const UNITS = ["kg", "quintal", "ton", "box"];
const SHELF_LIFE_PRESETS = [7, 14, 30, 90, 180];

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
  const [variety, setVariety] = useState("");
  const [isOrganic, setIsOrganic] = useState(false);
  const [district, setDistrict] = useState("Amritsar");
  const [state, setState] = useState("Punjab");
  const [pincode, setPincode] = useState("143001");
  const [sellerId, setSellerId] = useState(DEFAULT_SELLER_ID);
  const [showAdvancedSellerId, setShowAdvancedSellerId] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{
    type: "success" | "error";
    text: string;
  } | null>(null);

  const parsedQty = parseFloat(quantity) || 0;
  const parsedPrice = parseFloat(pricePerUnit) || 0;
  const estimatedRevenue = (parsedQty * parsedPrice).toLocaleString("en-IN", {
    maximumFractionDigits: 2,
  });

  const handleSubmit = async () => {
    setStatusMessage(null);

    const parsedShelfLife = parseInt(shelfLifeDays, 10);

    if (!cropName.trim()) {
      Alert.alert("Missing Crop Name", "Please enter the crop name.");
      return;
    }
    if (parsedQty <= 0) {
      Alert.alert("Invalid Quantity", "Please enter a valid quantity greater than 0.");
      return;
    }
    if (parsedPrice <= 0) {
      Alert.alert("Invalid Price", "Please enter a valid price per unit.");
      return;
    }
    if (!district.trim() || !state.trim()) {
      Alert.alert("Missing Location", "Please enter farm district and state.");
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
      shelf_life_days: isNaN(parsedShelfLife) || parsedShelfLife <= 0 ? 14 : parsedShelfLife,
      location_pincode: pincode.trim() || "143001",
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
        text: `Successfully published ${cropName}! Your produce is now live in the buyer marketplace.`,
      });
      // Reset form
      setCropName("");
      setQuantity("");
      setPricePerUnit("");
      setVariety("");
      if (onSuccess) onSuccess();
    } catch (error) {
      const msg =
        error instanceof Error ? error.message : "Failed to publish produce listing.";
      setStatusMessage({
        type: "error",
        text: msg,
      });
      Alert.alert("Publish Failed", msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <View style={styles.container}>
      {/* Farmer Identity Badge */}
      <View style={styles.farmerProfileBadge}>
        <View style={styles.farmerAvatar}>
          <Text style={styles.avatarEmoji}>👨‍🌾</Text>
        </View>
        <View style={styles.farmerProfileInfo}>
          <View style={styles.nameRow}>
            <Text style={styles.farmerName}>Ramesh Kumar</Text>
            <View style={styles.verifiedTag}>
              <Text style={styles.verifiedText}>✓ Verified Farmer</Text>
            </View>
          </View>
          <Text style={styles.farmerLocation}>📍 {district}, {state}</Text>
        </View>
      </View>

      {statusMessage ? (
        <View
          style={[
            styles.banner,
            statusMessage.type === "success" ? styles.successBanner : styles.errorBanner,
          ]}
        >
          <Text style={styles.bannerIcon}>
            {statusMessage.type === "success" ? "✅" : "⚠️"}
          </Text>
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

      {/* SECTION 1: CROP DETAILS */}
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>1. Crop Information / फसल का विवरण</Text>

        <Text style={styles.fieldLabel}>Crop Name / फसल का नाम *</Text>
        <TextInput
          style={styles.textInput}
          placeholder="e.g. Sharbati Whole Wheat, Alphonso Mango"
          placeholderTextColor="#94A3B8"
          value={cropName}
          onChangeText={setCropName}
        />

        <Text style={styles.fieldLabel}>Category / श्रेणी</Text>
        <View style={styles.categoryGrid}>
          {CATEGORIES.map((cat) => {
            const isSelected = category === cat.label;
            return (
              <Pressable
                key={cat.label}
                style={[
                  styles.categoryChip,
                  isSelected && styles.categoryChipActive,
                ]}
                onPress={() => setCategory(cat.label)}
              >
                <Text style={styles.categoryIcon}>{cat.icon}</Text>
                <View>
                  <Text
                    style={[
                      styles.categoryLabel,
                      isSelected && styles.categoryLabelActive,
                    ]}
                  >
                    {cat.label}
                  </Text>
                  <Text
                    style={[
                      styles.categorySubLabel,
                      isSelected && styles.categorySubLabelActive,
                    ]}
                  >
                    {cat.hindi}
                  </Text>
                </View>
              </Pressable>
            );
          })}
        </View>

        <Text style={styles.fieldLabel}>Variety or Strain / किस्म (Optional)</Text>
        <TextInput
          style={styles.textInput}
          placeholder="e.g. 1121 Extra Long, Golden Desi, Hybrid-4"
          placeholderTextColor="#94A3B8"
          value={variety}
          onChangeText={setVariety}
        />
      </View>

      {/* SECTION 2: QUANTITY & PRICING */}
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>2. Quantity & Direct Price / मात्रा एवं दर</Text>

        <View style={styles.unitSelectorContainer}>
          <Text style={styles.fieldLabel}>Selling Unit / इकाई</Text>
          <View style={styles.unitPillsRow}>
            {UNITS.map((u) => (
              <Pressable
                key={u}
                style={[styles.unitPill, unit === u && styles.unitPillActive]}
                onPress={() => setUnit(u)}
              >
                <Text
                  style={[
                    styles.unitPillText,
                    unit === u && styles.unitPillTextActive,
                  ]}
                >
                  {u}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        <View style={styles.twoColumnRow}>
          <View style={styles.columnItem}>
            <Text style={styles.fieldLabel}>Total Quantity ({unit}) *</Text>
            <TextInput
              style={styles.textInput}
              placeholder="e.g. 500"
              placeholderTextColor="#94A3B8"
              keyboardType="numeric"
              value={quantity}
              onChangeText={setQuantity}
            />
          </View>
          <View style={styles.columnItem}>
            <Text style={styles.fieldLabel}>Price per {unit} (₹) *</Text>
            <TextInput
              style={styles.textInput}
              placeholder="e.g. 45.00"
              placeholderTextColor="#94A3B8"
              keyboardType="numeric"
              value={pricePerUnit}
              onChangeText={setPricePerUnit}
            />
          </View>
        </View>

        {/* Dynamic Estimated Revenue Card */}
        {parsedQty > 0 && parsedPrice > 0 ? (
          <View style={styles.revenueCard}>
            <View style={styles.revenueHeader}>
              <Text style={styles.revenueLabel}>Total Estimated Value</Text>
              <Text style={styles.zeroCutBadge}>0% Intermediary Fee</Text>
            </View>
            <Text style={styles.revenueAmount}>₹{estimatedRevenue}</Text>
            <Text style={styles.revenueSubtext}>
              100% of payment goes directly to your bank account via escrow upon delivery.
            </Text>
          </View>
        ) : null}

        {/* Shelf Life Selection */}
        <Text style={styles.fieldLabel}>Freshness / Shelf Life (Days)</Text>
        <View style={styles.presetPillsRow}>
          {SHELF_LIFE_PRESETS.map((days) => (
            <Pressable
              key={days}
              style={[
                styles.presetPill,
                shelfLifeDays === String(days) && styles.presetPillActive,
              ]}
              onPress={() => setShelfLifeDays(String(days))}
            >
              <Text
                style={[
                  styles.presetPillText,
                  shelfLifeDays === String(days) && styles.presetPillTextActive,
                ]}
              >
                {days}d
              </Text>
            </Pressable>
          ))}
          <TextInput
            style={[styles.textInput, styles.customDaysInput]}
            placeholder="Custom"
            placeholderTextColor="#94A3B8"
            keyboardType="numeric"
            value={shelfLifeDays}
            onChangeText={setShelfLifeDays}
          />
        </View>
      </View>

      {/* SECTION 3: LOCATION & CERTIFICATION */}
      <View style={styles.sectionCard}>
        <Text style={styles.sectionTitle}>3. Location & Standards / स्थान एवं गुणवत्ता</Text>

        {/* Organic Certification Toggle */}
        <Pressable
          style={[styles.organicToggle, isOrganic && styles.organicToggleActive]}
          onPress={() => setIsOrganic(!isOrganic)}
        >
          <View style={styles.toggleCheckbox}>
            <Text style={styles.toggleCheckIcon}>{isOrganic ? "✓" : ""}</Text>
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.organicToggleTitle}>🌱 Organic Certified Produce</Text>
            <Text style={styles.organicToggleSubtitle}>
              Check if your crop follows certified organic or chemical-free practices.
            </Text>
          </View>
        </Pressable>

        <View style={styles.twoColumnRow}>
          <View style={styles.columnItem}>
            <Text style={styles.fieldLabel}>District / ज़िला *</Text>
            <TextInput
              style={styles.textInput}
              placeholder="e.g. Amritsar"
              placeholderTextColor="#94A3B8"
              value={district}
              onChangeText={setDistrict}
            />
          </View>
          <View style={styles.columnItem}>
            <Text style={styles.fieldLabel}>State / राज्य *</Text>
            <TextInput
              style={styles.textInput}
              placeholder="e.g. Punjab"
              placeholderTextColor="#94A3B8"
              value={state}
              onChangeText={setState}
            />
          </View>
        </View>

        <Text style={styles.fieldLabel}>Pincode / पिन कोड</Text>
        <TextInput
          style={styles.textInput}
          placeholder="e.g. 143001"
          placeholderTextColor="#94A3B8"
          keyboardType="numeric"
          value={pincode}
          onChangeText={setPincode}
        />
      </View>

      {/* Advanced / Developer Settings Accordion */}
      <Pressable
        style={styles.advancedToggle}
        onPress={() => setShowAdvancedSellerId(!showAdvancedSellerId)}
      >
        <Text style={styles.advancedToggleText}>
          {showAdvancedSellerId ? "▼ Hide Advanced Config" : "▶ Advanced Seller Config"}
        </Text>
      </Pressable>

      {showAdvancedSellerId ? (
        <View style={styles.advancedBox}>
          <Text style={styles.fieldLabel}>Seller ID (UUID)</Text>
          <TextInput
            style={[styles.textInput, styles.monospaceInput]}
            placeholder="Seller UUID"
            placeholderTextColor="#94A3B8"
            value={sellerId}
            onChangeText={setSellerId}
            autoCapitalize="none"
          />
        </View>
      ) : null}

      {/* PUBLISH SUBMIT BUTTON */}
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Publish Produce Listing"
        disabled={submitting}
        style={({ pressed }) => [
          styles.publishButton,
          submitting && styles.publishButtonDisabled,
          pressed && styles.publishButtonPressed,
        ]}
        onPress={handleSubmit}
      >
        {submitting ? (
          <ActivityIndicator color="#FFFFFF" size="small" />
        ) : (
          <View style={styles.buttonContent}>
            <Text style={styles.publishButtonText}>
              Publish Produce Listing
            </Text>
            <Text style={styles.publishButtonSubtext}>
              फसल मंडी में प्रकाशित करें →
            </Text>
          </View>
        )}
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 16,
    paddingBottom: 32,
  },
  farmerProfileBadge: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#FFFFFF",
    padding: 14,
    borderRadius: 14,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    shadowColor: "#0F172A",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
    elevation: 1,
  },
  farmerAvatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: "#DCFCE7",
    justifyContent: "center",
    alignItems: "center",
    marginRight: 12,
  },
  avatarEmoji: {
    fontSize: 22,
  },
  farmerProfileInfo: {
    flex: 1,
  },
  nameRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  farmerName: {
    fontSize: 16,
    fontWeight: "700",
    color: "#0F172A",
  },
  verifiedTag: {
    backgroundColor: "#DCFCE7",
    paddingHorizontal: 8,
    paddingVertical: 2,
    borderRadius: 6,
  },
  verifiedText: {
    fontSize: 10,
    fontWeight: "700",
    color: "#166534",
  },
  farmerLocation: {
    fontSize: 12,
    color: "#64748B",
    marginTop: 2,
  },
  sectionCard: {
    backgroundColor: "#FFFFFF",
    borderRadius: 14,
    padding: 16,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#E2E8F0",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.04,
    shadowRadius: 3,
    elevation: 1,
  },
  sectionTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#166534",
    marginBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9",
    paddingBottom: 8,
  },
  fieldLabel: {
    fontSize: 12,
    fontWeight: "600",
    color: "#334155",
    marginBottom: 6,
    marginTop: 4,
  },
  textInput: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 10,
    fontSize: 14,
    color: "#0F172A",
    marginBottom: 12,
  },
  categoryGrid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 12,
  },
  categoryChip: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    minWidth: "45%",
    flexGrow: 1,
    gap: 8,
  },
  categoryChipActive: {
    backgroundColor: "#F0FDF4",
    borderColor: "#16A34A",
  },
  categoryIcon: {
    fontSize: 18,
  },
  categoryLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: "#334155",
  },
  categoryLabelActive: {
    color: "#166534",
    fontWeight: "700",
  },
  categorySubLabel: {
    fontSize: 10,
    color: "#94A3B8",
  },
  categorySubLabelActive: {
    color: "#15803D",
  },
  unitSelectorContainer: {
    marginBottom: 12,
  },
  unitPillsRow: {
    flexDirection: "row",
    gap: 8,
    marginTop: 4,
  },
  unitPill: {
    flex: 1,
    paddingVertical: 10,
    alignItems: "center",
    borderRadius: 8,
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
  },
  unitPillActive: {
    backgroundColor: "#166534",
    borderColor: "#166534",
  },
  unitPillText: {
    fontSize: 13,
    fontWeight: "600",
    color: "#475569",
  },
  unitPillTextActive: {
    color: "#FFFFFF",
    fontWeight: "700",
  },
  twoColumnRow: {
    flexDirection: "row",
    gap: 12,
  },
  columnItem: {
    flex: 1,
  },
  revenueCard: {
    backgroundColor: "#F0FDF4",
    borderWidth: 1,
    borderColor: "#BBF7D0",
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
  },
  revenueHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  revenueLabel: {
    fontSize: 11,
    fontWeight: "600",
    color: "#166534",
    textTransform: "uppercase",
  },
  zeroCutBadge: {
    backgroundColor: "#DCFCE7",
    color: "#15803D",
    fontSize: 10,
    fontWeight: "700",
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
  },
  revenueAmount: {
    fontSize: 24,
    fontWeight: "800",
    color: "#15803D",
    marginTop: 4,
    marginBottom: 4,
  },
  revenueSubtext: {
    fontSize: 11,
    color: "#475569",
    lineHeight: 16,
  },
  presetPillsRow: {
    flexDirection: "row",
    gap: 6,
    alignItems: "center",
    marginBottom: 4,
  },
  presetPill: {
    paddingHorizontal: 10,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: "#F1F5F9",
    borderWidth: 1,
    borderColor: "#E2E8F0",
  },
  presetPillActive: {
    backgroundColor: "#166534",
    borderColor: "#166534",
  },
  presetPillText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#475569",
  },
  presetPillTextActive: {
    color: "#FFFFFF",
  },
  customDaysInput: {
    flex: 1,
    marginBottom: 0,
    paddingVertical: 7,
    textAlign: "center",
  },
  organicToggle: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#E2E8F0",
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
    gap: 12,
  },
  organicToggleActive: {
    backgroundColor: "#F0FDF4",
    borderColor: "#16A34A",
  },
  toggleCheckbox: {
    width: 24,
    height: 24,
    borderRadius: 6,
    borderWidth: 1.5,
    borderColor: "#16A34A",
    backgroundColor: "#FFFFFF",
    justifyContent: "center",
    alignItems: "center",
  },
  toggleCheckIcon: {
    fontSize: 14,
    fontWeight: "800",
    color: "#16A34A",
  },
  organicToggleTitle: {
    fontSize: 14,
    fontWeight: "700",
    color: "#1E293B",
  },
  organicToggleSubtitle: {
    fontSize: 11,
    color: "#64748B",
    marginTop: 2,
    lineHeight: 15,
  },
  advancedToggle: {
    paddingVertical: 8,
    marginBottom: 8,
  },
  advancedToggleText: {
    fontSize: 12,
    color: "#64748B",
    fontWeight: "600",
  },
  advancedBox: {
    backgroundColor: "#F8FAFC",
    padding: 12,
    borderRadius: 10,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0",
  },
  monospaceInput: {
    fontSize: 11,
    fontFamily: Platform.OS === "ios" ? "Courier" : "monospace",
  },
  publishButton: {
    backgroundColor: "#16A34A",
    borderRadius: 12,
    paddingVertical: 14,
    alignItems: "center",
    marginTop: 6,
    shadowColor: "#16A34A",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 3,
  },
  publishButtonPressed: {
    backgroundColor: "#15803D",
  },
  publishButtonDisabled: {
    backgroundColor: "#86EFAC",
  },
  buttonContent: {
    alignItems: "center",
  },
  publishButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
  publishButtonSubtext: {
    color: "#DCFCE7",
    fontSize: 12,
    marginTop: 2,
  },
  banner: {
    flexDirection: "row",
    alignItems: "center",
    padding: 12,
    borderRadius: 10,
    marginBottom: 16,
    gap: 8,
  },
  bannerIcon: {
    fontSize: 18,
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
    flex: 1,
  },
  successBannerText: {
    color: "#166534",
    fontWeight: "600",
  },
  errorBannerText: {
    color: "#991B1B",
    fontWeight: "600",
  },
});
