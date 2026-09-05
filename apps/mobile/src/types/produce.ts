export interface ProduceAttributes {
  variety?: string;
  organic_certified?: boolean;
  grade?: string;
  moisture_percentage?: number;
  cold_chain_required?: boolean;
  [key: string]: unknown;
}

export type ProduceStatus = "ACTIVE" | "RESERVED" | "SOLD_OUT" | "DELISTED";

export interface ProduceListing {
  id: string;
  seller_id: string;
  crop_name: string;
  crop_category: string;
  quantity: string | number;
  unit: string;
  price_per_unit: string | number;
  harvest_date: string;
  shelf_life_days: number;
  status: ProduceStatus;
  location_pincode: string;
  location_district: string;
  location_state: string;
  location_lat?: number | null;
  location_lng?: number | null;
  attributes: ProduceAttributes;
  created_at: string;
  updated_at: string;
}

export interface ProduceCreatePayload {
  seller_id: string;
  crop_name: string;
  crop_category: string;
  quantity: number;
  unit: string;
  price_per_unit: number;
  harvest_date: string;
  shelf_life_days: number;
  location_pincode: string;
  location_district: string;
  location_state: string;
  attributes?: ProduceAttributes;
}

export interface ListingFilterParams {
  crop_name?: string;
  crop_category?: string;
  location_state?: string;
  location_district?: string;
  min_price?: number;
  max_price?: number;
}
