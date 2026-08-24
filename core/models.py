from django.db import models
from tinymce.models import HTMLField
from phonenumber_field.modelfields import PhoneNumberField

class Tour(models.Model):
    title = models.CharField('Название', max_length=200)
    subtitle = models.CharField('Подзаголовок', max_length=200, blank=True)
    price = models.DecimalField('Цена', max_digits=8, decimal_places=2)
    currency = models.CharField('Валюта', max_length=3, default='BYN')
    rating = models.DecimalField('Рейтинг', max_digits=3, decimal_places=1)
    description = HTMLField('Описание', blank=True)
    program = HTMLField('Программа по дням', blank=True)
    is_popular = models.BooleanField('Популярное', default=False)

    @property
    def cover(self):
        return self.tour_images.first()

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"

    def __str__(self):
        return self.title


class TourImage(models.Model):
    tour = models.ForeignKey(
        Tour,
        related_name='tour_images',
        on_delete=models.CASCADE,
        verbose_name='Тур',
    )
    image = models.ImageField('Картинка', upload_to='tours/')
    order = models.PositiveIntegerField(
        default=0, verbose_name='Порядок отображения', db_index=True
    )

    class Meta:
        verbose_name = 'Фотография тура'
        verbose_name_plural = 'Фотографии тура'
        ordering = ['order']


class BlogPost(models.Model):
    title = models.CharField('Заголовок', max_length=300)
    excerpt = models.TextField('Анонс', max_length=200)
    content = HTMLField('Полный текст')
    image = models.ImageField('Изображение', upload_to='blog/')
    published_date = models.DateField('Дата публикации')
    is_published = models.BooleanField('Опубликовано', default=False)

    class Meta:
        verbose_name = "Статья блога"
        verbose_name_plural = "Статьи блога"
        ordering = ['-published_date']

    def __str__(self):
        return self.title


class Advantage(models.Model):
    icon = models.CharField('Иконка (emoji или класс)', max_length=50)
    title = models.CharField('Заголовок', max_length=200)
    description = HTMLField('Описание')
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        verbose_name = 'Преимущество'
        verbose_name_plural = 'Преимущества'
        ordering = ['order']


class GalleryImage(models.Model):
    image = models.ImageField('Изображение', upload_to='gallery/')
    section = models.CharField(
        'Секция',
        max_length=50,
        choices=[
            ('collage', 'Фотоколлаж (2x2)'),
            ('gallery', 'Фотогалерея (2x3)'),
        ]
    )
    order = models.PositiveIntegerField('Порядок', default=0, db_index=True)

    class Meta:
        verbose_name = 'Изображение галереи'
        verbose_name_plural = 'Изображения галереи'
        ordering = ['order']


class ContactForm(models.Model):
    name = models.CharField('Имя', max_length=100)
    phone = PhoneNumberField('Номер телефона', max_length=20)
    email = models.EmailField('Email', blank=True)
    comment = models.TextField('Комментарий', blank=True)
    form_type = models.CharField(
        'Тип формы',
        max_length=50,
        choices=[
            ('consultation', 'Консультация'),
            ('subscription', 'Подписка'),
            ('tour_search', 'Поиск тура'),
        ]
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    is_processed = models.BooleanField('Обработано', default=False)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'
        ordering = ['-created_at']

