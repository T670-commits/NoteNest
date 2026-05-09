from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, Http404
from .models import SharedFile, Like, Comment, Profile
import os


# ── AUTH ───────────────────────────────────────────────────────────────────────

def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('feed')
        messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'Username and password are required.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
        else:
            user = User.objects.create_user(username=username, email=email, password=password1)
            Profile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome to NoteNest, {username}! 🎉')
            return redirect('feed')
    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ── FEED ───────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def feed(request):
    query = request.GET.get('q', '').strip()
    files = SharedFile.objects.all()
    if query:
        files = files.filter(title__icontains=query) | files.filter(description__icontains=query)
        files = files.distinct()

    # attach liked status
    liked_ids = Like.objects.filter(user=request.user).values_list('file_id', flat=True)

    return render(request, 'feed.html', {
        'files': files,
        'liked_ids': list(liked_ids),
        'query': query,
    })


# ── UPLOAD ─────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def upload_file(request):
    if request.method == 'POST':
        title       = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        file        = request.FILES.get('file')

        if not title or not file:
            messages.error(request, 'Title and file are required.')
        else:
            SharedFile.objects.create(
                user=request.user,
                title=title,
                description=description,
                file=file,
            )
            messages.success(request, 'File uploaded successfully! 🎉')
            return redirect('feed')

    return render(request, 'upload.html')


# ── FILE DETAIL ────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def file_detail(request, pk):
    shared_file = get_object_or_404(SharedFile, pk=pk)
    comments    = shared_file.comments.all()
    liked       = Like.objects.filter(user=request.user, file=shared_file).exists()

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Comment.objects.create(user=request.user, file=shared_file, body=body)
            messages.success(request, 'Comment added!')
            return redirect('file_detail', pk=pk)

    return render(request, 'file_detail.html', {
        'file': shared_file,
        'comments': comments,
        'liked': liked,
    })


# ── DELETE FILE ────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def delete_file(request, pk):
    shared_file = get_object_or_404(SharedFile, pk=pk, user=request.user)
    shared_file.file.delete()
    shared_file.delete()
    messages.success(request, 'File deleted.')
    return redirect('feed')


# ── LIKE ───────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def toggle_like(request, pk):
    shared_file = get_object_or_404(SharedFile, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, file=shared_file)
    if not created:
        like.delete()
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER', 'feed')
    return redirect(next_url)


# ── DOWNLOAD ──────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def download_file(request, pk):
    shared_file = get_object_or_404(SharedFile, pk=pk)
    file_path   = shared_file.file.path
    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'), as_attachment=True,
                                filename=shared_file.filename())
        return response
    raise Http404


# ── DELETE COMMENT ─────────────────────────────────────────────────────────────

@login_required(login_url='login')
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, user=request.user)
    file_pk = comment.file.pk
    comment.delete()
    return redirect('file_detail', pk=file_pk)


# ── PROFILE ────────────────────────────────────────────────────────────────────

@login_required(login_url='login')
def profile_view(request, username):
    profile_user = get_object_or_404(User, username=username)
    profile, _   = Profile.objects.get_or_create(user=profile_user)
    user_files   = SharedFile.objects.filter(user=profile_user)

    if request.method == 'POST' and request.user == profile_user:
        profile.bio = request.POST.get('bio', '').strip()
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        messages.success(request, 'Profile updated!')
        return redirect('profile', username=username)

    return render(request, 'profile.html', {
        'profile_user': profile_user,
        'profile': profile,
        'user_files': user_files,
        'is_own': request.user == profile_user,
    })