from django.db import models
from django.contrib.auth.models import User

class Badge(models.Model):
    name = models.CharField('nombre', max_length=100)
    description = models.TextField('descripción')
    icon = models.CharField('icono (FontAwesome)', max_length=50, help_text='Ej: fas fa-award text-warning')
    code_name = models.SlugField('código interno', unique=True, help_text='Ej: maestro-facilitador')
    
    class Meta:
        verbose_name = 'medalla'
        verbose_name_plural = 'medallas'
        
    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges', verbose_name='usuario')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='awarded_to', verbose_name='medalla')
    earned_at = models.DateTimeField('fecha de obtención', auto_now_add=True)
    
    class Meta:
        verbose_name = 'medalla de usuario'
        verbose_name_plural = 'medallas de usuarios'
        unique_together = ('user', 'badge')
        ordering = ['-earned_at']
        
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
