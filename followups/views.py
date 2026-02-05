from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from .models import FollowUp, PublicViewLog
from django.shortcuts import redirect, get_object_or_404
from .forms import FollowUpForm


@login_required
def followup_create(request):
    if request.method == 'POST':
        form = FollowUpForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.clinic = request.user.userprofile.clinic
            followup.created_by = request.user
            followup.save()
            return redirect('dashboard')
    else:
        form = FollowUpForm()
    return render(request, 'followups/form.html', {'form': form})


@login_required
def followup_edit(request, pk):
    followup = get_object_or_404(
        FollowUp,
        pk=pk,
        clinic=request.user.userprofile.clinic
    )

    if request.method == 'POST':
        form = FollowUpForm(request.POST, instance=followup)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = FollowUpForm(instance=followup)

    return render(request, 'followups/form.html', {'form': form})

@login_required
def followup_mark_done(request, pk):
    if request.method == 'POST':
        followup = get_object_or_404(
            FollowUp,
            pk=pk,
            clinic=request.user.userprofile.clinic
        )
        followup.status = 'done'
        followup.save()
    return redirect('dashboard')

@login_required
def dashboard(request):
    clinic = request.user.userprofile.clinic

    followups = FollowUp.objects.filter(
        clinic=clinic
    ).annotate(
        view_count=Count('publicviewlog')
    )

    total = followups.count()
    pending = followups.filter(status='pending').count()
    done = followups.filter(status='done').count()

    context = {
        'followups': followups,
        'total': total,
        'pending': pending,
        'done': done
    }
    return render(request, 'followups/dashboard.html', context)


def public_followup(request, token):
    followup = get_object_or_404(FollowUp, public_token=token)

    PublicViewLog.objects.create(
        followup=followup,
        user_agent=request.META.get('HTTP_USER_AGENT'),
        ip_address=request.META.get('REMOTE_ADDR')
    )

    message = (
        "Please contact the clinic."
        if followup.language == 'en'
        else "कृपया क्लिनिक से संपर्क करें।"
    )

    return render(
        request,
        'followups/public.html',
        {'message': message}
    )