from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.core.files.storage import FileSystemStorage
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import Reading
from .forms import NewUserForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import os
from django.utils.timezone import make_naive
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.views.decorators.http import require_POST
from recognition.image_recognition import process_image
from recognition.water_image_recognition import process_water_image
import logging

def index(request):
    return render(request, 'main/index.html')

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        logger.info('POST запрос на регистрацию')
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info('Форма регистрации валидна, пользователь создан: %s', user.username)
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('index')
        else:
            logger.error('Ошибка при регистрации: %s', form.errors)
            messages.error(request, 'Ошибка при регистрации. Пожалуйста, попробуйте снова.')
    else:
        logger.info('GET запрос на регистрацию')
        form = NewUserForm()
    return render(request, 'main/register.html', {'form': form})

def login_request(request):
    if request.method == 'POST':
        logger.info('POST запрос на вход')
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                logger.info('Пользователь аутентифицирован: %s', username)
                login(request, user)
                messages.info(request, f'Вы вошли как {username}.')
                return redirect('index')
            else:
                logger.error('Не удалось аутентифицировать пользователя: %s', username)
                messages.error(request, 'Неверное имя пользователя или пароль.')
        else:
            logger.error('Форма входа не валидна: %s', form.errors)
            messages.error(request, 'Неверное имя пользователя или пароль.')
    else:
        logger.info('GET запрос на вход')
        form = AuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


@login_required(login_url='/login_required/')
def upload(request):
    return render(request, 'main/upload.html')


@login_required(login_url='/login_required/')
def water_upload(request):
    return render(request, 'main/water_readings.html')

@login_required(login_url='/login_required/')
def readings(request):
    user_readings = Reading.objects.filter(user=request.user).order_by('-date_posted')
    return render(request, 'main/readings.html', {'readings': user_readings})

def login_required_view(request):
    return render(request, 'main/login_required.html')
@csrf_exempt
@login_required
def recognize(request):
    if request.method == 'POST' and request.FILES.get('image'):
        file = request.FILES['image']

        if not allowed_file(file.name):
            return JsonResponse({'error': 'File type not allowed'}, status=400)

        fs = FileSystemStorage()
        filename = fs.save(os.path.join('uploads', file.name), file)
        uploaded_file_url = fs.url(filename)

        save_path = fs.path(filename)
        final_reading = process_image(save_path)

        return JsonResponse({
            'success': True,
            'final_reading': final_reading,
            'image_url': uploaded_file_url
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
@login_required
def water_recognize(request):
    if request.method == 'POST' and request.FILES.get('image'):
        file = request.FILES['image']

        if not allowed_file(file.name):
            return JsonResponse({'error': 'File type not allowed'}, status=400)

        fs = FileSystemStorage()
        filename = fs.save(os.path.join('uploads', file.name), file)
        uploaded_file_url = fs.url(filename)

        save_path = fs.path(filename)
        final_reading = process_water_image(save_path)

        return JsonResponse({
            'success': True,
            'final_reading': final_reading,
            'image_url': uploaded_file_url
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


def allowed_file(filename):
    """Проверка разрешенного расширения файла."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@require_POST
@login_required
def delete_readings(request):
    ids_to_delete = request.POST.getlist('delete-ids')
    Reading.objects.filter(id__in=ids_to_delete, user=request.user).delete()
    return HttpResponseRedirect(reverse('readings'))

@require_POST
@login_required
def delete_all_readings(request):
    Reading.objects.filter(user=request.user).delete()
    return redirect('readings')

@login_required
def export_readings_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="readings.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    y = height - 50
    x = 50

    p.setFont("Helvetica-Bold", 14)
    p.drawString(x, y, "Список показаний")

    p.setFont("Helvetica", 12)
    y -= 30

    readings = Reading.objects.filter(user=request.user)

    p.drawString(x, y, "ID")
    p.drawString(x+100, y, "Дата")
    p.drawString(x+300, y, "Показания")
    y -= 20

    for reading in readings:
        naive_date = make_naive(reading.date_posted) if reading.date_posted.tzinfo else reading.date_posted
        reading_data = [
            str(reading.id),
            naive_date.strftime('%Y-%m-%d %H:%M'),
            reading.reading_value
        ]
        p.drawString(x, y, reading_data[0])
        p.drawString(x+100, y, reading_data[1])
        p.drawString(x+300, y, reading_data[2])
        y -= 20

    p.showPage()
    p.save()

    return response

@login_required
def export_readings_excel(request):
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="readings.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Readings"

    columns = ['ID', 'Дата', 'Показания']
    ws.append(columns)

    readings = Reading.objects.filter(user=request.user)
    for reading in readings:
        naive_date = make_naive(reading.date_posted) if reading.date_posted.tzinfo else reading.date_posted
        ws.append([reading.id, naive_date, reading.reading_value])

    wb.save(response)

    return response

@csrf_exempt
@login_required
def save_reading(request):
    if request.method == 'POST':
        reading_value = request.POST.get('reading')
        image_path = request.POST.get('image_path')

        if reading_value and image_path:
            reading = Reading(user=request.user, reading_value=reading_value, image_url=image_path)
            reading.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Недостаточно данных для сохранения'})

    return JsonResponse({'success': False, 'error': 'Недопустимый метод'})


@login_required
def edit_reading(request, reading_id):
    reading = get_object_or_404(Reading, id=reading_id, user=request.user)
    context = {
        'reading': reading,
        'edit_mode': True,
    }
    return render(request, 'main/edit_reading.html', context)

@login_required
def edit_water_reading(request, reading_id):
    reading = get_object_or_404(Reading, id=reading_id, user=request.user)
    context = {
        'reading': reading,
        'edit_mode': True
    }
    return render(request, 'main/water_edit_reading.html', context)

@csrf_exempt
@login_required
def save_edited_reading(request):
    if request.method == 'POST':
        reading_id = request.POST.get('reading_id')
        new_reading_value = request.POST.get('reading')
        image_file = request.FILES.get('image')

        old_reading = get_object_or_404(Reading, id=reading_id, user=request.user)

        # Удаляем старую запись
        old_reading.delete()

        # Создаем новую запись
        image_url = old_reading.image_url
        if image_file:
            image_url = save_image(image_file)

        new_reading = Reading.objects.create(
            user=request.user,
            meter_type='factory',
            reading_value=new_reading_value,
            image_url=image_url
        )

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@csrf_exempt
@login_required
def save_edited_water_reading(request):
    if request.method == 'POST':
        reading_id = request.POST.get('reading_id')
        new_reading_value = request.POST.get('reading')
        image_file = request.FILES.get('image')

        old_reading = get_object_or_404(Reading, id=reading_id, user=request.user)

        # Удаляем старую запись
        old_reading.delete()

        # Создаем новую запись
        image_url = old_reading.image_url
        if image_file:
            image_url = save_image(image_file)

        new_reading = Reading.objects.create(
            user=request.user,
            reading_value=new_reading_value,
            image_url=image_url
        )

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'})


def save_image(image_file):
    fs = FileSystemStorage()
    filename = fs.save(os.path.join('uploads', image_file.name), image_file)
    return fs.url(filename)

