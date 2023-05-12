from django.contrib import admin
from .models import Profile

"""
Registers Profile model in the admin panel
"""


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = 'id', 'user', 'balance', 'status',

