from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from typing import Dict, List, Optional
import re
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatPattern:
    def __init__(self, patterns: List[str], responses: List[str], requires_context: bool = False):
        self.patterns = [re.compile(pattern, re.IGNORECASE) for pattern in patterns]
        self.responses = responses
        self.requires_context = requires_context


CHAT_PATTERNS = [
    # Salomlashish
    ChatPattern(
        patterns=[r"\b(salom|hi|hello|hey|assalomu alaykum)\b"],
        responses=[
            "Salom! 👋 Sizga qanday yordam bera olaman?",
            "Salom, hush kelibsiz! Qanday yordam bera olaman?",
            "Hey! Qanday yordam bera olaman?",
            "Assalomu alaykum! Bugun sizga qanday foydam tegishi mumkin?"
        ]
    ),
    # Hol-ahvol so'rash
    ChatPattern(
        patterns=[r"\b(qandaysiz|ahvoling qanday|yaxshimisiz)\b"],
        responses=[
            "Yaxshi, rahmat! Siz-chi? 😊",
            "Ajoyib! Bugun qanday yordam bera olaman?",
            "Zo'rman! Nima yordam kerak?",
            "Yaxshi! Sizga qanday ko'mak bera olaman?"
        ]
    ),
    # Minnatdorchilik
    ChatPattern(
        patterns=[r"\b(rahmat|katta rahmat|raxmat|tashakkur)\b"],
        responses=[
            "Arzimaydi! 😊",
            "Sizga yordam bera olganimdan xursandman! 🌟",
            "Marhamat! Yana savollaringiz bo'lsa, bemalol so'rang!",
            "Siz uchun har doim tayyorman! 🤗"
        ]
    ),
    # Xayrlashish
    ChatPattern(
        patterns=[r"\b(xayr|hayr|ko'rishguncha|salomat bo'ling)\b"],
        responses=[
            "Xayr! Yaxshi kun tilayman! 👋",
            "Ko'rishguncha! O'zingizga qarang! 😊",
            "Hayr! Yana uchrashguncha!",
            "Salomat bo'ling! Agar yordam kerak bo'lsa, men shu yerdaman!"
        ]
    ),
    # Yordam
    ChatPattern(
        patterns=[r"\b(yordam|ko'mak|maslahat)\b"],
        responses=[
            "Albatta, qanday yordam bera olaman? 🤝",
            "Sizga qanday ko'mak kerak? Tafsilot berib o'ting!",
            "Savolingizni aniqroq tushuntirsangiz, yaxshi bo'lardi!",
            "Yordamga tayyorman! Nima masala bo'yicha yordam kerak?"
        ]
    ),
    # Ob-havo haqida (misol javob)
    ChatPattern(
        patterns=[r"\b(ob-havo|havo qanday|ertaga havo)\b"],
        responses=[
            "Men real vaqtdagi ob-havo ma'lumotlarini ko'ra olmayman, ammo siz ob-havo ilovalaridan foydalanishingiz mumkin! ☀️",
            "Aniq bilmayman, lekin sizga eng yaqin ob-havo xizmatini tavsiya qila olaman! ☁️"
        ]
    ),
    # Dasturlash bo'yicha yordam
    ChatPattern(
        patterns=[r"\b(dasturlash yordam|kod yozish yordam|proyekt yordam)\b"],
        responses=[
            "Dasturlash bo'yicha yordam kerakmi? Qaysi til yoki framework bilan ishlayapsiz? 💻",
            "Albatta! Qanday loyiha ustida ishlayapsiz? Qanday muammo bor? 🚀",
            "Kod yozishda yordam kerakmi? Muammoni batafsilroq tushuntiring! 🛠️"
        ]
    ),
    ChatPattern(
        patterns=['Kompaniya haqida'],
        responses=[
            "Kompaniyamiz 5 yildan beri ishlab kelmoqda "
            'Biz qanday ishlaymiz?'
            'Biz mijozlarga ularning hohish istaklaridan kelib chiqgan holda dasturiy taminoat yaratishga yordam beramiz '
            'Qanday dasturiy taminot yaratamiz? '
            'Biz biznesingiz uchun it yechimlarini taklif qilamiz yani tuli xil web saytlar chatbot crm erp telegram bot tizimlarini taklif qilamiz'
        ]
    )
]

DEFAULT_RESPONSES = [
    "Tafsilotlarni ulashganingiz uchun rahmat tez orada bizning agentimiz siga javib qaytaradi",
    # "Men hali o'rganishda davom etyapman! Iltimos, boshqacha shaklda so'rab ko'ring. 🌱",
    "Bu haqda aniq bilmayman, lekin sizga yordam berishga harakat qilaman!"
]


class ChatBotService:
    @staticmethod
    def get_bot_response(message: str) -> str:
        """
        Enhanced bot response generator with better pattern matching and context awareness
        """
        if not message:
            return "I didn't receive any message. How can I help you? 🤔"

        message = message.strip().lower()
        logger.info(f"Received message: {message}")

        # Check for dynamic responses first
        for pattern in CHAT_PATTERNS:
            for regex in pattern.patterns:
                if regex.search(message):
                    response = random.choice(pattern.responses)
                    # Handle callable responses (like time/date)
                    if callable(response):
                        response = response()
                    logger.info(f"Responding with: {response}")
                    return response

        # If no pattern matches, return default response
        response = random.choice(DEFAULT_RESPONSES)
        logger.info(f"No pattern match. Using default response: {response}")
        return response


class ChatBotView(APIView):
    def post(self, request, *args, **kwargs) -> Response:
        """
        Enhanced POST handler with better error handling and response formatting
        """
        try:
            user_message = request.data.get("message", "")
            if not isinstance(user_message, str):
                return Response(
                    {"error": "Message must be a string"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get bot response
            bot_response = ChatBotService.get_bot_response(user_message)

            # Add typing delay simulation flag
            response_data = {
                "response": bot_response,
                "shouldSimulateTyping": True  # Frontend can use this to show typing indicator
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
