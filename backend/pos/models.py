from django.db import models
import os
from django.utils.timezone import now
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.models import User
from django.db.models import UniqueConstraint
from django.core.validators import MinValueValidator
from django.conf import settings
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.dispatch import receiver


class Category(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.code})"  

# 01. Tambah model Unit
class Unit(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class BackupUpload(models.Model):
    file = models.FileField(upload_to='backups/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Backup file: {self.file.name}"
    
    
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Purchase(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    invoice_id = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.invoice_id} - {self.supplier.name}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

class PurchaseReturn(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='returns')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    refunded_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[('Approved', 'Approved'), ('Pending', 'Pending')], default='Pending')
    returned_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Return - {self.purchase.invoice_id} - {self.product.name}"
    
    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Jumlah retur harus lebih dari 0.")

        if self.refunded_amount < 0:
            raise ValidationError("Jumlah refund tidak boleh negatif.")    
    
    
# 01.1 Tambah model Warehouse
class Warehouse(models.Model):
    name = models.CharField(max_length=100, unique=True)
    location = models.TextField(blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# 01.2 Tambah model Stock per Warehouse
class Stock(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='stocks')
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            UniqueConstraint(fields=['product', 'warehouse'], name='uniq_product_warehouse')
        ]

    def __str__(self):
        return f"{self.product.name} - {self.quantity} pcs @ {self.warehouse.name}"

  
# 2. Baru Product
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    
    # New fields for variant, unit, and discount
    variant = models.CharField(max_length=100, blank=True, null=True)  # Field for variants (e.g., size, color)
    unit = models.ForeignKey(Unit, on_delete=models.SET_NULL, null=True, blank=True)  # Field for unit
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    
    stock = models.PositiveIntegerField()
    min_stock = models.PositiveIntegerField(default=0)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    
    def get_price_after_discount(self):
        return self.price - (self.price * self.discount / Decimal("100"))

    def __str__(self):
        return f"{self.name} ({self.sku})"

# 2.1 Baru StockAdjustment
class StockAdjustment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    old_stock = models.IntegerField()
    new_stock = models.IntegerField()
    reason = models.CharField(max_length=255)
    adjusted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    adjusted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.old_stock = self.product.stock
            self.product.stock = self.new_stock
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product.name} adjusted by {self.adjusted_by}"


