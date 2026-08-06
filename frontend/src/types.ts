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
