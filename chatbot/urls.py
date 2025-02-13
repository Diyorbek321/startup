from django.urls import path
from .views import ChatBotView

urlpatterns = [
    path("get_response/", ChatBotView.as_view(), name="chatbot_response"),
]