# 3. Transaction
class Transaction(models.Model):
    PAYMENT_CHOICES = (
        ('cash', 'Cash'),
        ('transfer', 'Bank Transfer'),
        ('credit', 'Credit'),
        ('qris', 'QRIS'),
    )
    customer = models.ForeignKey('Customer', on_delete=models.SET_NULL, null=True, blank=True)
    invoice_id = models.CharField(max_length=20, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invoice #{self.invoice_id} - {self.total}"
    
    @property
    def amount_due(self):
        return max(self.total - self.amount_paid, Decimal("0"))
    
    
class StockMovement(models.Model):
    MOVEMENT_TYPES = (
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    note = models.CharField(max_length=255, blank=True)
    adjusted_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.get_movement_type_display()} {self.quantity} @ {self.warehouse.name}"
    
 
class StockTransfer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    from_warehouse = models.ForeignKey(Warehouse, related_name='transfers_out', on_delete=models.CASCADE)
    to_warehouse = models.ForeignKey(Warehouse, related_name='transfers_in', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    note = models.CharField(max_length=255, blank=True)
    transferred_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} — {self.quantity} dari {self.from_warehouse.name} ke {self.to_warehouse.name}"

# 4. TransactionItem
class TransactionItem(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


# 5. Profile
class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('cashier', 'Cashier'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='cashier')

    def __str__(self):
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    Profile.objects.get_or_create(user=instance)


# 6. Customer
class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True)
    points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    
class PointsEarningRule(models.Model):
    """
    Aturan perolehan poin berbasis minimum total belanja.
    Ambil rule dengan min_total TERBESAR yang <= total transaksi.
    Contoh (tabel kanan 'Pontus'):
      - min_total 100.00 -> points_awarded 5
      - min_total 500.00 -> points_awarded 30
    """
    name = models.CharField(max_length=120, blank=True, default="")
    min_total = models.DecimalField(max_digits=12, decimal_places=2, help_text="Minimal total belanja")
    points_awarded = models.PositiveIntegerField(help_text="Poin yang didapat bila total >= min_total")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["min_total"]

    def __str__(self):
        return f"≥ ${self.min_total} → {self.points_awarded} pts"


# 6.1 Tukar Poin
class PointsRedemptionRule(models.Model):
    """
    Aturan penukaran poin (Troka Pontos) - kiri:
      poin -> detil (deskripsi) + optional diskon uang.
    """
    name = models.CharField(max_length=120, blank=True, default="")
    points_required = models.PositiveIntegerField(help_text="Poin yang dibutuhkan")
    detail = models.CharField(max_length=255, blank=True, default="", help_text="Detalle (mis. Diskon $5)")
    discount_amount = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00"),
        help_text="Nominal diskon uang saat ditebus (opsional, bisa 0)"
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["points_required"]

    def __str__(self):
        return f"{self.points_required} pts → {self.detail or ('-$' + str(self.discount_amount))}"


class PointsLedger(models.Model):
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE, related_name='points_ledger')
    change = models.IntegerField(help_text="+ untuk earn, - untuk redeem")
    balance_after = models.IntegerField(default=0)
    note = models.CharField(max_length=255, blank=True, default="")
    transaction = models.ForeignKey('Transaction', on_delete=models.SET_NULL, null=True, blank=True, related_name='points_entries')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sign = "+" if self.change >= 0 else ""
        return f"{self.customer.name}: {sign}{self.change} pts @ {self.created_at:%Y-%m-%d %H:%M}"


def calculate_points_from_total(total: Decimal) -> int:
    try:
        rule = PointsEarningRule.objects.filter(is_active=True, min_total__lte=total).order_by('-min_total').first()
        return rule.points_awarded if rule else 0
    except Exception:
        return 0    
    
    
@receiver(post_save, sender=Transaction)
def add_points_after_transaction_created(sender, instance: Transaction, created, **kwargs):
    if not created:
        return
    if not instance.customer:
        return

    pts = calculate_points_from_total(Decimal(instance.total))
    if pts <= 0:
        return

    cust = instance.customer
    cust.points = (cust.points or 0) + pts
    cust.save(update_fields=["points"])

    PointsLedger.objects.create(
        customer=cust,
        change=pts,
        balance_after=cust.points,
        note=f"Earn from invoice {instance.invoice_id}",
        transaction=instance
    )    


# 7. StoreProfile
def logo_upload_path(instance, filename):
    base, ext = os.path.splitext(filename)
    return f'logos/logo_{now().strftime("%Y%m%d%H%M%S")}{ext}'

class StoreProfile(models.Model):
    LOCATION_CHOICES = [
        ("Aileu Timor-Leste", "Aileu Timor-Leste"),
        ("Ainaro Timor-Leste", "Ainaro Timor-Leste"),
        ("Baucau Timor-Leste", "Baucau Timor-Leste"),
        ("Bobonaro Timor-Leste", "Bobonaro Timor-Leste"),
        ("Covalima Timor-Leste", "Covalima Timor-Leste"),
        ("Dili Timor-Leste", "Dili Timor-Leste"),
        ("Ermera Timor-Leste", "Ermera Timor-Leste"),
        ("Lautem Timor-Leste", "Lautem Timor-Leste"),
        ("Liquiça Timor-Leste", "Liquiça Timor-Leste"),
        ("Manatuto Timor-Leste", "Manatuto Timor-Leste"),
        ("Manufahi Timor-Leste", "Manufahi Timor-Leste"),
        ("Oecusse Timor-Leste", "Oecusse Timor-Leste"),
    ]

    
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, blank=True, null=True)
    logo = models.ImageField(upload_to=logo_upload_path, blank=True, null=True)
    logo_base64 = models.TextField(null=True, blank=True)
    version = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            old = StoreProfile.objects.get(pk=self.pk)
            if old.logo and old.logo != self.logo:
                old_path = old.logo.path
                if os.path.isfile(old_path):
                    os.remove(old_path)
        super().save(*args, **kwargs)
        

