from django.contrib import admin
from .models import UserProfile, FollowUp, PublicViewLog, Clinic


# Register your models here.
@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'clinic_code', 'created_at')
    search_fields = ('name', 'clinic_code')
    readonly_fields = ('clinic_code', 'created_at')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'clinic')
    search_fields = ('user__username', 'clinic__name')
    

@admin.register(FollowUp)
class FollowUpAdmin(admin.ModelAdmin):
    list_display = (
        'patient_name',
        'phone',
        'clinic',
        'due_date',
        'status',
        'language',
        'created_at'
    )
    list_filter = ('status', 'language', 'clinic')
    search_fields = ('patient_name', 'phone')
    readonly_fields = ('public_token', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
@admin.register(PublicViewLog)
class PublicViewLogAdmin(admin.ModelAdmin):
    list_display = ('followup', 'viewed_at', 'ip_address')
    readonly_fields = ('viewed_at',)    