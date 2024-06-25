from django.db import models
from django.utils.translation import gettext_lazy as _

class WereHouse(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    address = models.CharField(max_length=200, verbose_name=_('Address'))

    class Meta:
        verbose_name = _('Warehouse')
        verbose_name_plural = _('Warehouses')

    def __str__(self):
        return f"{self.name}/{self.address}"
    
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    