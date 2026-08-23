from django.shortcuts import render
from .models import Tour, BlogPost, GalleryImage

def index(request):
    return render(request, 'index.html', {
        'tours': Tour.objects.filter(is_popular=True)[:3],
        'posts': BlogPost.objects.filter(is_published=True)[:4],
        'gallery_images': GalleryImage.objects.filter(section='gallery')[:6],
    })
