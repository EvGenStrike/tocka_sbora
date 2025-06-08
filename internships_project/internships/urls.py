from django.contrib.auth.views import LogoutView
from django.urls import path
from . import views
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.my_internships, name='my_internships'),
    path('all/', views.all_internships, name='all_internships'),
    path('templates/', views.InternshipTemplateListView.as_view(), name='template_list'),
path('create/', views.create_internship, name='create_internship'),
    path('profile/', views.profile_view, name='profile'),
    path('internship/create/template/<int:template_id>/',
         views.CreateInternshipFromTemplate.as_view(),
         name='create_from_template'),
    path('internship/<int:pk>/editor/', views.BlockEditorView.as_view(), name='block_editor'),
path('api/internship/<int:internship_id>/block/create/',
         views.create_block,
         name='create_block'),
    path('api/block/<int:block_id>/update/',
         views.update_block,
         name='update_block'),
    path('api/block/<int:block_id>/delete/',
         views.delete_block,
         name='delete_block'),
    path('create_from_empty_page/', views.create_from_empty_page, name='create_from_empty_page'),
    path('internships/<int:internship_id>/add-block-content/', add_block_content, name='add_block_content'),
    path('internships/<int:internship_id>/get-blocks-json/', get_blocks_json, name='get_blocks_json'),
path('accounts/login/', auth_views.LoginView.as_view(template_name='internships/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/register/', views.register, name='register'),
path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
path('internships/<int:internship_id>/publish/', views.publish_internship, name='publish_internship'),
path('internships/create-from-empty/', CreateInternshipFromScratchView.as_view(), name='create_from_empty'),
path('internships/<int:internship_id>/update-title/', views.update_internship_title, name='update_internship_title'),
    path('internships/<int:pk>/delete/', views.delete_internship, name='delete_internship'),
path('internship/create-from-template/', create_internship_from_template, name='create_internship_from_template'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)