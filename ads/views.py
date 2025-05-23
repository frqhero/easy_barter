from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ads.forms import AdForm
from ads.models import Ad


def list_ads(request):
    ads = Ad.objects.all()
    return render(request, 'ads/list_ads.html', {'ads': ads})


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
