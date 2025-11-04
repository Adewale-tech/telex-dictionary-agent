import requests
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DictionaryAgent:
    """
    Smart Dictionary Agent using Free Dictionary API
    """
    
    def __init__(self):
        self.api_base_url = "https://api.dictionaryapi.dev/api/v2/entries/en"
        self.name = "SmartDict Bot"
        self.help_message = """📖 **SmartDict Bot - How to Use**
        
I can help you look up word definitions! Here's how:

- `define [word]` - Get full definition
- `meaning [word]` - Get meaning
- `[word]` - Just type any word
- `help` - Show this message

Examples:
- define ephemeral
- meaning serendipity
- eloquent
"""
    
    def process_message(self, message: str) -> str:
        """Process incoming messages"""
        message = message.strip()
        message_lower = message.lower()
        
        # Check for help
        if message_lower in ['help', '/help', 'how to use']:
            return self.help_message
        
        # Check for greetings
        if message_lower in ['hello', 'hi', 'hey', 'greetings']:
            return f"👋 Hello! I'm {self.name}. Send me any word or type 'help' to learn how to use me!"
        
        # Extract word
        word = self._extract_word(message)
        
        if not word:
            return "❓ Please provide a word to look up. Type 'help' for usage instructions."
        
        return self.lookup_word(word)
    
    def _extract_word(self, message: str) -> Optional[str]:
        """Extract the word from message"""
        message_lower = message.lower().strip()
        
        prefixes = ['define ', 'meaning ', 'what is ', 'whats ', 
                   'definition of ', 'meaning of ', 'define: ', 'meaning: ']
        
        for prefix in prefixes:
            if message_lower.startswith(prefix):
                word = message[len(prefix):].strip()
                return word.split()[0] if word else None
        
        words = message.split()
        if words:
            return words[0]
        
        return None
    
    def lookup_word(self, word: str) -> str:
        """Look up word in dictionary API"""
        try:
            url = f"{self.api_base_url}/{word.lower()}"
            logger.info(f"Looking up: {word}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 404:
                return f"❌ Sorry, I couldn't find '{word}' in my dictionary. Please check the spelling."
            
            if response.status_code != 200:
                return f"⚠️ I had trouble looking up '{word}'. Please try again later."
            
            data = response.json()
            return self._format_definition(word, data)
        
        except requests.exceptions.Timeout:
            return f"⏱️ Request timed out while looking up '{word}'. Please try again."
        
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return f"❌ An unexpected error occurred. Please try again."
    
    def _format_definition(self, word: str, data: list) -> str:
        """Format API response"""
        try:
            if not data:
                return f"❌ No definition found for '{word}'."
            
            entry = data[0]
            phonetic = entry.get('phonetic', '')
            meanings = entry.get('meanings', [])
            
            if not meanings:
                return f"❌ No meanings found for '{word}'."
            
            response = f"📖 **{word.upper()}**"
            
            if phonetic:
                response += f" _{phonetic}_"
            
            response += "\n\n"
            
            count = 0
            for meaning in meanings[:3]:
                part_of_speech = meaning.get('partOfSpeech', 'unknown')
                definitions = meaning.get('definitions', [])
                
                if definitions:
                    definition = definitions[0]
                    def_text = definition.get('definition', '')
                    example = definition.get('example', '')
                    
                    count += 1
                    response += f"**{count}. ({part_of_speech})**\n"
                    response += f"   {def_text}\n"
                    
                    if example:
                        response += f"   💡 Example: _{example}_\n"
                    
                    response += "\n"
            
            if meanings and meanings[0].get('synonyms'):
                synonyms = meanings[0]['synonyms'][:5]
                if synonyms:
                    response += f"🔄 Similar words: {', '.join(synonyms)}\n"
            
            return response.strip()
        
        except Exception as e:
            logger.error(f"Formatting error: {str(e)}")
            return f"❌ Error formatting the definition for '{word}'."