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
    # Greetings
    ChatPattern(
        patterns=[r"\b(hi|hello|hey|howdy|hola|greetings)\b"],
        responses=[
            "Hello! 👋 How can I assist you today?",
            "Hi there! What can I help you with?",
            "Hey! Great to see you. How may I help?",
            "Welcome! How can I make your day better?"
        ]
    ),
    # How are you
    ChatPattern(
        patterns=[r"\b(how are you|how's it going|how are things)\b"],
        responses=[
            "I'm doing great, thanks for asking! How about you? 😊",
            "All good here! How can I help you today?",
            "I'm wonderful! What brings you here today?",
            "Doing excellent! Ready to assist you! 🌟"
        ]
    ),
    # Thanks
    ChatPattern(
        patterns=[r"\b(thanks|thank you|thx|appreciate it)\b"],
        responses=[
            "You're welcome! 😊",
            "Glad I could help! 🌟",
            "My pleasure! Let me know if you need anything else!",
            "Anytime! Don't hesitate to ask if you need more help!"
        ]
    ),
    # Goodbye
    ChatPattern(
        patterns=[r"\b(goodbye|bye|see you|cya|farewell)\b"],
        responses=[
            "Goodbye! Have a great day! 👋",
            "See you later! Take care! 😊",
            "Bye! Hope to chat again soon!",
            "Take care! Remember, I'm here if you need help! 🌟"
        ]
    ),
    # Help
    ChatPattern(
        patterns=[r"\b(help|assist|support)\b"],
        responses=[
            "I'd be happy to help! What do you need assistance with? 🤝",
            "Sure thing! What kind of help are you looking for?",
            "I'm here to help! Could you please specify what you need?",
            "Ready to assist! What's on your mind? 💭"
        ]
    ),
    # Time and Date
    ChatPattern(
        patterns=[r"\b(what('s| is) the time|what time is it|what('s| is) today('s| is) date)\b"],
        responses=[
            lambda: f"It's {datetime.now().strftime('%I:%M %p')} on {datetime.now().strftime('%A, %B %d, %Y')} 🕒"
        ]
    ),
    # Weather inquiry (mock response)
    ChatPattern(
        patterns=[r"\b(what('s| is) the weather|how('s| is) the weather)\b"],
        responses=[
            "I'm not connected to real-time weather data, but I can help you find a weather service! 🌤️",
            "While I can't check the weather directly, I can suggest some weather apps! ⛅"
        ]
    ),
    # Project help
    ChatPattern(
        patterns=[r"\b(project help|coding help|programming help)\b"],
        responses=[
            "I can help with various programming topics! What language or framework are you working with? 💻",
            "Sure! What kind of project are you working on? I'd be happy to provide guidance! 🚀",
            "Programming assistance? Great! Could you describe your project or the specific issue? 🛠️"
        ]
    ),
]

DEFAULT_RESPONSES = [
    "I'm not quite sure about that. Could you rephrase your question? 🤔",
    "I didn't quite catch that. Can you explain differently?",
    "Hmm, I'm not sure I understand. Could you provide more details?",
    "I'm still learning! Could you try asking in a different way? 🌱"
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
