from django.db import models
from django.contrib.auth.models import User
import os


class SharedFile(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file        = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def filename(self):
        return os.path.basename(self.file.name)

    def extension(self):
        name, ext = os.path.splitext(self.file.name)
        return ext.lower().strip('.')

    def is_image(self):
        return self.extension() in ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg']

    def is_video(self):
        return self.extension() in ['mp4', 'webm', 'mov', 'avi']

    def is_audio(self):
        return self.extension() in ['mp3', 'wav', 'ogg', 'm4a']

    def is_pdf(self):
        return self.extension() == 'pdf'

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    class Meta:
        ordering = ['-uploaded_at']


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    file = models.ForeignKey(SharedFile, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        unique_together = ('user', 'file')


class Comment(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    file       = models.ForeignKey(SharedFile, on_delete=models.CASCADE, related_name='comments')
    body       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user.username}: {self.body[:40]}'


class Profile(models.Model):
    user   = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio    = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} profile'