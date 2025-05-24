from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ads.forms import AdForm, ExchangeProposalForm

from ads.models import Ad


def list_ads(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    condition = request.GET.get('condition')

    ads = Ad.objects.all()

    if query:
        ads = ads.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    if category:
        ads = ads.filter(category=category)
    if condition:
        ads = ads.filter(condition=condition)

    paginator = Paginator(ads, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ads/list_ads.html', {
        'page_obj': page_obj,
        'query': query or '',
        'category': category or '',
        'condition': condition or '',
        'categories': Ad.Category.choices,
        'conditions': Ad.Condition.choices,
    })


@login_required
def create_ad(request):
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            messages.success(request, 'Объявление успешно создано!')
            return redirect('ads:ad_detail', ad.id)
    else:
        form = AdForm()

    return render(request, 'ads/ad_form.html', {'form': form})


def ad_detail(request, pk):
    ad = get_object_or_404(Ad, pk=pk)
    return render(request, 'ads/ad_detail.html', {'ad': ad})


@login_required
def delete_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        messages.error(request, "Вы не можете удалить чужое объявление.")
        return redirect('ads:ad_detail', pk=ad.pk)

    if request.method == "POST":
        ad.delete()
        messages.success(request, "Объявление удалено.")
        return redirect('ads:list_ads')

    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


@login_required
def update_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        messages.error(request, "Вы не можете редактировать чужое объявление.")
        return redirect('ads:ad_detail', pk=ad.pk)

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, "Объявление обновлено.")
            return redirect('ads:ad_detail', pk=ad.pk)
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/ad_form.html', {'form': form, 'ad': ad})


@login_required
def create_proposal(request, ad_id):
    target_ad = get_object_or_404(Ad, pk=ad_id)

    if target_ad.user == request.user:
        messages.error(request, "Нельзя предлагать обмен самому себе.")
        return redirect('ads:ad_detail', ad_id)

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = target_ad
            proposal.save()
            messages.success(request, "Предложение отправлено.")
            return redirect('ads:ad_detail', ad_id)
    else:
        form = ExchangeProposalForm(user=request.user)

    return render(request, 'ads/proposal_form.html', {'form': form, 'target_ad': target_ad})

