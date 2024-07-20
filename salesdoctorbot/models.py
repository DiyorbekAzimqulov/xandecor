from django.db import models
from django.utils.translation import gettext_lazy as _

class WareHouse(models.Model):
    name = models.CharField(_("Name"), max_length=255)
    sd_id = models.CharField(_("SD ID"), max_length=255, unique=True)

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

class WareHouseProduct(models.Model):
    warehouse = models.ForeignKey(WareHouse, on_delete=models.CASCADE)
    product = models.ForeignKey(StockProduct, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    prixod = models.IntegerField(_("Prixod"), default=0)
    sold = models.IntegerField(_("Sold"), default=0)
    ostatok = models.IntegerField(_("Ostatok"), default=0)
    arrivel_date = models.DateTimeField(_("Arrivel date"), null=True, blank=True)

    class Meta:
        verbose_name = _("Warehouse product")
        verbose_name_plural = _("Warehouse products")
        unique_together = ('warehouse', 'product', 'category')

    def __str__(self):
        return f"{self.warehouse.name} - {self.product.name}"

