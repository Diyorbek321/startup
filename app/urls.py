from django.urls import path,include
from app.views import Index

urlpatterns = [
    path('home/', Index.as_view(), name='home'),
    path('',include('chatbot.urls'))
]
