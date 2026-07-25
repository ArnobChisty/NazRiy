from django.urls import path

from .auth_views import (
    CurrentUserView, LoginView, LogoutView, PasswordChangeView, ProfileView, RegisterView,
)
from .banner_views import BannerListView
from .sprint3_views import CartItemView, CartView, CheckoutView
from .sprint4_views import CustomerOrderDetailView, CustomerOrderListView
from .views import CategoryListView, FeaturedProductListView, NavigationLinkListView, ProductDetailView, ProductListView, TopProductListView

urlpatterns = [
    path('banners/', BannerListView.as_view(), name='banner-list'),
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/profile/', ProfileView.as_view(), name='profile'),
    path('auth/password/change/', PasswordChangeView.as_view(), name='password-change'),
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/<int:pk>/', CartItemView.as_view(), name='cart-item'),
    path('orders/checkout/', CheckoutView.as_view(), name='checkout'),
    path('orders/', CustomerOrderListView.as_view(), name='orders'),
    path('orders/<int:pk>/', CustomerOrderDetailView.as_view(), name='order-detail'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/featured/', FeaturedProductListView.as_view(), name='featured-products'),
    path('top-products/', TopProductListView.as_view(), name='top-products'),
    path('navigation-links/', NavigationLinkListView.as_view(), name='navigation-links'),
    path('products/<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
]
