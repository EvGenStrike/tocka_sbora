from django.urls import path
from . import views

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
]