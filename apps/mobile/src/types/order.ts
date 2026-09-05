export interface OrderCreatePayload {
  buyer_id: string;
  listing_id: string;
  quantity: number;
  delivery_address?: {
    street?: string;
    city?: string;
    district?: string;
    state?: string;
    pincode?: string;
    [key: string]: unknown;
  };
}

export interface OrderResponse {
  id: string;
  buyer_id: string;
  seller_id: string;
  listing_id: string;
  quantity: number | string;
  unit_price: number | string;
  total_amount: number | string;
  platform_fee: number | string;
  status: string;
  delivery_address: Record<string, unknown>;
  escrow_status?: string | null;
  created_at: string;
  updated_at: string;
}
