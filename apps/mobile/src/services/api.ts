import { Platform } from "react-native";
import {
  ListingFilterParams,
  ProduceCreatePayload,
  ProduceListing,
} from "../types/produce";

// Android emulator routes localhost to 10.0.2.2; iOS and physical devices on LAN use host IP/localhost
const DEFAULT_HOST = Platform.OS === "android" ? "10.0.2.2" : "localhost";
export const API_BASE_URL = `http://${DEFAULT_HOST}:8000/api/v1`;

export async function fetchListings(
  filters: ListingFilterParams = {},
): Promise<ProduceListing[]> {
  const params = new URLSearchParams();
  if (filters.crop_name) params.append("crop_name", filters.crop_name);
  if (filters.crop_category)
    params.append("crop_category", filters.crop_category);
  if (filters.location_state)
    params.append("location_state", filters.location_state);
  if (filters.location_district)
    params.append("location_district", filters.location_district);
  if (filters.min_price !== undefined)
    params.append("min_price", filters.min_price.toString());
  if (filters.max_price !== undefined)
    params.append("max_price", filters.max_price.toString());

  const queryString = params.toString();
  const endpoint = `${API_BASE_URL}/listings${queryString ? `?${queryString}` : ""}`;

  const response = await fetch(endpoint, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch listings: ${response.status}`);
  }

  return response.json();
}

export async function fetchListingById(id: string): Promise<ProduceListing> {
  const response = await fetch(`${API_BASE_URL}/listings/${id}`, {
    headers: { Accept: "application/json" },
  });

  if (!response.ok) {
    throw new Error(`Listing not found: ${response.status}`);
  }

  return response.json();
}

export async function createProduceListing(
  payload: ProduceCreatePayload,
): Promise<ProduceListing> {
  const response = await fetch(`${API_BASE_URL}/listings`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    const message = errorBody.detail || `Server error (${response.status})`;
    throw new Error(message);
  }

  return response.json();
}
