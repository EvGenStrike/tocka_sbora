from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Template(models.Model):
    """Модель шаблона стажировки"""
    name = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    preview_image = models.ImageField(_('Превью'), upload_to='templates/', blank=True, null=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Шаблон')
        verbose_name_plural = _('Шаблоны')

    def __str__(self):
        return self.name


class Internship(models.Model):
    """Модель стажировки"""
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='internships',
                                   verbose_name=_('Создатель'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    is_published = models.BooleanField(_('Опубликовано'), default=False)

    class Meta:
        verbose_name = _('Стажировка')
        verbose_name_plural = _('Стажировки')

    def __str__(self):
        return self.title


class Block(models.Model):
    """Модель блока содержимого"""
    BLOCK_TYPES = (
        ('cover', _('Обложка')),
        ('about', _('О проекте')),
        ('heading', _('Заголовок')),
        ('text', _('Текстовый блок')),
        ('image', _('Изображение')),
        ('form', _('Форма')),
        ('button', _('Кнопка')),
        ('video', _('Видео')),
    )

    internship = models.ForeignKey(Internship, on_delete=models.CASCADE,
                                   related_name='blocks',
                                   verbose_name=_('Стажировка'),
                                   null=True, blank=True)
    template = models.ForeignKey(Template, on_delete=models.CASCADE,
                                 related_name='blocks',
                                 verbose_name=_('Шаблон'),
                                 null=True, blank=True)
    type = models.CharField(_('Тип блока'), max_length=50, choices=BLOCK_TYPES)
    content = models.JSONField(_('Содержимое'), default=dict)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Блок')
        verbose_name_plural = _('Блоки')
        ordering = ['order']

    def __str__(self):
        parent = self.internship or self.template
        return f"{self.get_type_display()} - {parent}"