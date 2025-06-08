import re

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse, Http404
from django.contrib.auth.mixins import LoginRequiredMixin
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.contrib.auth import views as auth_views
from django.views.decorators.http import require_POST, require_http_methods

from .models import Internship, Template, Block, ImageItem, TextItem, ButtonItem, VideoItem


def my_internships(request):
    internships = Internship.objects.all()
    print(f"Стажировки: {internships}")

    data = []
    i = 0
    for internship in internships:
        if i == 3 or i == 4:
            i += 1
            continue
        cover = internship.blocks.filter(type='cover').first()
        heading = internship.blocks.filter(type='heading').first()

        cover_url = None
        heading_text = None

        if cover and cover.images.exists():
            cover_url = cover.images.first().image.url

        if heading and heading.texts.exists():
            texts = heading.texts.all()
            heading_str = str(heading)
            match = re.search(r'-\s*(\S+)', heading_str)
            if match:
                internship_heading = match.group(1)

            heading_text = internship_heading
            #heading_text = "Самая лучшая стажировка"

        print(internship)
        data.append({
            'internship': internship,
            'cover_url': cover_url,
            'heading_text': heading_text,
        })

    return render(request, 'internships/my_internships.html', {
        'internship_data': data
    })


def all_internships(request):
    context = {
        'range8': range(8),
    }
    return render(request, 'internships/all_internships.html', context)

def create_internship(request):
    return render(request, 'internships/create_internship.html')

def profile_view(request):
    return render(request, 'internships/profile.html')

class InternshipTemplateListView(LoginRequiredMixin, ListView):
    """Представление для списка шаблонов стажировки"""
    model = Template
    template_name = 'internships/template_list.html'
    context_object_name = 'templates'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Создать стажировку'
        return context

class CreateInternshipFromScratchView(LoginRequiredMixin, View):
    def get(self, request):
        internship = Internship.objects.create(
            title='Новая стажировка',
            created_by=request.user
        )
        return redirect(f"{reverse_lazy('create_from_empty_page')}?id={internship.id}")

class BlockEditorView(LoginRequiredMixin, UpdateView):
    """Представление для редактора блоков"""
    model = Internship
    template_name = 'internships/block_editor.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['blocks'] = Block.objects.filter(internship=self.object)
        context['block_types'] = [
            {'name': 'Обложка', 'type': 'cover'},
            {'name': 'О проекте', 'type': 'about'},
            {'name': 'Заголовок', 'type': 'heading'},
            {'name': 'Текстовый блок', 'type': 'text'},
            {'name': 'Изображение', 'type': 'image'},
            {'name': 'Форма', 'type': 'form'},
            {'name': 'Кнопка', 'type': 'button'},
            {'name': 'Видео', 'type': 'video'},
        ]
        return context

    def form_valid(self, form):
        return redirect('internship_detail', pk=self.object.pk)


class CreateInternshipFromTemplate(LoginRequiredMixin, CreateView):
    """Создание стажировки из шаблона"""
    model = Internship
    template_name = 'internships/create_from_template.html'
    fields = ['title', 'description']
    success_url = reverse_lazy('block_editor')

    def form_valid(self, form):
        # Получаем шаблон
        template_id = self.kwargs.get('template_id')
        template = get_object_or_404(Template, id=template_id)

        # Создаем новую стажировку
        internship = form.save(commit=False)
        internship.created_by = self.request.user
        internship.save()

        # Копируем блоки из шаблона
        for template_block in template.blocks.all():
            Block.objects.create(
                internship=internship,
                type=template_block.type,
                content=template_block.content,
                order=template_block.order
            )

        # Перенаправляем на редактор блоков
        return redirect('block_editor', pk=internship.pk)


# API для работы с блоками
def create_block(request, internship_id):
    """Добавление нового блока"""
    if request.method == 'POST':
        block_type = request.POST.get('type')
        internship = get_object_or_404(Internship, id=internship_id)

        # Определение порядка блока
        last_order = Block.objects.filter(internship=internship).order_by('-order').first()
        order = last_order.order + 1 if last_order else 0

        block = Block.objects.create(
            internship=internship,
            type=block_type,
            content={},
            order=order
        )

        return JsonResponse({
            'status': 'success',
            'block_id': block.id
        })

    return JsonResponse({'status': 'error'}, status=400)


def update_block(request, block_id):
    """Обновление содержимого блока"""
    if request.method == 'POST':
        block = get_object_or_404(Block, id=block_id)
        content = request.POST.get('content', '{}')

        block.content = content
        block.save()

        return JsonResponse({
            'status': 'success'
        })

    return JsonResponse({'status': 'error'}, status=400)


def delete_block(request, block_id):
    """Удаление блока"""
    if request.method == 'POST':
        block = get_object_or_404(Block, id=block_id)
        block.delete()

        return JsonResponse({
            'status': 'success'
        })

    return JsonResponse({'status': 'error'}, status=400)


