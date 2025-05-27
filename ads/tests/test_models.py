from django.test import TestCase
from django.contrib.auth import get_user_model
from ads.models import Ad, ExchangeProposal

User = get_user_model()

class AdModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='tester', password='pass123')
        self.ad = Ad.objects.create(
            user=self.user,
            title='Гитара Fender',
            description='Почти новая',
            category='tech',
            condition='used',
        )

    def test_ad_creation(self):
        self.assertEqual(self.ad.title, 'Гитара Fender')
        self.assertEqual(self.ad.condition, 'used')
        self.assertEqual(self.ad.category, 'tech')
        self.assertEqual(str(self.ad), f'{self.ad.title} ({self.ad.user.username})')
        self.assertIsNotNone(self.ad.created_at)

class ExchangeProposalModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='sender', password='pass123')
        self.user2 = User.objects.create_user(username='receiver', password='pass456')

        self.ad_sender = Ad.objects.create(
            user=self.user1, title='Велосипед', description='GT', category='tech', condition='used'
        )
        self.ad_receiver = Ad.objects.create(
            user=self.user2, title='Сноуборд', description='Burton', category='tech', condition='new'
        )

        self.proposal = ExchangeProposal.objects.create(
            ad_sender=self.ad_sender,
            ad_receiver=self.ad_receiver,
            comment='Давай махнёмся!',
        )

    def test_proposal_default_status(self):
        self.assertEqual(self.proposal.status, 'pending')

    def test_proposal_str(self):
        self.assertIn('Велосипед', str(self.proposal))
        self.assertIn('Сноуборд', str(self.proposal))

    def test_proposal_created_at(self):
        self.assertIsNotNone(self.proposal.created_at)