# 8. ProductReturn
class ProductReturn(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    transaction = models.ForeignKey('Transaction', on_delete=models.CASCADE, related_name='returns')
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='returns')
    quantity = models.PositiveIntegerField()
    refunded_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    returned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Return {self.product.name} ({self.quantity})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.quantity <= 0:
            raise ValidationError("Jumlah retur harus lebih dari 0.")

        max_refund = self.product.get_price_after_discount() * self.quantity
        if self.refunded_amount > max_refund:
            raise ValidationError(f"Jumlah refund maksimal untuk {self.quantity} pcs adalah {max_refund:.2f}")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and self.status == 'approved':
            self.product.stock += self.quantity
            self.product.save()

            if self.transaction:
                self.transaction.total -= self.refunded_amount
                if self.transaction.total < Decimal("0"):
                    self.transaction.total = Decimal("0")

                if self.transaction.amount_due > 0:
                    potong = min(self.refunded_amount, self.transaction.amount_due)
                    self.transaction.amount_paid += potong

                self.transaction.save()


class Expense(models.Model):
    date = models.DateField()
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.date} - {self.name} - ${self.amount}"
    

def D(x):
    """Konversi aman ke Decimal dari berbagai tipe (None, int, str, Decimal)."""
    return x if isinstance(x, Decimal) else Decimal(str(x or '0'))

# 9. Bank Payment
class Bank(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, blank=True)      
    account_name = models.CharField(max_length=120, blank=True)
    account_number = models.CharField(max_length=60, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True) 

    # Fee rules (cukup untuk 80% kasus)
    percent_fee = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    fixed_fee   = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    min_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    max_fee     = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))
    fee_paid_by_customer = models.BooleanField(default=True)  

    enable_credit = models.BooleanField(default=True) 
    enable_transfer = models.BooleanField(default=True)
    enable_qris = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class BankPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'pending'),
        ('verified', 'verified'),
        ('rejected', 'rejected'),
    ]

    transaction = models.ForeignKey('pos.Transaction', on_delete=models.CASCADE, related_name='bank_payments')
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT)
    gross_amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))]   # ✅ validasi ≥ 0 di level field
    )
    fee_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    proof = models.FileField(upload_to='payments/proofs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        errors = {}

        if self.gross_amount is None or self.gross_amount < Decimal("0.00"):
            errors['gross_amount'] = "Gross amount harus ≥ 0."

        if self.bank and not self.bank.is_active:
            errors['bank'] = "Bank tidak aktif."

        pm = getattr(self.transaction, 'payment_method', None)
        if pm == 'transfer' and not self.bank.enable_transfer:
            errors['bank'] = "Bank ini tidak mengizinkan Transfer."
        if pm == 'credit' and not self.bank.enable_credit:
            errors['bank'] = "Bank ini tidak mengizinkan Credit."
        if pm == 'qris' and not self.bank.enable_qris:
            errors['bank'] = "Bank ini tidak mengizinkan QRIS."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()

        gross   = D(self.gross_amount)
        percent = D(getattr(self.bank, "percent_fee", 0)) / Decimal("100")
        fixed   = D(getattr(self.bank, "fixed_fee", 0))
        min_fee = D(getattr(self.bank, "min_fee", 0))
        max_fee = D(getattr(self.bank, "max_fee", 0))

        fee = (gross * percent) + fixed
        if min_fee > 0 and fee < min_fee:
            fee = min_fee
        if max_fee > 0 and fee > max_fee:
            fee = max_fee

        fee = fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        net = (gross - fee).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if net < Decimal("0.00"):
            raise ValidationError({"gross_amount": "Konfigurasi fee melebihi gross. Periksa fixed/min/max fee."})

        self.fee_amount = fee
        self.net_amount = net
        return super().save(*args, **kwargs)