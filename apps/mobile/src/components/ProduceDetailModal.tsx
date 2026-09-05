import React, { useState } from "react";
import {
  ActivityIndicator,
  Alert,
  KeyboardAvoidingView,
  Modal,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { createOrder } from "../services/api";
import { ProduceListing } from "../types/produce";

interface ProduceDetailModalProps {
  listing: ProduceListing | null;
  visible: boolean;
  onClose: () => void;
  onOrderSuccess?: () => void;
}

// Default demo buyer ID
const DEFAULT_BUYER_ID = "00000000-0000-0000-0000-000000000002";

export const ProduceDetailModal: React.FC<ProduceDetailModalProps> = ({
  listing,
  visible,
  onClose,
  onOrderSuccess,
}) => {
  const [orderQuantity, setOrderQuantity] = useState("");
  const [deliveryStreet, setDeliveryStreet] = useState("10 Mandi Road");
  const [deliveryCity, setDeliveryCity] = useState("Amritsar");
  const [deliveryPincode, setDeliveryPincode] = useState("143001");
  const [submitting, setSubmitting] = useState(false);
  const [orderSuccessId, setOrderSuccessId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  if (!listing) return null;

  const unitPrice = parseFloat(String(listing.price_per_unit)) || 0;
  const availableQty = parseFloat(String(listing.quantity)) || 0;
  const parsedOrderQty = parseFloat(orderQuantity) || 0;
  const calculatedTotal = (parsedOrderQty * unitPrice).toFixed(2);

  const isOrganic = listing.attributes?.organic_certified;
  const variety = listing.attributes?.variety;
  const grade = listing.attributes?.grade;

  const handleClose = () => {
    setOrderQuantity("");
    setOrderSuccessId(null);
    setErrorMessage(null);
    onClose();
  };

  const handlePlaceOrder = async () => {
    setErrorMessage(null);

    if (parsedOrderQty <= 0) {
      Alert.alert("Validation Error", "Please enter a valid quantity greater than 0.");
      return;
    }

    if (parsedOrderQty > availableQty) {
      Alert.alert(
        "Insufficient Inventory",
        `Only ${availableQty} ${listing.unit} is available.`,
      );
      return;
    }

    setSubmitting(true);
    try {
      const order = await createOrder({
        buyer_id: DEFAULT_BUYER_ID,
        listing_id: listing.id,
        quantity: parsedOrderQty,
        delivery_address: {
          street: deliveryStreet,
          city: deliveryCity,
          pincode: deliveryPincode,
          district: listing.location_district,
          state: listing.location_state,
        },
      });

      setOrderSuccessId(order.id);
      if (onOrderSuccess) onOrderSuccess();
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Failed to place order";
      setErrorMessage(msg);
      Alert.alert("Order Failed", msg);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Modal
      animationType="slide"
      transparent={true}
      visible={visible}
      onRequestClose={handleClose}
    >
      <KeyboardAvoidingView
        style={styles.modalOverlay}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View style={styles.modalContent}>
          {/* Modal Header */}
          <View style={styles.modalHeader}>
            <View style={{ flex: 1 }}>
              <Text style={styles.cropTitle}>{listing.crop_name}</Text>
              <Text style={styles.cropCategory}>{listing.crop_category}</Text>
            </View>
            <Pressable
              onPress={handleClose}
              style={styles.closeButton}
              accessibilityLabel="Close"
            >
              <Text style={styles.closeButtonText}>✕</Text>
            </Pressable>
          </View>

          <ScrollView style={styles.scrollBody} keyboardShouldPersistTaps="handled">
            {/* Price & Quantity Banner */}
            <View style={styles.pricingBanner}>
              <View>
                <Text style={styles.priceLabel}>Farmer Price</Text>
                <Text style={styles.priceValue}>
                  ₹{listing.price_per_unit}{" "}
                  <Text style={styles.unitText}>/ {listing.unit}</Text>
                </Text>
              </View>
              <View style={{ alignItems: "flex-end" }}>
                <Text style={styles.stockLabel}>Stock Available</Text>
                <Text style={styles.stockValue}>
                  {listing.quantity} {listing.unit}
                </Text>
              </View>
            </View>

            {/* Quality & Specifications */}
            <View style={styles.specSection}>
              <Text style={styles.sectionHeader}>Produce Specifications</Text>
              <View style={styles.badgeRow}>
                {isOrganic ? (
                  <View style={styles.organicBadge}>
                    <Text style={styles.organicText}>🌱 Organic Certified</Text>
                  </View>
                ) : null}
                {variety ? (
                  <View style={styles.attrBadge}>
                    <Text style={styles.attrText}>Variety: {String(variety)}</Text>
                  </View>
                ) : null}
                {grade ? (
                  <View style={styles.gradeBadge}>
                    <Text style={styles.gradeText}>Grade: {String(grade)}</Text>
                  </View>
                ) : null}
              </View>

              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>📍 Location:</Text>
                <Text style={styles.metaValue}>
                  {listing.location_district}, {listing.location_state} ({listing.location_pincode})
                </Text>
              </View>
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>⏱️ Shelf Life:</Text>
                <Text style={styles.metaValue}>{listing.shelf_life_days} days freshness</Text>
              </View>
              <View style={styles.metaRow}>
                <Text style={styles.metaLabel}>📅 Harvest Date:</Text>
                <Text style={styles.metaValue}>{listing.harvest_date}</Text>
              </View>
            </View>

            {/* Escrow Guarantee Trust Banner */}
            <View style={styles.escrowTrustBox}>
              <Text style={styles.escrowTrustTitle}>🔒 KhetSetu Escrow Protection</Text>
              <Text style={styles.escrowTrustDesc}>
                Your payment is safely held in escrow. Payout is only released to the farmer after you inspect and verify delivery.
              </Text>
            </View>

            {/* Order Form or Order Placed Confirmation */}
            {orderSuccessId ? (
              <View style={styles.successContainer}>
                <Text style={styles.successEmoji}>🎉</Text>
                <Text style={styles.successTitle}>Order Successfully Initiated!</Text>
                <Text style={styles.successOrderId}>Order ID: {orderSuccessId}</Text>
                <Text style={styles.successSubtext}>
                  {orderQuantity} {listing.unit} of {listing.crop_name} reserved. Status is now INITIATED.
                </Text>
                <Pressable style={styles.doneButton} onPress={handleClose}>
                  <Text style={styles.doneButtonText}>Back to Marketplace</Text>
                </Pressable>
              </View>
            ) : (
              <View style={styles.orderFormContainer}>
                <Text style={styles.sectionHeader}>Place Escrow Order</Text>

                {errorMessage ? (
                  <View style={styles.errorBox}>
                    <Text style={styles.errorBoxText}>{errorMessage}</Text>
                  </View>
                ) : null}

                <Text style={styles.inputLabel}>Quantity to Purchase ({listing.unit}) *</Text>
                <TextInput
                  style={styles.textInput}
                  placeholder={`e.g. 50 (max ${availableQty})`}
                  keyboardType="numeric"
                  value={orderQuantity}
                  onChangeText={setOrderQuantity}
                />

                {parsedOrderQty > 0 ? (
                  <View style={styles.totalPreview}>
                    <Text style={styles.totalLabel}>Total Payable Amount:</Text>
                    <Text style={styles.totalAmount}>₹{calculatedTotal}</Text>
                  </View>
                ) : null}

                <Text style={styles.inputLabel}>Delivery Street Address</Text>
                <TextInput
                  style={styles.textInput}
                  placeholder="e.g. 10 Mandi Road"
                  value={deliveryStreet}
                  onChangeText={setDeliveryStreet}
                />

                <View style={styles.rowInputs}>
                  <View style={{ flex: 1, marginRight: 8 }}>
                    <Text style={styles.inputLabel}>City</Text>
                    <TextInput
                      style={styles.textInput}
                      placeholder="e.g. Amritsar"
                      value={deliveryCity}
                      onChangeText={setDeliveryCity}
                    />
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={styles.inputLabel}>Pincode</Text>
                    <TextInput
                      style={styles.textInput}
                      placeholder="143001"
                      keyboardType="numeric"
                      value={deliveryPincode}
                      onChangeText={setDeliveryPincode}
                    />
                  </View>
                </View>

                <Pressable
                  style={[styles.placeOrderBtn, submitting && styles.btnDisabled]}
                  onPress={handlePlaceOrder}
                  disabled={submitting}
                >
                  {submitting ? (
                    <ActivityIndicator color="#FFFFFF" />
                  ) : (
                    <Text style={styles.placeOrderBtnText}>
                      Initiate Order {parsedOrderQty > 0 ? `(₹${calculatedTotal})` : ""}
                    </Text>
                  )}
                </Pressable>
              </View>
            )}
          </ScrollView>
        </View>
      </KeyboardAvoidingView>
    </Modal>
  );
};

const styles = StyleSheet.create({
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(15, 23, 42, 0.6)",
    justifyContent: "flex-end",
  },
  modalContent: {
    backgroundColor: "#FFFFFF",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    maxHeight: "90%",
    paddingBottom: 24,
  },
  modalHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 20,
    paddingTop: 18,
    paddingBottom: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#F1F5F9",
  },
  cropTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#0F172A",
  },
  cropCategory: {
    fontSize: 13,
    color: "#64748B",
    fontWeight: "500",
    marginTop: 2,
  },
  closeButton: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: "#F1F5F9",
    justifyContent: "center",
    alignItems: "center",
  },
  closeButtonText: {
    fontSize: 16,
    color: "#64748B",
    fontWeight: "700",
  },
  scrollBody: {
    paddingHorizontal: 20,
    paddingTop: 14,
  },
  pricingBanner: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#F0FDF4",
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#DCFCE7",
    marginBottom: 16,
  },
  priceLabel: {
    fontSize: 11,
    color: "#166534",
    fontWeight: "600",
    textTransform: "uppercase",
  },
  priceValue: {
    fontSize: 22,
    fontWeight: "800",
    color: "#15803D",
    marginTop: 2,
  },
  unitText: {
    fontSize: 13,
    fontWeight: "500",
    color: "#4B5563",
  },
  stockLabel: {
    fontSize: 11,
    color: "#166534",
    fontWeight: "600",
    textTransform: "uppercase",
  },
  stockValue: {
    fontSize: 17,
    fontWeight: "700",
    color: "#1E293B",
    marginTop: 2,
  },
  specSection: {
    backgroundColor: "#F8FAFC",
    padding: 14,
    borderRadius: 12,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: "#E2E8F0",
  },
  sectionHeader: {
    fontSize: 15,
    fontWeight: "700",
    color: "#1E293B",
    marginBottom: 10,
  },
  badgeRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 6,
    marginBottom: 10,
  },
  organicBadge: {
    backgroundColor: "#DCFCE7",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  organicText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#15803D",
  },
  attrBadge: {
    backgroundColor: "#E2E8F0",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  attrText: {
    fontSize: 12,
    fontWeight: "500",
    color: "#334155",
  },
  gradeBadge: {
    backgroundColor: "#FEF3C7",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  gradeText: {
    fontSize: 12,
    fontWeight: "600",
    color: "#B45309",
  },
  metaRow: {
    flexDirection: "row",
    marginTop: 6,
  },
  metaLabel: {
    fontSize: 13,
    color: "#64748B",
    width: 110,
    fontWeight: "500",
  },
  metaValue: {
    fontSize: 13,
    color: "#1E293B",
    flex: 1,
    fontWeight: "600",
  },
  escrowTrustBox: {
    backgroundColor: "#EFF6FF",
    padding: 14,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#BFDBFE",
    marginBottom: 18,
  },
  escrowTrustTitle: {
    fontSize: 13,
    fontWeight: "700",
    color: "#1E40AF",
    marginBottom: 4,
  },
  escrowTrustDesc: {
    fontSize: 12,
    color: "#334155",
    lineHeight: 17,
  },
  orderFormContainer: {
    marginBottom: 24,
  },
  inputLabel: {
    fontSize: 13,
    fontWeight: "600",
    color: "#334155",
    marginBottom: 6,
    marginTop: 8,
  },
  textInput: {
    backgroundColor: "#F8FAFC",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 15,
    color: "#0F172A",
  },
  rowInputs: {
    flexDirection: "row",
  },
  totalPreview: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    backgroundColor: "#FEF9C3",
    padding: 12,
    borderRadius: 8,
    marginTop: 12,
    marginBottom: 4,
  },
  totalLabel: {
    fontSize: 14,
    fontWeight: "600",
    color: "#854D0E",
  },
  totalAmount: {
    fontSize: 18,
    fontWeight: "800",
    color: "#854D0E",
  },
  placeOrderBtn: {
    backgroundColor: "#166534",
    paddingVertical: 14,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 18,
  },
  btnDisabled: {
    opacity: 0.6,
  },
  placeOrderBtnText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
  errorBox: {
    backgroundColor: "#FEE2E2",
    padding: 10,
    borderRadius: 8,
    marginBottom: 10,
  },
  errorBoxText: {
    color: "#DC2626",
    fontSize: 13,
    fontWeight: "600",
  },
  successContainer: {
    alignItems: "center",
    paddingVertical: 24,
  },
  successEmoji: {
    fontSize: 48,
    marginBottom: 8,
  },
  successTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#166534",
    marginBottom: 6,
  },
  successOrderId: {
    fontSize: 12,
    color: "#64748B",
    marginBottom: 8,
  },
  successSubtext: {
    fontSize: 13,
    color: "#334155",
    textAlign: "center",
    lineHeight: 18,
    marginBottom: 20,
  },
  doneButton: {
    backgroundColor: "#166534",
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  doneButtonText: {
    color: "#FFFFFF",
    fontWeight: "700",
    fontSize: 15,
  },
});
