from typing import Dict, List, Any, Tuple
import re
import random
from config import settings
from models import Intelligence

class HoneyPotAgent:
    """
    The Brain of the HoneyPot. 
    Simulates an elderly persona to bait scammers into revealing PII.
    """
    def __init__(self):
        # Regex patterns for intelligence extraction
        self.upi_regex = re.compile(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}')
        self.url_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*')
        self.bank_regex = re.compile(r'\b\d{9,18}\b') 
        self.phone_regex = re.compile(r'\+?\d[\d -]{8,12}\d') # Basic phone matcher

        # Expanded keywords for better detection
        self.scam_indicators = {
            "urgency": ["urgent", "immediately", "today", "blocked", "limit", "verify now"],
            "financial": ["payment", "bank", "kyc", "upi", "card", "account", "transfer"],
            "bait": ["lottery", "prize", "reward", "winner", "bonus", "gift"],
            "technical": ["link", "click", "app", "download", "apk", "verification"]
        }
        
        # Flatten indicators for keyword search
        self.all_keywords = [w for cat in self.scam_indicators.values() for w in cat]
        
        # AI Client setup
        self.client = None
        if settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                pass

    def _should_humanize(self, chance: float = 0.5) -> bool:
        return random.random() < chance

    def _humanize_text(self, text: str) -> str:
        """Adds subtle human errors common in elderly mobile users."""
        if not text: return text
        chars = list(text)
        
        if len(chars) > 10 and self._should_humanize(0.05):
            idx = random.randint(0, len(chars)-2)
            chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
            
        if self._should_humanize(0.3):
            chars[0] = chars[0].lower()
            
        res = "".join(chars)
        if self._should_humanize(0.25):
            res = res.replace(".", "...")
            
        return res

    def extract_intelligence(self, text: str) -> Intelligence:
        """Extracts technical details using refined regex."""
        # Find suspicious keywords present in text
        found_keywords = [k for k in self.all_keywords if k in text.lower()]
        
        # Filter out likely timestamps (13 digits starting with 17 or 18) from bank accounts
        raw_accounts = self.bank_regex.findall(text)
        valid_accounts = []
        for acc in raw_accounts:
            # 13 digits starting with 17 or 18 is likely a ms timestamp for ~2023-2029
            if len(acc) == 13 and acc.startswith(("17", "18")):
                continue
            valid_accounts.append(acc)

        return Intelligence(
            upi_ids=list(set(self.upi_regex.findall(text))),
            bank_accounts=list(set(valid_accounts)),
            phishing_links=list(set(self.url_regex.findall(text))),
            phone_numbers=list(set(self.phone_regex.findall(text))),
            suspicious_keywords=list(set(found_keywords))
        )

    def classify_scam(self, message: str) -> bool:
        """Heuristic-based scam detection."""
        msg = message.lower()
        match_count = sum(1 for group in self.scam_indicators.values() 
                         for word in group if word in msg)
        # Low threshold for hackathon purposes - default to true if anything suspicious
        return match_count >= 1

    def _get_simulated_response(self, message: str) -> str:
        """Fallback logic when AI is unavailable - feels like an old person."""
        m = message.lower()
        prefixes = ["oh dear...", "hello dear,", "bless you,", "sorry i am late replying,"]
        
        if any(x in m for x in ["pay", "upi", "money"]):
            body = "i want to pay you but i can't find where to type. can you give me that upi name or account? my grandson is not home to help."
        elif any(x in m for x in ["link", "click", "open"]):
            body = "the screen just went black when i clicked. do i need to send you my bank details instead so you can fix it?"
        else:
            body = random.choice([
                "who is this? is this the electricity man again?",
                "i'm trying to find my glasses... what did you say?",
                "i hope this isn't a virus, my mobile made a funny sound."
            ])
            
        return f"{random.choice(prefixes)} {body}"

    async def generate_response(self, message: str, history: List[Any] = None) -> str:
        """Primary response generation."""
        if self.client:
            try:
                system_prompt = (
                    "IDENTITY: Martha, 74. Kind, technically illiterate, helpful but slow. "
                    "STYLE: Short sentences, few capital letters, occasional ellipses. "
                    "GOAL: Waste the scammer's time. Feign interest but act confused. "
                    "NEVER mention AI. "
                    "Try to get their UPI/bank account for 'manual payment'."
                )
                messages = [{"role": "system", "content": system_prompt}]
                
                if history:
                    # Map history format to OpenAI format
                    # History item: {'sender': 'scammer'|'user', 'text': '...', ...}
                    for m in history:
                        # Safely extract sender and text
                        sender = None
                        text = None
                        
                        if isinstance(m, dict):
                            sender = m.get('sender')
                            text = m.get('text')
                        elif isinstance(m, str):
                            # Handle plain string messages (assume User/Scammer)
                            sender = "user"
                            text = m
                        else:
                            # Try object attributes
                            sender = getattr(m, 'sender', None)
                            text = getattr(m, 'text', None)
                        
                        if sender and text:
                            role = "user" if sender == "scammer" else "assistant"
                            messages.append({"role": role, "content": text})
                
                messages.append({"role": "user", "content": message})
                
                resp = await self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=0.85
                )
                return self._humanize_text(resp.choices[0].message.content)
            except Exception as e:
                print(f"OpenAI Error: {e}")
                pass
                
        return self._humanize_text(self._get_simulated_response(message))

    async def engage(self, message: str, history: List[Any] = None) -> Tuple[bool, str, Intelligence, float]:
        """Orchestrates the honeypot engagement."""
        is_scam = self.classify_scam(message)
        intel = self.extract_intelligence(message)
        
        # Only engage if it's a scam or we just want to reply
        # For this challenge, we always reply to keep it going if requested
        response_text = await self.generate_response(message, history)
        
        # Occasional "distraction" delay
        delay_base = len(response_text.split()) / 12  # Slow typing speed
        suggested_delay = min(max(delay_base * 5.0, 2.0), 10.0)
        
        return is_scam, response_text, intel, suggested_delay
