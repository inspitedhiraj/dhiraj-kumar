"""
URL configuration for tannis project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tannis_app.views import *
from tannis_app.controller.category import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('admin-login/', AdminLogin),
    path('admin-logout/', AdminLogout),
    path('dashboard/', Dashboard),
    path('add-category/', AddCategory),
    path('add-shades/', AddShades),
    path('list-shades/', ListShades),
    path('list-category/', ListCategory),
    path('add-sub-category/', AddSubCategory),
    path('list-sub-category/', ListSubCategory),
    path('add-mid-category/', AddMidCategory),
    path('list-mid-category/', ListMidCategory),
    path('list-order/', ListOrder),
    path('list-customer/', ListCustomer),
    path('fetch-mid-category/', FetchMidCategory),
    path('fetch-sub-category/', FetchSubCategory),
    path('list-vendor/', ListVendor),
    path('api/', include('api.urls')),
    path('vendor/', include('vendor.urls')),
    path('add-brand/', AddBrand),
    path('list-brand/', ListBrand),
    path('add-product-type/', AddProductType),
    path('list-product-type/', ListProductType),
    path('list-product/', ListProduct),
    path('list-variant/<p_id>', ListVariant),
    path('change-product-status/', ChangeProductStatus),
    path('delete-category/<id>', DeleteCategory),
    path('delete-sub-category/<id>', DeleteSubCategory),
    path('delete-product-type/<id>', DeleteProductType),
    path('delete-brand/<id>', DeleteBrand),
    path('change-vendor-status/', ChangeVendorStatus),
    path('edit-category/<id>', EditCategory),
    path('edit-sub-category/<id>', EditSubCategory),
    path('edit-brand/<id>', EditBrand),
    path('delete-vendor/<id>', DeleteVendor),
    path('add-banner/', AddBanner),
    path('list-banner/', ListBanner),
    path('change-order-status/', ChangeOrderStatus),
    path('edit-vendor/<id>', UpdateVendor),
    path('add-vendor/', AddVendor),
    path('list-customer/', ListCustomer),
    path('change-customer-status/', ChangeCustomerStatus),
    path('change-brand-wishlist-status/', ChangeBrandWishlistStatus),
    path('add-tranding-offer/', AddTrandingOffer),
    path('list-tranding-offer/', ListTrandingOffer),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
