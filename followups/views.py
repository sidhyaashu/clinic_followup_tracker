from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count
from .models import FollowUp, PublicViewLog, UserProfile
from django.shortcuts import redirect, get_object_or_404
from .forms import FollowUpForm
from django.utils.timezone import now
from django.contrib import messages




@login_required
def followup_create(request):
    if request.method == 'POST':
        form = FollowUpForm(request.POST)
        if form.is_valid():
            followup = form.save(commit=False)
            followup.clinic = request.user.userprofile.clinic
            followup.created_by = request.user
            followup.save()
            
            messages.success(request, "Follow-up created successfully.")
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
            
            messages.success(request, "Follow-up updated successfully.")
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
        
        messages.success(request, "Follow-up marked as done.")
    return redirect('dashboard')

@login_required
def dashboard(request):
    try:
        clinic = request.user.userprofile.clinic
    except UserProfile.DoesNotExist:
        messages.error(request, "No clinic assigned. Contact admin.")
        return redirect("login")

    followups = FollowUp.objects.filter(clinic=clinic)

    status = request.GET.get('status')
    if status:
        followups = followups.filter(status=status)

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if start_date:
        followups = followups.filter(due_date__gte=start_date)

    if end_date:
        followups = followups.filter(due_date__lte=end_date)

    followups = followups.annotate(
        view_count=Count('views')
    )

    context = {
        'followups': followups,
        'total': followups.count(),
        'pending': followups.filter(status='pending').count(),
        'done': followups.filter(status='done').count(),
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