from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Category(models.Model):
    c_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='category/')
    slug = models.SlugField(default="", null=False)
    on_our_radar = models.BooleanField()
    status = models.BooleanField()
    created_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.c_name}"

class MidCategory(models.Model):
    m_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='mid-category/')
    slug = models.SlugField(default="", null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category")
    status = models.BooleanField()
    created_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.m_name}"

class SubCategory(models.Model):
    s_name = models.CharField(max_length=255)
    slug = models.SlugField(default="", null=False)
    mid_category = models.ForeignKey(MidCategory, on_delete=models.CASCADE, related_name="mid_category")
    status = models.BooleanField()
    created_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.s_name}"

class Product(models.Model):
    p_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="product_category")
    mid_category = models.ForeignKey(MidCategory, on_delete=models.CASCADE, related_name="product_mid_category")
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="sub_category")
    mrp = models.FloatField()
    selling_price = models.FloatField()
    discount = models.IntegerField()
    # sku = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    short_description = models.TextField()
    long_description = models.TextField()
    product_type = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    vendor_name = models.CharField(max_length=255)
    vendor_contact = models.CharField(max_length=255)
    trending = models.BooleanField()
    deals_of_the_day = models.BooleanField()
    most_popular = models.BooleanField()
    status = models.BooleanField()
    admin = models.BooleanField()
    created_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.p_name}"

class Shades(models.Model):
    s_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='shades/')
    status = models.BooleanField()
    created_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.s_name}"

class Variant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    thumbnail = models.ImageField(upload_to='images/')
    shades = models.ForeignKey(Shades, on_delete=models.CASCADE, related_name="shades")
    size = models.CharField(max_length=5, null=True, blank=True)
    qty = models.IntegerField()
    price = models.FloatField()
    base_shipping_days = models.PositiveIntegerField(default=1)

class ProductImage(models.Model):
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='images/')

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_id = models.CharField(max_length=255, null=True, blank=True)
    total_price = models.FloatField()

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="carts")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="c_variants")
    p_name = models.CharField(max_length=255)
    thumbnail = models.ImageField(upload_to='carts/')
    mrp = models.FloatField()
    price = models.FloatField()
    qty = models.PositiveIntegerField(default=1)
    total_price = models.FloatField()
    # brand = models.CharField(max_length=255)
    # vendor_name = models.CharField(max_length=255)
    # vendor_contact = models.CharField(max_length=255)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=15)
    address = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=6, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='customer-image/', null=True, blank=True)
    otp = models.CharField(max_length=4)
    status = models.BooleanField()

class ShippingAddress(models.Model):
    customer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    pin_code = models.CharField(max_length=255)
    country = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=255)
    TYPE_OF_ADDRESS_CHOICES = {
        "Home": "Home",
        "Work": "Work",
        "Other": "Other",
    }
    type_of_address = models.CharField(max_length=255, choices=TYPE_OF_ADDRESS_CHOICES)
    email = models.CharField(max_length=255, null=True, blank=True)
    is_default = models.BooleanField(default=False)

class Order(models.Model):
    payment_status_choices = {
        "PENDING":"pending",
        "COMPLETED": "completed",
        "FAILED": "failed",
        "REFUNDED": "refunded"
    }
    PAYMENT_CHOICES = [
        ('COD', 'Cash on Delivery'),
        ('ONLINE', 'Online Payment'),
    ]
    ORDER_STATUS_CHOICES = [
        ('created', 'Created'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    total_amount = models.FloatField()
    payment_mode = models.CharField(max_length=255, choices=PAYMENT_CHOICES)
    payment_status = models.CharField(max_length=255, choices=payment_status_choices, default='PENDING')
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=ORDER_STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Ordered_item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="ordered_items")
    variant = models.ForeignKey(Variant, on_delete=models.CASCADE, related_name="o_variants")
    qty = models.PositiveIntegerField()
    price = models.FloatField()
    expected_delivery_date = models.DateField(null=True, blank=True)

class Vendor(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=255)
    gst = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    added_by = models.CharField(max_length=255)
    status = models.BooleanField()

class State(models.Model):
    name = models.CharField(max_length=255)

class City(models.Model):
    name = models.CharField(max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

class Brand(models.Model):
    brand_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='brand/')
    wishlist = models.BooleanField()
    # slug = models.CharField(max_length=255)

class ProductType(models.Model):
    product_type = models.CharField(max_length=255)

class Commission(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE)
    commission = models.IntegerField()

class Banner(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='category/')
    brand = models.CharField(max_length=255)
    status = models.BooleanField()
    created_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.title}"

class TrandingOffer(models.Model):
    coupon = models.CharField(max_length=255)
    image = models.ImageField(upload_to='tranding-offer/')
    discount = models.IntegerField()
    description = models.CharField(max_length=255)

class Otp(models.Model):
    email = models.CharField(max_length=255, null=True)
    phone = models.CharField(max_length=255, null=True)
    otp = models.CharField(max_length=6)
    user = models.IntegerField()

class DeliveryZone(models.Model):
    city = models.CharField(max_length=255)
    pin_code = models.CharField(max_length=6)
    extra_days = models.PositiveIntegerField(default=0)