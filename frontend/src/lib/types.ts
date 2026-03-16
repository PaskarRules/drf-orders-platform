export interface User {
  id: number;
  email: string;
  username: string;
  phone: string;
  is_staff: boolean;
  date_joined: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  username: string;
  phone?: string;
  password: string;
  password_confirm: string;
}

export interface ChangePasswordData {
  old_password: string;
  new_password: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  created_at: string;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  sku: string;
  description: string;
  price: string;
  stock_quantity: number;
  category: number;
  category_name: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CartItem {
  product: Product;
  quantity: number;
}

export interface OrderItem {
  id: number;
  product: number;
  product_name: string;
  quantity: number;
  unit_price: string;
  line_total: string;
}

export interface Order {
  id: number;
  order_number: string;
  user_email: string;
  status: OrderStatus;
  total_amount: string;
  notes: string;
  items: OrderItem[];
  created_at: string;
  updated_at: string;
}

export type OrderStatus =
  | "pending"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled";

export interface CreateOrderItem {
  product_id: number;
  quantity: number;
}

export interface CreateOrderData {
  items: CreateOrderItem[];
  notes?: string;
}

export interface Notification {
  id: number;
  notification_type: string;
  title: string;
  message: string;
  is_read: boolean;
  order: number | null;
  created_at: string;
}

export interface DailyOrderReport {
  id: number;
  report_date: string;
  total_orders: number;
  total_revenue: string;
  completed_count: number;
  failed_count: number;
  cancelled_count: number;
  avg_order_value: string;
  report_data: Record<string, unknown>;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  detail?: string;
  [key: string]: unknown;
}
