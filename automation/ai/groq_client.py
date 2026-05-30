from groq import Groq
from automation.config import config
from automation.utils.logger import get_logger

logger = get_logger(__name__)

_client: Groq = None


def get_groq_client() -> Groq:
    """Return a singleton Groq client."""
    global _client
    if _client is None:
        if not config.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not set in your .env file.\n"
                "Get a free key at https://console.groq.com"
            )
        _client = Groq(api_key=config.GROQ_API_KEY)
        logger.info("Groq client initialized")
    return _client


def call_groq(prompt: str, system: str = '', max_tokens: int = 400) -> str:
    """
    Make a chat completion call to Groq's llama3-70b model.

    Args:
        prompt: The user message
        system: Optional system prompt
        max_tokens: Max response length

    Returns:
        Response text, or empty string on failure
    """
    client = get_groq_client()

    messages = []
    if system:
        messages.append({'role': 'system', 'content': system})
    messages.append({'role': 'user', 'content': prompt})

    try:
        resp = client.chat.completions.create(
            model='llama3-70b-8192',
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return ''