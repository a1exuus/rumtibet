from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from adminsortable2.admin import SortableAdminBase, SortableTabularInline
from .models import GalleryImage, Tour, BlogPost, Advantage, ContactForm, TourImage


class TourImageInline(SortableTabularInline):
    model = TourImage
    can_delete = False
    extra = 1
    fields = ('image', 'preview_inline')
    readonly_fields = ('preview_inline',)
    verbose_name_plural = 'Фотографии тура'

    def preview_inline(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; border-radius: 4px; object-fit: cover;" />', 
                obj.image.url
            )
        return mark_safe('<span style="color: gray;">Нет фото</span>')
        
    preview_inline.short_description = 'Превью'


@admin.register(Tour)
class TourAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['title', 'subtitle', 'rating']
    inlines = [TourImageInline]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TourImage)
class TourImageAdmin(admin.ModelAdmin):
    list_display = ['tour', 'preview']
    raw_id_fields = ['tour']
    readonly_fields = ['preview']

    def preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 8px; object-fit: cover;" />',
                obj.image.url
            )
        return mark_safe('<span style="color: gray;">Нет изображения</span>')
        
    preview.short_description = 'Превью изображения'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['title', 'published_date', 'is_published']
    list_editable = ['is_published']

@admin.register(Advantage)
class AdvantageAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['title', 'order']

@admin.register(GalleryImage)
class GalleryImageAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = ['section', 'order']
    list_filter = ['section']

@admin.register(ContactForm)
class ContactFormAdmin(admin.ModelAdmin):
    list_display = ['name', 'form_type', 'created_at', 'is_processed']
    list_filter = ['form_type', 'is_processed']
    readonly_fields = ['name', 'phone', 'email', 'comment', 'form_type', 'created_at']
    
    def has_add_permission(self, request):
        return False