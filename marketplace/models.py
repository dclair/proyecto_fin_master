from django.db import models
from django.contrib.auth.models import User
from profiles.models import Hobby
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from posts.models import validate_image_size
import os

def validate_video_size(value):
    filesize = value.size
    if filesize > 15 * 1024 * 1024:
        raise ValidationError("El tamaño máximo del video es 15MB")

class Listing(models.Model):
    LISTING_TYPES = [
        ('SALE', 'Venta'),
        ('RENT', 'Alquiler de equipo'),
        ('SPACE', 'Alquiler de Espacio/Gabinete'),
        ('EXCHANGE', 'Intercambio'),
        ('OTHER', 'Otro'),
    ]

    STATUS_CHOICES = [
        ('AVAILABLE', 'Disponible'),
        ('RESERVED', 'Reservado'),
        ('SOLD', 'Vendido/Alquilado'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings', verbose_name='vendedor')
    hobby = models.ForeignKey(Hobby, on_delete=models.SET_NULL, null=True, blank=True, related_name='listings', verbose_name='terapia', help_text='Déjalo en blanco si el artículo/servicio aplica a múltiples terapias (ej: una camilla).')
    
    title = models.CharField('título', max_length=200)
    slug = models.SlugField('slug', max_length=255, unique=True, blank=True)
    description = models.TextField('descripción', max_length=2000)
    
    price = models.DecimalField('precio', max_digits=10, decimal_places=2, default=0.00, help_text='Pon 0 para intercambios o si es a convenir.')
    
    listing_type = models.CharField('tipo de anuncio', max_length=20, choices=LISTING_TYPES, default='SALE')
    status = models.CharField('estado', max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')
    
    image = models.ImageField(
        'imagen',
        upload_to='marketplace_images/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size,
        ],
        help_text='Formatos soportados: JPG, JPEG, PNG. Tamaño máximo: 5MB'
    )
    
    video = models.FileField(
        'video',
        upload_to='marketplace_videos/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov']),
            validate_video_size,
        ],
        help_text='Opcional. Duración máxima: 1 minuto. Tamaño máximo: 15MB. Formatos: MP4, WebM, MOV.'
    )
    
    created_at = models.DateTimeField('fecha de publicación', auto_now_add=True)
    updated_at = models.DateTimeField('última actualización', auto_now=True)

    class Meta:
        verbose_name = 'anuncio'
        verbose_name_plural = 'anuncios'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            # Generar slug único basado en título y usuario
            base_slug = slugify(self.title)
            slug = f"{base_slug}-{self.seller.id}"
            counter = 1
            while Listing.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{self.seller.id}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image and os.path.isfile(self.image.path):
            os.remove(self.image.path)
        if self.video and os.path.isfile(self.video.path):
            os.remove(self.video.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.title} - {self.get_listing_type_display()}"


class SellerReview(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_reviews', verbose_name='vendedor')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_left', verbose_name='comprador/evaluador')
    rating = models.PositiveSmallIntegerField(
        'puntuación',
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=5
    )
    comment = models.TextField('comentario', max_length=500, blank=True)
    created_at = models.DateTimeField('fecha de valoración', auto_now_add=True)

    class Meta:
        verbose_name = 'valoración de vendedor'
        verbose_name_plural = 'valoraciones de vendedores'
        unique_together = ('seller', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.reviewer.username} valora a {self.seller.username} con {self.rating}★"
