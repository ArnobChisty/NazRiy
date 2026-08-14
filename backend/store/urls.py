from django.urls import path

from .auth_views import (
    CurrentUserView, LoginView, LogoutView, PasswordChangeView, PasswordResetConfirmView,
    PasswordResetRequestView, ProfileView, RegisterView,
)
from .banner_views import BannerListView
from .bkash_gateway_views import BkashGatewayCallbackView, BkashGatewayConfigView, BkashGatewayInitiateView
from .discount_views import PromoCodeValidationView
from .sprint3_views import CartItemView, CartView, CheckoutView
from .sprint4_views import CustomerOrderDetailView, CustomerOrderListView
from .sprint5_views import BkashPaymentView
from .views import CategoryListView, DiscountCampaignListView, FeaturedProductListView, HealthCheckView, HomepageView, NavigationLinkListView, ProductAvailabilityView, ProductDetailView, ProductListView, RecommendationListView, RelatedProductListView, TopProductListView, WebsiteThemeView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('homepage/', HomepageView.as_view(), name='homepage'),
    path('theme/', WebsiteThemeView.as_view(), name='website-theme'),
    path('discount-campaigns/', DiscountCampaignListView.as_view(), name='discount-campaigns'),
    path('discounts/validate/', PromoCodeValidationView.as_view(), name='discount-validate'),
    path('banners/', BannerListView.as_view(), name='banner-list'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('auth/password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('auth/password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/<int:pk>/', CartItemView.as_view(), name='cart-item'),
    path('orders/checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', CustomerOrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', CustomerOrderDetailView.as_view(), name='order-detail'),
    path('orders/<int:pk>/payment/', BkashPaymentView.as_view(), name='bkash-payment'),
    path('orders/<int:pk>/payment/bkash/create/', BkashGatewayInitiateView.as_view(), name='bkash-gateway-create'),
    path('payments/bkash/config/', BkashGatewayConfigView.as_view(), name='bkash-gateway-config'),
    path('payments/bkash/callback/', BkashGatewayCallbackView.as_view(), name='bkash-gateway-callback'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/featured/', FeaturedProductListView.as_view(), name='featured-products'),
    path('products/<slug:slug>/related/', RelatedProductListView.as_view(), name='related-products'),
    path('products/<slug:slug>/availability/', ProductAvailabilityView.as_view(), name='product-availability'),
    path('recommendations/', RecommendationListView.as_view(), name='recommendations'),
    path('top-products/', TopProductListView.as_view(), name='top-products'),
    path('navigation-links/', NavigationLinkListView.as_view(), name='navigation-links'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
]
