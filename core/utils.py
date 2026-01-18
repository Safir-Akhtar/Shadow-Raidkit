# core/utils.py - Shadow Tools ke chhote-mote beast helpers
# No imports needed here, sab simple functions hain

import random
import time
import asyncio

def human_jitter(base: float = 0.35) -> float:
    """
    Human-like random delay taaki Discord rate-limit ya detection se bach sake
    Example: await asyncio.sleep(human_jitter())
    """
    return base + random.uniform(0, 0.8)


def random_delay(min_sec: float = 0.3, max_sec: float = 1.2) -> float:
    """
    Random delay messages ke beech (spam/typing simulation ke liye)
    """
    return random.uniform(min_sec, max_sec)


def get_timestamp() -> str:
    """Current time string for logs"""
    return time.strftime("%Y-%m-%d %H:%M:%S")


def censor_text(text: str) -> str:
    """
    Optional profanity censor (better_profanity install karke use kar sakta hai)
    Agar better_profanity nahi install toh simple return
    """
    try:
        from better_profanity import profanity
        return profanity.censor(text).censored
    except ImportError:
        return text  # fallback


async def safe_sleep(seconds: float):
    """asyncio.sleep with jitter"""
    await asyncio.sleep(human_jitter(seconds))


def generate_fake_typing_delay(length: int = 10) -> float:
    """
    Typing simulation ke liye delay (message length ke hisaab se)
    Discord typing indicator 10 sec tak tikta hai max
    """
    return min(8.0, 0.1 * length + random.uniform(0.5, 2.0))


# Example usage (test ke liye console mein run kar sakta hai)
if __name__ == "__main__":
    print("Testing utils.py:")
    print(f"Jitter delay: {human_jitter()}")
    print(f"Random delay: {random_delay()}")
    print(f"Timestamp: {get_timestamp()}")
    print(f"Censored: {censor_text('fuck this shit')}")