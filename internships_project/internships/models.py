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

    # Добавляем новые поля
    duration = models.PositiveIntegerField(_('Длительность (месяцы)'), default=3)
    positions = models.PositiveIntegerField(_('Количество позиций'), default=1)
    salary = models.PositiveIntegerField(_('Оплата (руб/месяц)'), default=0)
    LOCATION_CHOICES = [
        ('remote', 'Удаленно'),
        ('onsite', 'В офисе'),
        ('hybrid', 'Гибридный'),
    ]
    location = models.CharField(_('Формат работы'), max_length=10, choices=LOCATION_CHOICES, default='remote')
    requirements = models.TextField(_('Требования к кандидату'), blank=True)
    benefits = models.TextField(_('Бонусы и преимущества'), blank=True)

    class Meta:
        verbose_name = _('Стажировка')
        verbose_name_plural = _('Стажировки')

    def __str__(self):
        return self.title

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

class ImageItem(models.Model):
    """Изображения, используемые в блоках"""
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='images', verbose_name=_('Блок'))
    image = models.ImageField(_('Изображение'), upload_to='blocks/images/')
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Изображение блока')
        verbose_name_plural = _('Изображения блока')
        ordering = ['order']

    def __str__(self):
        return f"Изображение #{self.pk} для {self.block}"

class TextItem(models.Model):
    """Тексты, отображаемые в текстовых блоках"""
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='texts', verbose_name=_('Блок'))
    text = models.TextField(_('Текст'))
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Текст блока')
        verbose_name_plural = _('Тексты блока')
        ordering = ['order']

    def __str__(self):
        return f"Текст #{self.pk} для {self.block}"

class ButtonItem(models.Model):
    """Кнопки, используемые в блоке"""
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='buttons', verbose_name=_('Блок'))
    label = models.CharField(_('Надпись на кнопке'), max_length=100)
    style = models.CharField(_('CSS-класс / стиль'), max_length=255, blank=True)
    order = models.PositiveIntegerField(_('Порядок'), default=0)

    class Meta:
        verbose_name = _('Кнопка блока')
        verbose_name_plural = _('Кнопки блока')
        ordering = ['order']

    def __str__(self):
        return f"Кнопка '{self.label}' для {self.block}"

class VideoItem(models.Model):
    """Видео, используемое в блоке"""
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='videos', verbose_name=_('Блок'))
    video_url = models.URLField(_('Ссылка на видео'))
    preview_image = models.ImageField(_('Превью видео'), upload_to='blocks/videos/previews/', blank=True, null=True)

    class Meta:
        verbose_name = _('Видео блока')
        verbose_name_plural = _('Видео блока')

    def __str__(self):
        return f"Видео для {self.block}"