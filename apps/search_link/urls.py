from django.urls import path
from search_link import views

urlpatterns = [
    path('', views.search_link, name='search_link'),  # Search page
    # path('results/<uuid:job_id>/', views.results, name='results'),
    # path('user_left/', views.user_left, name='user_left'),
    # path('stop-job/<str:job_id>/', views.stop_job, name='stop_job'),
    # path('job_status/<str:job_id>/', views.job_status, name='job_status'),
]