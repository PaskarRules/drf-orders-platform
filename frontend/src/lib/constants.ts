export const API_BASE_URL = "/api/v1";

export const ROUTES = {
  HOME: "/",
  LOGIN: "/login",
  REGISTER: "/register",
  PRODUCTS: "/products",
  CART: "/cart",
  ORDERS: "/orders",
  NOTIFICATIONS: "/notifications",
  PROFILE: "/profile",
  ADMIN: "/admin",
} as const;

export const API_ROUTES = {
  LOGIN: `${API_BASE_URL}/auth/login/`,
  REFRESH: `${API_BASE_URL}/auth/login/refresh/`,
  REGISTER: `${API_BASE_URL}/auth/register/`,
  LOGOUT: `${API_BASE_URL}/auth/logout/`,
  PROFILE: `${API_BASE_URL}/auth/profile/`,
  CHANGE_PASSWORD: `${API_BASE_URL}/auth/password/change/`,
  PRODUCTS: `${API_BASE_URL}/products/`,
  CATEGORIES: `${API_BASE_URL}/categories/`,
  ORDERS: `${API_BASE_URL}/orders/`,
  NOTIFICATIONS: `${API_BASE_URL}/notifications/`,
  NOTIFICATIONS_MARK_READ: `${API_BASE_URL}/notifications/mark-read/`,
  NOTIFICATIONS_UNREAD_COUNT: `${API_BASE_URL}/notifications/unread-count/`,
  REPORTS_DAILY: `${API_BASE_URL}/reports/daily/`,
} as const;
