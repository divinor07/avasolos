from django.template import Library

register = Library()

from avasolos.turmas.models import Enrollment

@register.inclusion_tag('turmas/templatetags/my_turmas.html')
def my_turmas(user):
    enrollments = Enrollment.objects.filter(user=user)
    context = {
        'enrollments': enrollments
    }
    return context

@register.assignment_tag
def load_my_turmas(user):
    return Enrollment.objects.filter(user=user)