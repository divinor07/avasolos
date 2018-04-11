from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Turma, Enrollment, Announcement, Lesson, Material
from .forms import ContactTurma, CommentForm
from .decorators import enrollment_required

def index(request):
    turmas = Turma.objects.all()
    template_name = 'turmas/index.html'
    context = {
        'turmas': turmas
    }
    return render(request, template_name, context)

# def details(request, pk):
#     turma = get_object_or_404(Turma, pk=pk)
#     context = {
#         'turma': turma
#     }
#     template_name = 'turmas/details.html'
#     return render(request, template_name, context)

def details(request, slug):
    turma = get_object_or_404(Turma, slug=slug)
    context = {}
    if request.method == 'POST':
        form = ContactTurma(request.POST)
        if form.is_valid():
            context['is_valid'] = True
            form.send_mail(turma)
            form = ContactTurma()
    else:
        form = ContactTurma()
    context['form'] = form
    context['turma'] = turma
    template_name = 'turmas/details.html'
    return render(request, template_name, context)

@login_required
def enrollment(request, slug):
    turma = get_object_or_404(Turma, slug=slug)
    enrollment, created = Enrollment.objects.get_or_create(
        user=request.user, turma=turma
    )
    if created:
        # enrollment.active()
        messages.success(request, 'Você foi matriculado na turma com sucesso')
    else:
        messages.info(request, 'Você já está matriculado na turma')

    return redirect('accounts:dashboard')

@login_required
def undo_enrollment(request, slug):
    turma = get_object_or_404(Turma, slug=slug)
    enrollment = get_object_or_404(
        Enrollment, user=request.user, turma=turma
    )
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Sua matricula foi cancelada com sucesso')
        return redirect('accounts:dashboard')
    template = 'turmas/undo_enrollment.html'
    context = {
        'enrollment': enrollment,
        'turma': turma,
    }
    return render(request, template, context)

@login_required
@enrollment_required
def announcements(request, slug):
    turma = request.turma
    template = 'turmas/announcements.html'
    context = {
        'turma': turma,
        'announcements': turma.announcements.all()
    }
    return render(request, template, context)

@login_required
@enrollment_required
def show_announcement(request, slug, pk):
    turma = request.turma
    announcement = get_object_or_404(turma.announcements.all(), pk=pk)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.announcement = announcement
        comment.save()
        form = CommentForm()
        messages.success(request, 'Seu comentário foi enviado com sucesso')
    template = 'turmas/show_announcement.html'
    context = {
        'turma': turma,
        'announcement': announcement,
        'form': form,
    }
    return render(request, template, context)

@login_required
@enrollment_required
def lessons(request, slug):
    turma = request.turma
    template = 'turmas/lessons.html'
    lessons = turma.release_lessons()
    if request.user.is_staff:
        lessons = turma.lessons.all()
    context = {
        'turma': turma,
        'lessons': lessons
    }
    return render(request, template, context)

@login_required
@enrollment_required
def lesson(request, slug, pk):
    turma = request.turma
    lesson = get_object_or_404(Lesson, pk=pk, turma=turma)
    if not request.user.is_staff and not lesson.is_available():
        messages.error(request, 'Esta aula não está disponível')
        return redirect('turmas:lessons', slug=turma.slug)
    template = 'turmas/lesson.html'
    context = {
        'turma': turma,
        'lesson': lesson
    }
    return render(request, template, context)

@login_required
@enrollment_required
def material(request, slug, pk):
    turma = request.turma
    material = get_object_or_404(Material, pk=pk, lesson__turma=turma)
    lesson = material.lesson
    if not request.user.is_staff and not lesson.is_available():
        messages.error(request, 'Este material não está disponível')
        return redirect('turmas:lesson', slug=turma.slug, pk=lesson.pk)
    if not material.is_embedded():
        return redirect(material.file.url)
    template = 'turmas/material.html'
    context = {
        'turma': turma,
        'lesson': lesson,
        'material': material,
    }
    return render(request, template, context)