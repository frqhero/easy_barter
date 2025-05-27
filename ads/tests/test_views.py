from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from ads.models import Ad, ExchangeProposal

User = get_user_model()

class ViewsTestCase(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='pass123')
        self.receiver = User.objects.create_user(username='receiver', password='pass456')

        self.ad_sender = Ad.objects.create(
            user=self.sender,
            title='Рюкзак',
            description='На 40 литров',
            category='clothes',
            condition='used'
        )

        self.ad_receiver = Ad.objects.create(
            user=self.receiver,
            title='Палатка',
            description='2-местная',
            category='tech',
            condition='new'
        )

        self.proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiver,
            comment='Давай меняться!'
        )

    def test_protected_view_redirects_unauthorized(self):
        url = reverse('ads:create_ad')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)  # редирект на логин

    def test_create_ad_authenticated(self):
        self.client.login(username='sender', password='pass123')
        url = reverse('ads:create_ad')
        data = {
            'title': 'Ноутбук',
            'description': 'Рабочий',
            'category': 'tech',
            'condition': 'used'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # редирект на детальную
        self.assertEqual(Ad.objects.count(), 3)  # было 2, стало 3

    def test_create_proposal_authenticated(self):
        self.client.login(username='sender', password='pass123')
        url = reverse('ads:create_proposal', args=[self.ad_receiver.id])
        data = {
            'ad_sender': self.ad_sender.id,
            'comment': 'Обменяемся?'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ExchangeProposal.objects.count(), 2)

    def test_accept_proposal_by_receiver(self):
        self.client.login(username='receiver', password='pass456')
        url = reverse('ads:accept_proposal', args=[self.proposal.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('ads:list_proposals'))
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, 'accepted')

    def test_reject_proposal_by_receiver(self):
        self.client.login(username='receiver', password='pass456')
        url = reverse('ads:reject_proposal', args=[self.proposal.id])
        response = self.client.post(url)
        self.assertRedirects(response, reverse('ads:list_proposals'))
        self.proposal.refresh_from_db()
        self.assertEqual(self.proposal.status, 'rejected')
