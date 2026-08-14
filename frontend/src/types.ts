export interface Category {
  id: number
  name: string
  slug: string
  description: string
  product_count: number
  image: string
  image_alt: string
  featured: boolean
  sort_order: number
}

export interface ProductSizeMeasurement {
  id: number
  size: string
  garment_bust: string
  length: string
  recommended_bust: string
  pant_length: string
  sort_order: number
}

export interface Product {
  id: number
  name: string
  slug: string
  category: Category
  short_description: string
  description: string
  price: string
  primary_image: string
  additional_images: string[]
  available_sizes: string[]
  size_chart: ProductSizeMeasurement[]
  available_colors: string[]
  stock_quantity: number
  in_stock: boolean
  featured: boolean
  tone: string
  shape: string
  created_at: string
}

export interface ProductFilters {
  search: string
  category: string
  min_price: string
  max_price: string
  size: string
  color: string
  ordering: string
}

export interface TopProduct {
  id: number
  product: Product
  image: string
  image_alt: string
  sort_order: number
}

export interface NavigationLink {
  id: number
  label: string
  url: string
  sort_order: number
  open_in_new_tab: boolean
}

export interface Banner {
  id: number
  eyebrow: string
  title: string
  description: string
  desktop_image: string
  mobile_image: string
  image_alt: string
  primary_button_label: string
  primary_button_link: string
  secondary_button_label: string
  secondary_button_link: string
  theme: string
  object_position: string
}

export interface DiscountCampaign {
  id: number
  display_type: 'announcement' | 'popup'
  title: string
  message: string
  discount_code: string
  discount_type: 'percentage' | 'fixed' | 'free_delivery'
  discount_value: string
  minimum_order_amount: string
  button_label: string
  button_link: string
  image: string
  image_alt: string
  theme: 'forest' | 'burgundy' | 'pink' | 'black'
  popup_delay_seconds: number
  show_once_per_session: boolean
}

export interface PromoQuote {
  code: string
  title: string
  discount_type: 'percentage' | 'fixed' | 'free_delivery'
  subtotal: string
  delivery_charge: string
  discount_amount: string
  total: string
  message: string
}

export interface HomepageData {
  site_theme: WebsiteTheme
  banners: Banner[]
  top_products: TopProduct[]
  featured_products: Product[]
  navigation_links: NavigationLink[]
}

export type WebsiteTheme = 'dark' | 'white' | 'pink'

export interface ProductAvailability {
  id: number
  slug: string
  stock_quantity: number
  in_stock: boolean
}

export interface AccountUser {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  full_name: string
}

export interface OrderItem {
  product_name: string
  product_slug: string
  product_image: string
  size: string
  color: string
  unit_price: string
  quantity: number
  line_total: string
}

export interface CustomerOrder {
  id: number
  name: string
  email: string
  phone: string
  address: string
  city: string
  postal_code: string
  subtotal: string
  delivery_charge: string
  discount_code: string
  discount_amount: string
  total: string
  status: 'confirmed' | 'shipped' | 'delivered' | 'cancelled'
  status_label: string
  created_at: string
  updated_at: string
  items: OrderItem[]
  payment: PaymentInfo
}

export interface PaymentInfo {
  method: 'bkash' | 'cash_on_delivery'
  method_label: string
  amount: string
  status: 'pending' | 'paid' | 'failed' | 'cancelled'
  status_label: string
  provider_reference: string
  failure_reason: string
  attempts: number
  created_at: string
  updated_at: string
}

export interface BkashPaymentConfig {
  mode: 'automated' | 'manual' | 'unavailable'
  automated: boolean
  manual: boolean
  merchant_number: string
  environment: '' | 'sandbox' | 'production'
}

export interface BkashGatewayStart {
  payment: PaymentInfo
  redirect_url?: string
}
