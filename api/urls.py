from django.urls import path, include
from api.views.products import *
from api.views.categories import *
from api.views.subCategories import *
from api.views.midCategories import *
from api.views.banner import *
from api.views.signIn import *
from api.views.brand import *
from api.views.cart import *
from api.views.order import *

urlpatterns = [
    path('products/<sub_category>', product),
    path('categories/', category),
    path('mid-categories/<category>', midCategory),
    path('sub-categories/<mid_category>', subCategory),
    path('banners/', bannerDetails),
    path('product-details/<variantId>', variantDetails),
    # path('sign-in/', signIn),
    path('sign-up/', create_profile),
    path('brands/', brand),
    path('wishlist/', wishlist),
    path('update-user-details/', updateUserDetails),
    path('get-customer-details/', getCustomerDetails),
    # path('update-customer-address/', updateCustomerAddress),
    path('add-to-cart/', addToCart),
    path('remove-from-cart/<int:variant>', removeFromCart),
    path('get-cart/', getCart),
    path('tranding-offer/', trandingOffer),
    path('verify-otp/', verifyOtp),
    path('trending/', trending),
    path('deals-of-the-day/', dealsOfTheDay),
    path('most-popular/', mostPopular),
    path('logout/', logOut),
    path('update-customer-profile-image/', updateCustomerProfileImage),
    path('otp-email/', otpEmail),
    path('update-email/', updateEmail),
    # path('add-email/', addEmail),
    path('otp-phone/', otpPhone),
    path('update-phone/', updatePhone),
    path('search-product/', searchProduct),
    path('product-by-mid-category/<mid_category>', variantByMidCategory),
    path('more-like/', moreLike),
    path('on-our-radar/', onOurRadar),
    path('order/', order),
    path('shipping-address/', shippingAddress),
    path('get-shipping-address/', GetShippingAddress),
    path('check-out/', CheckOut),
    path('get-order/', getOrder),
    path('update-cart-qty/', updateCartQty),
    path('make-default-shipping-address/<int:shipping_id>', make_default_shipping_address),
    path('get-default-shipping-address/', getDefaultShippingAddress),
    path('review-order-details/', reviewOrderDetails),
    path('delete-customer/', deleteUserDetails),
]