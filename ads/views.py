from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST

from ads.forms import AdForm, ExchangeProposalForm

from ads.models import Ad, ExchangeProposal


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
        messages.error(request, 'Вы не можете удалить чужое объявление.')
        return redirect('ads:ad_detail', pk=ad.pk)

    if request.method == 'POST':
        ad.delete()
        messages.success(request, 'Объявление удалено.')
        return redirect('ads:list_ads')

    return render(request, 'ads/ad_confirm_delete.html', {'ad': ad})


@login_required
def update_ad(request, pk):
    ad = get_object_or_404(Ad, pk=pk)

    if ad.user != request.user:
        messages.error(request, 'Вы не можете редактировать чужое объявление.')
        return redirect('ads:ad_detail', pk=ad.pk)

    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, 'Объявление обновлено.')
            return redirect('ads:ad_detail', pk=ad.pk)
    else:
        form = AdForm(instance=ad)

    return render(request, 'ads/ad_form.html', {'form': form, 'ad': ad})


@login_required
def create_proposal(request, ad_id):
    target_ad = get_object_or_404(Ad, pk=ad_id)

    if target_ad.user == request.user:
        messages.error(request, 'Нельзя предлагать обмен самому себе.')
        return redirect('ads:ad_detail', ad_id)

    if request.method == 'POST':
        form = ExchangeProposalForm(request.POST, user=request.user)
        if form.is_valid():
            proposal = form.save(commit=False)
            proposal.ad_receiver = target_ad
            proposal.save()
            messages.success(request, 'Предложение отправлено.')
            return redirect('ads:ad_detail', ad_id)
    else:
        form = ExchangeProposalForm(user=request.user)

    return render(request, 'ads/proposal_form.html', {'form': form, 'target_ad': target_ad})


@login_required
def list_proposals(request):
    view_mode = request.GET.get('view', 'received')
    status_filter = request.GET.get('status')
    user_filter = request.GET.get('user')

    if view_mode == 'sent':
        proposals = ExchangeProposal.objects.filter(ad_sender__user=request.user)
        if status_filter:
            proposals = proposals.filter(status=status_filter)
        if user_filter:
            proposals = proposals.filter(ad_receiver__user__username__icontains=user_filter)
    else:
        proposals = ExchangeProposal.objects.filter(ad_receiver__user=request.user)
        if status_filter:
            proposals = proposals.filter(status=status_filter)
        if user_filter:
            proposals = proposals.filter(ad_sender__user__username__icontains=user_filter)

    return render(
        request,
        'ads/list_proposals.html',
        {
        'view_mode': view_mode,
        'proposals': proposals,
        'status_filter': status_filter or '',
        'user_filter': user_filter or '',
        }
    )


@login_required
def accept_proposal(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, pk=proposal_id)

    if proposal.ad_receiver.user != request.user:
        messages.error(request, 'Вы не можете принять предолжение адресованое другому пользователю.')
        return redirect('ads:list_proposals')

    if request.method == 'POST':
        proposal.status = ExchangeProposal.Status.ACCEPTED
        proposal.save()

        messages.success(request, 'Предложение принято!')
        return redirect('ads:list_proposals')

    return render(request, 'ads/confirm_accept.html', {'proposal': proposal})


@require_POST
@login_required
def reject_proposal(request, proposal_id):
    proposal = get_object_or_404(ExchangeProposal, id=proposal_id)

    if proposal.ad_receiver.user != request.user:
        messages.error(request, 'Вы не можете отменить это предложение.')
        return redirect('ads:list_proposals')

    if proposal.status != ExchangeProposal.Status.PENDING:
        messages.warning(request, 'Это предложение уже обработано и не может быть отменено.')
        return redirect('ads:list_proposals')

    proposal.status = ExchangeProposal.Status.REJECTED
    proposal.save()

    messages.success(request, 'Предложение успешно отменено.')
    return redirect('ads:list_proposals')
