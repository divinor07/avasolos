from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.conf import settings

from model_mommy import mommy

from avasolos.Turmas.models import Turma


class TurmaManagerTestCase(TestCase):

    def setUp(self):
        self.turmas_django = mommy.make(
            'turmas.Turma', name='Python na Web com Django', _quantity=5
        )
        self.turmas_dev = mommy.make(
            'turmas.Turma', name='Python para Devs', _quantity=10
        )
        self.client = Client()

    def tearDown(self):
        Turma.objects.all().delete()

    def test_turma_search(self):
        search = Turma.objects.search('django')
        self.assertEqual(len(search), 5)
        search = Turma.objects.search('devs')
        self.assertEqual(len(search), 10)
        search = Turma.objects.search('python')
        self.assertEqual(len(search), 15)
