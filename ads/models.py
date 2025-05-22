from django.contrib.auth.models import User
from django.db import models


class Ad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)

    class Category(models.TextChoices):
        BOOKS = 'books', 'Книги'
        CLOTHES = 'clothes', 'Одежда'
        TECH = 'tech', 'Техника'
        FURNITURE = 'furniture', 'Мебель'
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.BOOKS)

    class Condition(models.TextChoices):
        NEW = 'new', 'Новый'
        USED = 'used', 'Б/у'
    condition = models.CharField(max_length=20, choices=Condition.choices, default=Condition.NEW)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title} ({self.user.username})'


class ExchangeProposal(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        ACCEPTED = 'accepted', 'Принята'
        REJECTED = 'rejected', 'Отклонена'
    ad_sender = models.ForeignKey('Ad', related_name='sent_proposals', on_delete=models.CASCADE)

    ad_receiver = models.ForeignKey('Ad', related_name='received_proposals', on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Обмен {self.ad_sender} → {self.ad_receiver} ({self.status})'
