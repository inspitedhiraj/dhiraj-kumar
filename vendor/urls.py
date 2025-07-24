from django.urls import path, include
from vendor_app.views import *

urlpatterns = [
    path('list-product/', ListProduct),
    path('add-product/', AddProduct),
    path('login/', VendorLogin),
    path('logout/', VendorLogout),
    path('dashboard/', VendorDashboard),
    path('list-order/', ListOrder),
    path('add-variant/<p_id>', AddVariant),
    path('list-variant/<p_id>', ListVariant),
    path('change-product-status/', ChangeProductStatus),
    path('delete-product/<id>', DeleteProduct),
    path('invoice/<id>', Invoice),
    path('edit-product/<id>', EditProduct),
    path('edit-profile/', EditProfile),
    path('delete-variant/<id>', DeleteVariant),
    path('delete-product-image/', DeleteProductImage),
    path('change-order-status/', ChangeOrderStatus),
    path('list-ordered-item/<id>', ListOrderedItem),
    path('change-ordered-item-status/', ChangeOrderedItemStatus),
    path('list-customer/', ListCustomer),
]