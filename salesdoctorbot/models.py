from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid
import random

class WareHouse(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    sd_id = models.CharField(_("SD ID"), max_length=255, unique=True)
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, unique=True)    

    class Meta:
        verbose_name = _("WareHouse")
        verbose_name_plural = _("Warehouses")

    def __str__(self):
        return self.name

class StockProduct(models.Model):
    sd_id = models.CharField(_("Product SD ID"), max_length=255, unique=True)
    name = models.CharField(_("Product name"), max_length=255)

    class Meta:
        verbose_name = _("Stock product")
        verbose_name_plural = _("Stock products")

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(_("Name"), max_length=255, default="Xan Decor")
    sd_id = models.CharField(_("SD ID"), max_length=255, unique=True, default="d0_5")

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return self.name

class Store(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE, related_name='stores')
    uuid = models.UUIDField(_("UUID"), default=uuid.uuid4, editable=False, unique=True)
    class Meta:
        verbose_name = _("Store")
        verbose_name_plural = _("Stores")

    def __str__(self):
        return self.name

class WareHouseProduct(models.Model):
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    product = models.ForeignKey(StockProduct, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    prixod = models.IntegerField(_("Prixod"), default=0)
    sold = models.IntegerField(_("Sold"), default=0)
    ostatok = models.IntegerField(_("Ostatok"), default=0)
    arrivel_date = models.DateTimeField(_("Arrivel date"), null=True, blank=True)
    shelf = models.CharField(_("Shelf"), max_length=255, null=True, blank=True, default="A1")

    class Meta:
        verbose_name = _("Warehouse product")
        verbose_name_plural = _("Warehouse products")
        unique_together = ('warehouse', 'product', 'category')

    def __str__(self):
        return f"{self.warehouse.name} - {self.product.name}"

class StoreProduct(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(StockProduct, on_delete=models.CASCADE)
    quantity = models.IntegerField(_("Quantity"), default=0)

    class Meta:
        verbose_name = _("Store product")
        verbose_name_plural = _("Store products")
        unique_together = ('store', 'product')

    def __str__(self):
        return f"{self.store.name} - {self.product.name}"

class Client(models.Model):
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    name = models.CharField(_("Name"), max_length=255)
    phone = models.CharField(_("Phone"), max_length=255, unique=True)
    enrollement_count = models.IntegerField(_("Enrollement count"), default=0)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
    
    def __str__(self):
        return self.name
    
class Feedback(models.Model):
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    text = models.TextField()
    is_store = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _("Feedback")
        verbose_name_plural = _("Feedbacks")
        
    def __str__(self):
        return self.text
    