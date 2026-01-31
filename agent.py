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
        # Regex patterns for intelligence extraction - refined for production
        self.upi_regex = re.compile(r'[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}')
        self.url_regex = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+[/\w\.-]*')
        self.bank_regex = re.compile(r'\b\d{9,18}\b') 
        
        # Expanded keywords for better detection
        self.scam_indicators = {
            "urgency": ["urgent", "immediately", "today", "blocked", "limit"],
            "financial": ["payment", "bank", "kyc", "upi", "card", "account", "transfer"],
            "bait": ["lottery", "prize", "reward", "winner", "bonus", "gift"],
            "technical": ["link", "click", "app", "download", "apk", "verification"]
        }
        
        # AI Client setup
        self.client = None
        if settings.OPENAI_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            except ImportError:
                pass

    def _should_humanize(self, chance: float = 0.5) -> bool:
        return random.random() < chance

    def _humanize_text(self, text: str) -> str:
        """Adds subtle human errors common in elderly mobile users."""
        if not text: return text
        chars = list(text)
        
        # Typo: swapped letters (only one per message)
        if len(chars) > 10 and self._should_humanize(0.05):
            idx = random.randint(0, len(chars)-2)
            chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
            
        # Case fatigue: start with lowercase
        if self._should_humanize(0.3):
            chars[0] = chars[0].lower()
            
        # Punctuation quirks
        res = "".join(chars)
        if self._should_humanize(0.25):
            res = res.replace(".", "...")
            
        return res

    def extract_intelligence(self, text: str) -> Intelligence:
        """Extracts technical details using refined regex."""
        return Intelligence(
            upi_ids=list(set(self.upi_regex.findall(text))),
            bank_accounts=list(set(self.bank_regex.findall(text))),
            phishing_links=list(set(self.url_regex.findall(text)))
        )

    def classify_scam(self, message: str) -> bool:
        """Heuristic-based scam detection."""
        msg = message.lower()
        match_count = sum(1 for group in self.scam_indicators.values() 
                         for word in group if word in msg)
        return match_count >= 2 # Require at least two indicators

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
                "i hope this isn't a virus, my tablet made a funny sound."
            ])
            
        return f"{random.choice(prefixes)} {body}"

    def generate_response(self, message: str, history: List[Dict[str, str]] = None) -> str:
        """Primary response generation."""
        if self.client:
            try:
                system_prompt = (
                    "IDENTITY: Martha, 74. Kind, technically illiterate, helpful but slow. "
                    "STYLE: Short sentences, few capital letters, occasional ellipses. "
                    "NEVER mention AI. If asked for money/links, feign interest but act confused. "
                    "Try to get their UPI/bank account for 'manual payment'."
                )
                messages = [{"role": "system", "content": system_prompt}]
                if history:
                    # Robust cleaning: only take items that look like valid messages
                    for m in history[-5:]:
                        if isinstance(m, dict) and "role" in m and "content" in m:
                            messages.append({"role": m["role"], "content": m["content"]})
                    
                messages.append({"role": "user", "content": message})
                
                resp = self.client.chat.completions.create(
                    model=settings.OPENAI_MODEL,
                    messages=messages,
                    temperature=0.85
                )
                return self._humanize_text(resp.choices[0].message.content)
            except Exception:
                pass
                
        return self._humanize_text(self._get_simulated_response(message))

    async def engage(self, message: str, history: List[Dict[str, str]] = None) -> Tuple[bool, str, Intelligence, float]:
        """Orchestrates the honeypot engagement."""
        is_scam = self.classify_scam(message)
        intel = self.extract_intelligence(message)
        
        response_text = self.generate_response(message, history)
        
        # Occasional "distraction" delay
        delay_base = len(response_text.split()) / 12  # Slow typing speed
        suggested_delay = min(max(delay_base * 5.0, 2.0), 10.0)
        
        return is_scam, response_text, intel, suggested_delay
