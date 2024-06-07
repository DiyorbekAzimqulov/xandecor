from django.db import models


# Create your models here.


class CategoryWallPaper(models.Model):
    """CategoryWallPaper model for the wallpaper categories"""
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category Wallpaper'
        verbose_name_plural = 'Category Wallpapers'
        ordering = ['created_at']

class CategoryLed(models.Model):
    """CategoryLed model for the led categories"""
    name = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Category Led'
        verbose_name_plural = 'Category Leds'
        ordering = ['created_at']

class CarouselMainPhoto(models.Model):
    """Main photo model for the main page"""
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    image = models.FileField(upload_to='carousel/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Main Photo'
        verbose_name_plural = 'Main Photos'
        ordering = ['created_at']

class Wallcovers(models.Model):
    """Wallcowers model for the wallpaper photos"""
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default='Wallcover')
    image = models.FileField(upload_to='wallcovers/')
    category = models.ForeignKey(CategoryWallPaper, on_delete=models.CASCADE, related_name='wallcovers')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Wallcover'
        verbose_name_plural = 'Wallcovers'
        ordering = ['created_at']

class Leds(models.Model):
    """Led model for the led photos"""
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default='Led')
    image = models.FileField(upload_to='leds/')
    category = models.ForeignKey(CategoryLed, on_delete=models.CASCADE, related_name='leds')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Led'
        verbose_name_plural = 'Leds'
        ordering = ['created_at']


class News(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField(max_length=400)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'
        ordering = ['-created_at']

class NewsImage(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='news_images/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'News Image'
        verbose_name_plural = 'News Images'

    def __str__(self):
        return self.news.title

class NewsVideo(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE)
    video = models.FileField(upload_to='news_videos/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'News Video'
        verbose_name_plural = 'News Videos'

    def __str__(self):
        return self.news.title


class Teams(models.Model):
    """Teams model for the investor page"""
    name = models.CharField(max_length=100)
    photo = models.FileField(upload_to='investor/')
    telegram = models.CharField(max_length=100)
    instagram = models.CharField(max_length=100, default=telegram, null=True, blank=True)
    wechat = models.CharField(max_length=100, default=telegram, null=True, blank=True)
    description = models.TextField(default='Worker at the company')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        ordering = ['created_at']


class Service(models.Model):
    """Service model for the services page"""
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True, default='Make your life easier with our services.')
    photo = models.FileField(upload_to='services/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'
        ordering = ['created_at']


class DiagramAnalysis(models.Model):
    """Diagram Analysis model for the diagram analysis page"""
    client_numbers = models.CharField(max_length=20)
    license = models.CharField(max_length=20)
    delivered = models.CharField(max_length=20)
    monthly_containers = models.CharField(max_length=20)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Diagram Analysis'
        verbose_name_plural = 'Diagram Analysis'
        ordering = ['created_at']


class AboutUs(models.Model):
    """About us model for the about us page"""
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    work_time = models.CharField(max_length=100)
    telegram = models.CharField(max_length=100)
    facebook = models.CharField(max_length=100)
    instagram = models.CharField(max_length=100)
    wechat = models.CharField(max_length=100, null=True, blank=True, default=telegram)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address

    class Meta:
        verbose_name = 'Social Media'
        verbose_name_plural = 'Social Media'
        ordering = ['created_at']


class Contact(models.Model):
    """Contact model for the contact page"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=250)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        ordering = ['created_at']

class Quote(models.Model):
    """Quote model for the service quote page"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile = models.CharField(max_length=20)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    note = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.mobile

    class Meta:
        verbose_name = 'Quote'
        verbose_name_plural = 'Quotes'
        ordering = ['created_at']

class Brands(models.Model):
    """Brands model for the brands page"""
    name = models.CharField(max_length=100)
    photo = models.FileField(upload_to='brands/')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Brand'
        verbose_name_plural = 'Brands'
        ordering = ['created_at']
