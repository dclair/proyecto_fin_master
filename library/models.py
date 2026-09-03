from django.db import models
from django.contrib.auth.models import User
from profiles.models import Hobby
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from posts.models import validate_image_size
from marketplace.models import validate_video_size
import os

def validate_document_size(value):
    filesize = value.size
    if filesize > 15 * 1024 * 1024:
        raise ValidationError("El tamaño máximo del documento es 15MB")

class Article(models.Model):
    title = models.CharField('título', max_length=200)
    slug = models.SlugField('slug', max_length=255, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles', verbose_name='autor')
    hobby = models.ForeignKey(Hobby, on_delete=models.CASCADE, related_name='articles', verbose_name='terapia/categoría')
    
    content = models.TextField('contenido')
    
    cover_image = models.ImageField(
        'imagen de portada',
        upload_to='library_covers/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_image_size,
        ],
        help_text='Sugerencia: Imagen horizontal, máximo 5MB.'
    )
    
    attached_video = models.FileField(
        'video adjunto',
        upload_to='library_videos/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'webm', 'mov']),
            validate_video_size,
        ],
        help_text='Opcional. Tamaño máximo: 15MB.'
    )
    
    attached_document = models.FileField(
        'documento adjunto',
        upload_to='library_documents/%Y/%m/%d/',
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'txt', 'odt']),
            validate_document_size,
        ],
        help_text='Opcional. Para descargar. Tamaño máximo: 15MB.'
    )
    
    external_video_url = models.URLField('enlace de video externo', blank=True, null=True, help_text='Para videos pesados (YouTube, Vimeo, Drive).')
    external_document_url = models.URLField('enlace de documento externo', blank=True, null=True, help_text='Para documentos pesados (Drive, Dropbox).')
    
    created_at = models.DateTimeField('fecha de publicación', auto_now_add=True)
    updated_at = models.DateTimeField('última actualización', auto_now=True)
    views_count = models.PositiveIntegerField('visualizaciones', default=0)

    class Meta:
        verbose_name = 'artículo/caso de estudio'
        verbose_name_plural = 'artículos y casos de estudio'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = f"{base_slug}-{self.author.id}"
            counter = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{self.author.id}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.cover_image and os.path.isfile(self.cover_image.path):
            os.remove(self.cover_image.path)
        if self.attached_video and os.path.isfile(self.attached_video.path):
            os.remove(self.attached_video.path)
        if self.attached_document and os.path.isfile(self.attached_document.path):
            os.remove(self.attached_document.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('library:article_detail', kwargs={'slug': self.slug})

    @property
    def plain_text_summary(self):
        import html
        import re
        if not self.content:
            return ""
        # Reemplazar tags de bloque o saltos (<br>, </p>, </h1>...) por espacio
        text = re.sub(r'<(br|/p|/div|/h[1-6]|/li)[^>]*>', ' ', self.content, flags=re.IGNORECASE)
        # Quitar todos los tags HTML restantes
        text = re.sub(r'<[^>]+>', '', text)
        # Decodificar entidades HTML (&eacute; -> é, &nbsp; -> espacio, etc.)
        text = html.unescape(text)
        # Normalizar espacios múltiples
        return re.sub(r'\s+', ' ', text).strip()


class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name='artículo')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_comments', verbose_name='autor')
    content = models.TextField('comentario', max_length=1000)
    created_at = models.DateTimeField('fecha de creación', auto_now_add=True)

    class Meta:
        verbose_name = 'comentario'
        verbose_name_plural = 'comentarios'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comentario de {self.author.username} en {self.article.title}"

class ArticleRating(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings', verbose_name='artículo')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_ratings', verbose_name='autor')
    rating = models.PositiveSmallIntegerField('puntuación', validators=[MinValueValidator(1), MaxValueValidator(5)], default=5)
    created_at = models.DateTimeField('fecha de valoración', auto_now_add=True)

    class Meta:
        verbose_name = 'valoración'
        verbose_name_plural = 'valoraciones'
        unique_together = ('article', 'author')

    def __str__(self):
        return f"{self.author.username} valora con {self.rating}★ a {self.article.title}"
