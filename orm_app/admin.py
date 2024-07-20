from django.contrib import admin

# Register your models here.
from orm_app.models import (
    Category,
    Container,
    Organization,
    Product,
    User,
    Sale,
    Review,
    TelegramGroup,
)


admin.site.register(Category)
admin.site.register(Container)
admin.site.register(Organization)
admin.site.register(Product)
admin.site.register(User)
admin.site.register(Sale)
admin.site.register(Review)
admin.site.register(TelegramGroup)
