from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/',              views.login_view,    name='login'),
    path('register/',           views.register_view, name='register'),
    path('logout/',             views.logout_view,   name='logout'),

    # Feed & Upload
    path('',                    views.feed,          name='feed'),
    path('upload/',             views.upload_file,   name='upload_file'),

    # File actions
    path('file/<int:pk>/',      views.file_detail,   name='file_detail'),
    path('file/<int:pk>/delete/',views.delete_file,  name='delete_file'),
    path('file/<int:pk>/like/', views.toggle_like,   name='toggle_like'),
    path('file/<int:pk>/download/', views.download_file, name='download_file'),

    # Comment
    path('comment/<int:pk>/delete/', views.delete_comment, name='delete_comment'),

    # Profile
    path('profile/<str:username>/', views.profile_view, name='profile'),
]