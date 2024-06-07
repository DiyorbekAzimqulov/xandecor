from modeltranslation.translator import register, TranslationOptions
from . import models

@register(models.CategoryWallPaper)
class CategoryWallPaperTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(models.CategoryLed)
class CategoryLedTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(models.CarouselMainPhoto)
class CarouselMainPhotoTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(models.Wallcovers)
class WallcoversTranslationOptions(TranslationOptions):
    fields = ('description',)  

@register(models.Leds)
class LedsTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(models.Teams)
class TeamsTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(models.Service)
class ServiceTranslationOptions(TranslationOptions):
    fields = ('name', 'description')

@register(models.News)
class NewsTranslationOptions(TranslationOptions):
    fields = ('title', 'description')
