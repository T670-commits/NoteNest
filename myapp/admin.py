from django.contrib import admin
from .models import SharedFile, Like, Comment, Profile

@admin.register(SharedFile)
class SharedFileAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'uploaded_at']
    search_fields = ['title', 'description']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'file', 'created_at']

admin.site.register(Like)
admin.site.register(Profile)