def create_from_empty_page(request):
    internship_id = request.GET.get('id')
    if not internship_id:
        raise Http404("Не передан id стажировки")
    internship = get_object_or_404(Internship, id=internship_id) if internship_id else Internship.objects.first()

    blocks_data = []
    for block in internship.blocks.all():
        blocks_data.append({
            'id': block.id,
            'type': block.type,
            'content': block.content,
            'texts': [{'text': t.text} for t in block.texts.all()],
            'images': [{'image': t.image.url} for t in block.images.all()],
            'buttons': [{'label': b.label, 'style': b.style} for b in block.buttons.all()],
            'videos': [{'video_url': v.video_url} for v in block.videos.all()],
        })

    context = {
        'internship': internship,
        'blocks': json.dumps(blocks_data, cls=DjangoJSONEncoder),
    }
    return render(request, 'internships/create_from_empty_page.html', context)


@csrf_exempt
def add_block_content(request, internship_id):
    """Добавление контента в блок"""
    if request.method == 'POST':
        block_type = request.POST.get('type')
        internship = get_object_or_404(Internship, id=internship_id)

        # Создаем новый блок
        last_order = Block.objects.filter(internship=internship).order_by('-order').first()
        order = last_order.order + 1 if last_order else 0

        block = Block.objects.create(
            internship=internship,
            type=block_type,
            order=order
        )

        # Обрабатываем разные типы блоков
        if block_type in ['cover', 'image']:
            image_file = request.FILES.get('image')
            if image_file:
                # Сохраняем изображение
                image_item = ImageItem.objects.create(
                    block=block,
                    image=image_file,  # Используем напрямую файл
                    order=0
                )
                # Форсируем сохранение URL
                image_item.save()

                return JsonResponse({
                    'status': 'success',
                    'block_id': block.id,
                    'image_url': image_item.image.url  # Возвращаем полный URL
                })

        elif block_type in ['about', 'heading', 'text']:
            text_content = request.POST.get('text', '')
            if text_content:
                TextItem.objects.create(
                    block=block,
                    text=text_content,
                    order=0
                )

        elif block_type == 'button':
            label = request.POST.get('label', 'Кнопка')
            style = request.POST.get('style', 'btn-primary')
            ButtonItem.objects.create(
                block=block,
                label=label,
                style=style,
                order=0
            )

        elif block_type == 'video':
            video_url = request.POST.get('video_url', '')
            if video_url:
                VideoItem.objects.create(
                    block=block,
                    video_url=video_url
                )

        return JsonResponse({'status': 'success', 'block_id': block.id})

    return JsonResponse({'status': 'error'}, status=400)


def get_blocks_json(request, internship_id):
    """Возвращает JSON с блоками для стажировки"""
    internship = get_object_or_404(Internship, id=internship_id)

    blocks_data = []
    for block in internship.blocks.all():
        blocks_data.append({
            'id': block.id,
            'type': block.type,
            'content': block.content,
            'texts': [{'text': t.text} for t in block.texts.all()],
            'images': [{'image': t.image.url} for t in block.images.all()],
            'buttons': [{'label': b.label, 'style': b.style} for b in block.buttons.all()],
            'videos': [{'video_url': v.video_url} for v in block.videos.all()],
        })

    return JsonResponse(blocks_data, safe=False)


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('my_internships')
    else:
        form = UserCreationForm()

    return render(request, 'internships/register.html', {'form': form})

from django.views.decorators.http import require_POST

@require_POST
def publish_internship(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id, created_by=request.user)
    internship.is_published = True
    internship.save()

    return JsonResponse({'status': 'success'})

@require_POST
@csrf_exempt
def update_internship_title(request, internship_id):
    internship = get_object_or_404(Internship, id=internship_id, created_by=request.user)
    data = json.loads(request.body)
    new_title = data.get('title', '').strip()
    if new_title:
        internship.title = new_title
        internship.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Пустой заголовок'}, status=400)

@require_http_methods(["DELETE"])
def delete_internship(request, pk):
    try:
        internship = Internship.objects.get(pk=pk, created_by=request.user)
        internship.delete()
        return JsonResponse({'status': 'success'})
    except Internship.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Стажировка не найдена'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@login_required
def create_internship_from_template(request):
    if request.method == 'POST':
        template_id = request.POST.get('template_id')
        try:
            # Создаем новую стажировку
            internship = Internship.objects.create(
                title=request.POST.get('title'),
                description=request.POST.get('description'),
                created_by=request.user,
                is_published=False
            )

            # Получаем шаблон (если нужен)
            template = Template.objects.get(id=template_id) if template_id else None

            # Здесь можно добавить копирование блоков из шаблона в стажировку
            if template:
                for block in template.blocks.all():
                    new_block = Block.objects.create(
                        internship=internship,
                        type=block.type,
                        content=block.content,
                        order=block.order
                    )

                    # Копируем связанные объекты (изображения, тексты и т.д.)
                    if block.type == 'image':
                        for image in block.images.all():
                            ImageItem.objects.create(
                                block=new_block,
                                image=image.image,
                                order=image.order
                            )
                    elif block.type == 'text':
                        for text in block.texts.all():
                            TextItem.objects.create(
                                block=new_block,
                                text=text.text,
                                order=text.order
                            )
                    # Аналогично для других типов блоков

            messages.success(request, 'Стажировка успешно создана!')
            return redirect('internship_detail', pk=internship.id)

        except Exception as e:
            messages.error(request, f'Ошибка при создании стажировки: {str(e)}')
            return redirect('template_list')

    return redirect('template_list')