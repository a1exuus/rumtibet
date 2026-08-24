from django.shortcuts import render
from .models import Tour, BlogPost, GalleryImage, ContactForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect
from .services import notify_telegram
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

def index(request):
    return render(request, 'index.html', {
        'tours': Tour.objects.filter(is_popular=True)[:3],
        'posts': BlogPost.objects.filter(is_published=True)[:4],
        'gallery_images': GalleryImage.objects.filter(section='gallery')[:6],
        'collage_images': GalleryImage.objects.filter(section='collage')[:4],
    })


def programs(request):
    tours = Tour.objects.all()

    location = request.GET.get('location')
    price_max = request.GET.get('price_max')
    sort = request.GET.get('sort', 'rating')

    if location:
        tours = tours.filter(pk=location)
    if price_max:
        tours = tours.filter(price__lte=price_max)

    if sort == 'price_asc':
        tours = tours.order_by('price')
    elif sort == 'price_desc':
        tours = tours.order_by('-price')
    else:
        tours = tours.order_by('-rating')

    return render(request, 'programs.html', {
        'tours': tours,
        'all_tours': Tour.objects.all(),
        'filters': {
            'location': location or '',
            'price_max': price_max or '',
            'sort': sort,
        }
    })


def blog(request):
    posts = BlogPost.objects.filter(is_published=True)
    paginator = Paginator(posts, 4)  # по 4 карточки (сетка 2×2)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blog.html', {'page_obj': page_obj})


def blog_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, is_published=True)
    related = (
        BlogPost.objects.filter(is_published=True)
        .exclude(pk=post.pk)[:2]
    )
    return render(request, 'blog_post.html', {'post': post, 'related': related})


def tour_detail(request, pk):
    tour = get_object_or_404(Tour, pk=pk)
    return render(request, 'tour_detail.html', {
        'tour': tour,
        'images': tour.tour_images.all(),
        'initial_date': request.GET.get('date', ''),
        'initial_people': request.GET.get('people', ''),
    })


def booking(request):
    if request.method != 'POST':
        return redirect('home')
    tour = Tour.objects.filter(pk=request.POST.get('tour_id')).first()
    parts = []
    if tour: parts.append(f'Тур: {tour.title}')
    if request.POST.get('date'): parts.append(f'Дата: {request.POST.get("date")}')
    if request.POST.get('people'): parts.append(f'Участников: {request.POST.get("people")}')
    if request.POST.get('comment'): parts.append(request.POST.get('comment'))

    lead = ContactForm.objects.create(
        name=request.POST.get('name', ''),
        phone=request.POST.get('phone') or '',
        email=request.POST.get('email', ''),
        comment=' | '.join(parts),
        form_type='tour_search',
    )

    notify_telegram(f"🧳Бронирование!\n\n{lead.name}\n{lead.comment}\n\nСвязь: {lead.phone}, {lead.email}", lead.pk)
    messages.success(request, 'Заявка отправлена! Мы свяжемся с вами.')
    return redirect(f'/programs/{tour.pk}/' if tour else '/')


def consultation(request):
    if request.method != 'POST':
        return redirect('home')

    if request.POST.get('website'):
        return redirect(request.META.get('HTTP_REFERER', '/'))

    name    = request.POST.get('name', '').strip()
    phone   = request.POST.get('phone', '').strip()
    email   = request.POST.get('email', '').strip()
    comment = request.POST.get('comment', '').strip()

    if not name or not (phone or email):
        messages.error(request, 'Заполните имя и телефон или e-mail.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    lead = ContactForm.objects.create(
        name=name, phone=phone, email=email, comment=comment,
        form_type='consultation',
    )
    notify_telegram(
        f'💬 Заявка на консультацию!\n'
        f'👤 {name}\n📞 {phone or "—"}\n✉️ {email or "—"}\n'
        f'💬 {comment or "—"}',
        lead.pk,
    )
    messages.success(request, 'Спасибо! Мы скоро свяжемся с вами.')
    return redirect(request.META.get('HTTP_REFERER', '/'))


def subscribe(request):
    if request.method != 'POST':
        return redirect('home')

    if request.POST.get('website'):
        return redirect(request.META.get('HTTP_REFERER', '/'))

    email = request.POST.get('email', '').strip()

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, 'Похоже, в e-mail опечатка. Проверьте формат.')
        return redirect(request.META.get('HTTP_REFERER', '/'))

    lead = ContactForm.objects.create(
        name='Подписка', phone='', email=email,
        comment='Подписка на рассылку',
        form_type='subscription',
    )
    notify_telegram(f'📬 Новая подписка на рассылку: {email}', lead.pk)
    messages.success(request, 'Готово! Вы подписаны на рассылку.')
    return redirect(request.META.get('HTTP_REFERER', '/'))
