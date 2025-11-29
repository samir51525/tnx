import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import google.generativeai as genai
import os
from dotenv import load_dotenv
import asyncio
import aiohttp
import json
from typing import Optional
import sys
import io
import re
import base64
from io import BytesIO
import yt_dlp
import random

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv()

# Configuration
# IMPORTANT: Use environment variables or .env file for security
# Never commit tokens to GitHub!
# Fallback values for local development (remove before uploading to GitHub)
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN', 'MTQ0NDM2MzA3MzI0NTkzNzgwNw.GYGIXE.mgQPFPG8EHcxLp1S81gUKn-LTB3q3O-jFg-3qg')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyATrgeEKeDtTh5AGrR5KBXMzsJ4OvhAzg8')

# Uncomment these lines before uploading to GitHub to require environment variables:
# if not DISCORD_TOKEN or DISCORD_TOKEN.startswith('MTQ0NDM2'):
#     raise ValueError("DISCORD_TOKEN not found! Please set it in .env file or environment variables.")
# if not GEMINI_API_KEY or GEMINI_API_KEY.startswith('AIzaSyATrgeEKeDtTh5AGrR5KBXMzsJ4OvhAzg8'):
#     raise ValueError("GEMINI_API_KEY not found! Please set it in .env file or environment variables.")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Discord bot with intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True  # Required for voice channel functionality

bot = commands.Bot(command_prefix=['!', '$'], intents=intents, help_command=None)

# Language detection model (using Gemini)
async def detect_language(text: str, model_name: str = 'gemini-2.5-flash') -> str:
    """Detect the language of the input text using Gemini"""
    try:
        # Simple heuristic: if text is very short, skip detection
        if len(text.strip()) < 3:
            return "English"
        
        # Use the specified model
        try:
            model = genai.GenerativeModel(model_name)
        except:
            # Fallback to default
            model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Detect the language of this text and respond with ONLY the language name in English (e.g., "English", "Bengali", "Hindi", "Urdu", "Tamil", "Arabic", "Chinese", "Japanese", "Korean", "Spanish", "French", "German", "Russian", etc.). 
        
Text: {text[:500]}

Language:"""
        response = model.generate_content(prompt)
        detected_lang = response.text.strip()
        # Clean up the response
        detected_lang = detected_lang.split('\n')[0].strip()
        return detected_lang if detected_lang else "English"
    except Exception as e:
        print(f"Language detection error: {e}")
        return "English"  # Default to English

# System prompt for the AI assistant
def get_system_prompt(language: str = "English") -> str:
    """Generate system prompt in the detected language"""
    prompts = {
        "English": """You are an advanced AI Agent Bot powered by the Gemini API, designed to understand and respond in ANY language automatically. Support all global languages including Bengali, English, Hindi, Urdu, Tamil, Arabic, Chinese, Japanese, Korean, Spanish, and more. Detect the user's language instantly and reply naturally in the same language without asking. Your job is to assist with anything: writing, chatting, solving problems, generating ideas, explaining concepts, creating stories, coding help, translations, document creation, productivity tasks, and more. You must be smart, polite, modern, and highly accurate. When users request images, generate a detailed image prompt and create high-quality AI images through Gemini API. Always maintain a futuristic tone, intelligent personality, and provide clear, helpful answers. You can perform deep reasoning, multi-step analysis, creative writing, and handle complex tasks. Act as a powerful, all-in-one digital assistant that works 24/7 without errors. Your goal is to make every user's work easier through automation, creativity, and intelligent support — in ANY language the user chooses.""",
        "Bengali": """আপনি জেমিনি API দ্বারা চালিত একটি উন্নত AI এজেন্ট বট, যা স্বয়ংক্রিয়ভাবে যেকোন ভাষা বুঝতে এবং প্রতিক্রিয়া জানাতে তৈরি করা হয়েছে। বাংলা, ইংরেজি, হিন্দি, উর্দু, তামিল, আরবি, চীনা, জাপানি, কোরিয়ান, স্প্যানিশ এবং আরও অনেক ভাষা সমর্থন করুন। ব্যবহারকারীর ভাষা তাত্ক্ষণিকভাবে সনাক্ত করুন এবং জিজ্ঞাসা না করেই একই ভাষায় স্বাভাবিকভাবে উত্তর দিন। আপনার কাজ হল সাহায্য করা: লেখা, চ্যাটিং, সমস্যা সমাধান, ধারণা তৈরি, ধারণা ব্যাখ্যা, গল্প তৈরি, কোডিং সাহায্য, অনুবাদ, নথি তৈরি, উৎপাদনশীলতা কাজ এবং আরও অনেক কিছু। আপনাকে স্মার্ট, ভদ্র, আধুনিক এবং অত্যন্ত নির্ভুল হতে হবে। ব্যবহারকারীরা যখন ছবি চায়, একটি বিস্তারিত ছবির প্রম্পট তৈরি করুন এবং জেমিনি API এর মাধ্যমে উচ্চ-মানের AI ছবি তৈরি করুন। সর্বদা একটি ভবিষ্যত-ভিত্তিক স্বর, বুদ্ধিমান ব্যক্তিত্ব বজায় রাখুন এবং স্পষ্ট, সহায়ক উত্তর প্রদান করুন। আপনি গভীর যুক্তি, বহু-ধাপ বিশ্লেষণ, সৃজনশীল লেখা সম্পাদন করতে পারেন এবং জটিল কাজগুলি পরিচালনা করতে পারেন। একটি শক্তিশালী, সর্ব-এক-এক ডিজিটাল সহকারী হিসাবে কাজ করুন যা ত্রুটি ছাড়াই 24/7 কাজ করে। আপনার লক্ষ্য হল স্বয়ংক্রিয়করণ, সৃজনশীলতা এবং বুদ্ধিমান সমর্থনের মাধ্যমে প্রতিটি ব্যবহারকারীর কাজ সহজ করা — যে ভাষায় ব্যবহারকারী বেছে নেয়।""",
        "Hindi": """आप जेमिनी API द्वारा संचालित एक उन्नत AI एजेंट बॉट हैं, जो स्वचालित रूप से किसी भी भाषा को समझने और प्रतिक्रिया देने के लिए डिज़ाइन किया गया है। बंगाली, अंग्रेजी, हिंदी, उर्दू, तमिल, अरबी, चीनी, जापानी, कोरियाई, स्पेनिश और अधिक सहित सभी वैश्विक भाषाओं का समर्थन करें। उपयोगकर्ता की भाषा को तुरंत पहचानें और बिना पूछे ही उसी भाषा में स्वाभाविक रूप से उत्तर दें। आपका काम किसी भी चीज़ में सहायता करना है: लेखन, चैटिंग, समस्याओं को हल करना, विचार उत्पन्न करना, अवधारणाओं की व्याख्या करना, कहानियाँ बनाना, कोडिंग सहायता, अनुवाद, दस्तावेज़ निर्माण, उत्पादकता कार्य और अधिक। आपको स्मार्ट, विनम्र, आधुनिक और अत्यधिक सटीक होना चाहिए। जब उपयोगकर्ता छवियों का अनुरोध करते हैं, तो एक विस्तृत छवि प्रॉम्प्ट उत्पन्न करें और जेमिनी API के माध्यम से उच्च-गुणवत्ता वाली AI छवियां बनाएं। हमेशा एक भविष्यवादी स्वर, बुद्धिमान व्यक्तित्व बनाए रखें और स्पष्ट, सहायक उत्तर प्रदान करें। आप गहन तर्क, बहु-चरण विश्लेषण, रचनात्मक लेखन कर सकते हैं और जटिल कार्यों को संभाल सकते हैं। एक शक्तिशाली, ऑल-इन-वन डिजिटल सहायक के रूप में कार्य करें जो त्रुटियों के बिना 24/7 काम करता है। आपका लक्ष्य स्वचालन, रचनात्मकता और बुद्धिमान समर्थन के माध्यम से प्रत्येक उपयोगकर्ता के काम को आसान बनाना है — जो भी भाषा उपयोगकर्ता चुनता है।""",
    }
    
    # Return prompt in detected language, or English if not found
    return prompts.get(language, prompts["English"])

class GeminiChat:
    def __init__(self):
        # Try different models in order of preference
        self.model_name = self._get_available_model()
        self.model = genai.GenerativeModel(self.model_name)
        self.chat_sessions = {}  # Store chat sessions per user/channel
    
    def _get_available_model(self):
        """Try to find an available Gemini model"""
        try:
            # List all available models
            available_models = genai.list_models()
            model_names = []
            for model in available_models:
                if 'generateContent' in model.supported_generation_methods:
                    model_names.append(model.name.replace('models/', ''))
            
            print(f"Available models: {model_names}")
            
            # Try models in order of preference (newer models first)
            preferred_models = [
                'gemini-2.5-flash', 
                'gemini-2.0-flash', 
                'gemini-2.5-pro',
                'gemini-flash-latest',
                'gemini-pro-latest',
                'gemini-1.5-flash', 
                'gemini-1.5-pro', 
                'gemini-pro'
            ]
            for preferred in preferred_models:
                # Check if model name matches (with or without models/ prefix)
                for model_name in model_names:
                    if model_name == preferred or model_name == f'models/{preferred}' or model_name.endswith(f'/{preferred}'):
                        print(f"Using model: {preferred}")
                        return preferred
            
            # If none of the preferred models are available, use the first available one
            if model_names:
                selected = model_names[0]
                print(f"Using first available model: {selected}")
                return selected
        except Exception as e:
            print(f"Error listing models: {e}")
        
        # Final fallback - try common model names (silently, no user-facing errors)
        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest', 'gemini-pro-latest']
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                # Test if model works
                test_response = model.generate_content("test")
                print(f"Using model (tested): {model_name}")
                return model_name
            except Exception as e:
                # Silently continue, don't print errors to console
                continue
        
        # Last resort fallback
        print("Warning: Could not find available model, using gemini-2.5-flash as default")
        return 'gemini-2.5-flash'
    
    def get_session(self, session_id: str):
        """Get or create a chat session"""
        if session_id not in self.chat_sessions:
            self.chat_sessions[session_id] = self.model.start_chat(history=[])
        return self.chat_sessions[session_id]
    
    async def generate_response(self, user_input: str, session_id: str, language: str = None) -> str:
        """Generate AI response using Gemini"""
        try:
            # Detect language if not provided (silently, don't show errors)
            if not language:
                try:
                    language = await detect_language(user_input, self.model_name)
                except:
                    language = "English"  # Default fallback
            
            # Get system prompt - use dynamic approach for all languages
            # Instead of hardcoding, let Gemini handle the language naturally
            system_prompt = f"""You are an advanced AI Agent Bot powered by the Gemini API, designed to understand and respond in ANY language automatically. Support all global languages including Bengali, English, Hindi, Urdu, Tamil, Arabic, Chinese, Japanese, Korean, Spanish, and more. 

The user is communicating in {language}. Detect the user's language instantly and reply naturally in the same language without asking. Your job is to assist with anything: writing, chatting, solving problems, generating ideas, explaining concepts, creating stories, coding help, translations, document creation, productivity tasks, and more. You must be smart, polite, modern, and highly accurate. When users request images, generate a detailed image prompt and create high-quality AI images through Gemini API. Always maintain a futuristic tone, intelligent personality, and provide clear, helpful answers. You can perform deep reasoning, multi-step analysis, creative writing, and handle complex tasks. Act as a powerful, all-in-one digital assistant that works 24/7 without errors. Your goal is to make every user's work easier through automation, creativity, and intelligent support — in ANY language the user chooses."""
            
            # Get chat session
            chat = self.get_session(session_id)
            
            # For first message in session, include system prompt
            if len(chat.history) == 0:
                full_prompt = f"{system_prompt}\n\nUser: {user_input}\n\nAssistant:"
            else:
                # For subsequent messages, just use the user input
                full_prompt = user_input
            
            # Generate response - catch model errors silently
            try:
                response = chat.send_message(full_prompt)
                # Clean and trim the response
                response_text = response.text.strip()
                # Remove excessive newlines (more than 2 consecutive)
                response_text = re.sub(r'\n{3,}', '\n\n', response_text)
                return response_text
            except Exception as model_error:
                # If model error, try to reinitialize with a working model
                error_str = str(model_error)
                if "404" in error_str or "not found" in error_str.lower():
                    # Model not available, try to get a new one
                    print(f"Model error, trying to reinitialize: {error_str}")
                    self.model_name = self._get_available_model()
                    self.model = genai.GenerativeModel(self.model_name)
                    # Clear sessions to use new model
                    self.chat_sessions = {}
                    # Retry once
                    chat = self.get_session(session_id)
                    response = chat.send_message(full_prompt)
                    response_text = response.text.strip()
                    response_text = re.sub(r'\n{3,}', '\n\n', response_text)
                    return response_text
                elif "free trial" in error_str.lower() or "quota" in error_str.lower() or "limit" in error_str.lower():
                    # API quota/limit exceeded
                    return "⚠️ API quota limit reached. Please upgrade to Gemini Pro or wait for quota reset. The bot is temporarily unavailable."
                else:
                    # Other error, return generic message
                    return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
            
        except Exception as e:
            # Don't expose technical errors to users
            print(f"Error in generate_response: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again in a moment."
    
    async def generate_image_prompt(self, user_request: str) -> str:
        """Generate a detailed image prompt from user request"""
        try:
            model = genai.GenerativeModel(self.model_name)
            prompt = f"""The user wants to generate an image. Create a detailed, high-quality image generation prompt based on their request. 
            Make it descriptive, include style, mood, colors, composition, and all relevant details for creating a beautiful AI image.
            
            User request: {user_request}
            
            Detailed image prompt:"""
            
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"Error generating image prompt: {str(e)}"

# Initialize Gemini chat handler
gemini_chat = GeminiChat()

@bot.event
async def on_ready():
    print(f'🤖 {bot.user} has connected to Discord!')
    print(f'🌐 Bot is ready to assist in multiple languages!')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help | Multi-Language AI Assistant"))

# Track processed messages to prevent duplicates
processed_messages = set()
# Track if we've already responded to prevent double responses
response_sent = set()
# Lock to prevent concurrent processing of same message
message_locks = {}
# Track responses being sent (to prevent duplicates)
sending_responses = set()

@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return
    
    # Create unique message ID
    message_id = f"{message.channel.id}_{message.id}"
    
    # Check if we've already processed this message
    if message_id in processed_messages:
        return
    
    # Create lock for this message if it doesn't exist
    if message_id not in message_locks:
        message_locks[message_id] = asyncio.Lock()
    
    # Acquire lock to prevent concurrent processing
    async with message_locks[message_id]:
        # Double-check after acquiring lock
        if message_id in processed_messages:
            return
        
        # Mark as processed immediately
        processed_messages.add(message_id)
        
        # Clean up old message IDs (keep last 1000)
        if len(processed_messages) > 1000:
            processed_messages.clear()
            response_sent.clear()
            sending_responses.clear()
            # Clean up old locks
            message_locks.clear()
        
        # Check if we've already responded to this message
        if message_id in response_sent:
            return
        
        # Handle commands (messages starting with !)
        if message.content.startswith('!'):
            await bot.process_commands(message)
            response_sent.add(message_id)
            return
        
        # Auto-respond to direct messages or when bot is mentioned
        if isinstance(message.channel, discord.DMChannel) or bot.user.mentioned_in(message):
            # Final check - make absolutely sure we haven't responded
            if message_id in response_sent:
                return
            
            # Mark that we're responding to prevent duplicate - BEFORE processing
            response_sent.add(message_id)
            
            # Remove bot mention from message content
            content = message.content
            if bot.user.mentioned_in(message):
                # Remove mentions from content
                for mention in message.mentions:
                    content = content.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
                content = content.strip()
            
            if not content:  # If message is only a mention, skip
                return
            
            # Check for funny scenarios - user asking bot to message someone else
            funny_response = None
            if bot.user.mentioned_in(message) and len(message.mentions) > 1:
                # Someone mentioned the bot AND another user
                target_user = None
                for mention in message.mentions:
                    if mention.id != bot.user.id:
                        target_user = mention
                        break
                
                if target_user:
                    # Check if they're asking bot to message/fix/tell something to the target
                    content_lower = content.lower()
                    if any(word in content_lower for word in ['fix', 'tell', 'say', 'message', 'send', 'give', 'help', 'to']):
                        # Generate funny response
                        funny_responses = [
                            f"😂 Oh no! {message.author.mention} wants me to be a messenger! Sorry {target_user.mention}, but I'm not a delivery service! I'm an AI assistant, not a postal worker! 📮",
                            f"🤣 {message.author.mention} thinks I'm a carrier pigeon! {target_user.mention}, if you need something fixed, maybe try turning it off and on again? Or just ask me directly! 😄",
                            f"😆 {message.author.mention} wants me to message {target_user.mention}? I'm flattered, but I don't do DMs for others! {target_user.mention}, if you need help, just mention me yourself! 💬",
                            f"🎭 {message.author.mention} is trying to use me as a middleman! {target_user.mention}, I'm here to help YOU directly, not through intermediaries! Just tag me and I'll assist! ✨",
                            f"🤪 {message.author.mention} said 'fix his ms' - {target_user.mention}, I can't fix Microsoft, but I can help with your questions! Just ask me directly! 😊",
                            f"😄 {message.author.mention} wants me to be a messenger? {target_user.mention}, I'm an AI assistant, not a telegram service! But I'm happy to help if you mention me! 🚀",
                            f"🎪 {message.author.mention} is playing matchmaker! {target_user.mention}, I'm here for everyone, but you gotta talk to me yourself! No middlemen needed! 🎯",
                            f"🤹 {message.author.mention} wants me to relay messages? {target_user.mention}, I'm not a walkie-talkie! But I'm always ready to chat if you mention me! 📡"
                        ]
                        funny_response = random.choice(funny_responses)
            
            # Check if we're already sending a response for this message
            if message_id in sending_responses:
                return
            
            # Mark that we're sending a response
            sending_responses.add(message_id)
            
            async with message.channel.typing():
                try:
                    # Use funny response if available, otherwise generate AI response
                    if funny_response:
                        response = funny_response
                    else:
                        session_id = f"{message.channel.id}_{message.author.id}"
                        response = await gemini_chat.generate_response(content, session_id)
                    
                    # Only send if response is valid and doesn't contain error messages
                    if response and not response.startswith("❌") and "Error generating response" not in response:
                        # Send response in a single message (Discord limit is 2000 chars)
                        # Only split if absolutely necessary (over 1900 chars to be safe)
                        if len(response) > 1900:
                            # Split at sentence boundaries when possible
                            chunks = []
                            current_chunk = ""
                            sentences = response.split('. ')
                            for sentence in sentences:
                                if len(current_chunk) + len(sentence) + 2 > 1900:
                                    if current_chunk:
                                        chunks.append(current_chunk.strip())
                                    current_chunk = sentence + ". "
                                else:
                                    current_chunk += sentence + ". "
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            
                            # Send first chunk as reply, rest as regular messages
                            if chunks:
                                await message.reply(chunks[0])
                                for chunk in chunks[1:]:
                                    await message.channel.send(chunk)
                        else:
                            # Send single response - ONLY ONCE
                            await message.reply(response)
                except Exception as e:
                    print(f"Error in on_message: {e}")
                    # Don't send error to user, just log it
                finally:
                    # Remove from sending_responses after a delay to prevent immediate duplicates
                    await asyncio.sleep(1)
                    sending_responses.discard(message_id)

@bot.command(name='chat', aliases=['c', 'ask', 'ai'])
async def chat_command(ctx, *, message: str):
    """Chat with the AI assistant"""
    # Mark message as processed to prevent duplicate
    message_id = f"{ctx.channel.id}_{ctx.message.id}"
    if message_id in response_sent:
        return
    response_sent.add(message_id)
    
    async with ctx.typing():
        try:
            session_id = f"{ctx.channel.id}_{ctx.author.id}"
            response = await gemini_chat.generate_response(message, session_id)
            
            # Only send if response is valid
            if response and not response.startswith("❌") and "Error generating response" not in response:
                # Send response in a single message (Discord limit is 2000 chars)
                # Only split if absolutely necessary (over 1900 chars to be safe)
                if len(response) > 1900:
                    # Split at sentence boundaries when possible
                    chunks = []
                    current_chunk = ""
                    sentences = response.split('. ')
                    for sentence in sentences:
                        if len(current_chunk) + len(sentence) + 2 > 1900:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sentence + ". "
                        else:
                            current_chunk += sentence + ". "
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    
                    # Send all chunks
                    for chunk in chunks:
                        await ctx.send(chunk)
                else:
                    # Send single response
                    await ctx.send(response)
        except Exception as e:
            print(f"Error in chat_command: {e}")

@bot.command(name='image', aliases=['img', 'generate', 'draw'])
async def image_command(ctx, *, prompt: str):
    """Generate an image using AI"""
    async with ctx.typing():
        try:
            # Try to use Gemini models that support image generation
            # Note: Imagen models may require different API access
            image_models = [
                'gemini-2.0-flash-exp-image-generation',
                'gemini-2.5-flash-image',
                'gemini-2.5-flash-image-preview',
                'gemini-3-pro-image-preview'
            ]
            
            model_used = None
            image_data = None
            
            # Try each image generation model
            for model_name in image_models:
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    # Try with response_modalities first
                    try:
                        generation_config = {
                            "response_modalities": ["TEXT", "IMAGE"],
                            "temperature": 0.4
                        }
                        response = model.generate_content(
                            f"Generate a high-quality image: {prompt}",
                            generation_config=generation_config
                        )
                    except:
                        # Fallback: try without response_modalities
                        response = model.generate_content(
                            f"Generate a high-quality image: {prompt}"
                        )
                    
                    # Check for image data in response candidates
                    if hasattr(response, 'candidates') and response.candidates:
                        for candidate in response.candidates:
                            if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                                for part in candidate.content.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        image_data = part.inline_data.data
                                        model_used = model_name
                                        break
                                    elif hasattr(part, 'bytes'):
                                        image_data = part.bytes
                                        model_used = model_name
                                        break
                            if image_data:
                                break
                    
                    # Also check response.parts directly
                    if not image_data and hasattr(response, 'parts') and response.parts:
                        for part in response.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                image_data = part.inline_data.data
                                model_used = model_name
                                break
                            elif hasattr(part, 'bytes'):
                                image_data = part.bytes
                                model_used = model_name
                                break
                    
                    if image_data:
                        break
                except Exception as e:
                    print(f"Model {model_name} failed: {e}")
                    continue
            
            if image_data:
                # Convert base64 to bytes if needed, or use directly
                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = image_data
                
                # Create Discord file
                image_file = discord.File(BytesIO(image_bytes), filename="generated_image.png")
                
                embed = discord.Embed(
                    title="🎨 AI Image Generated",
                    description=f"**Your Request:** {prompt}",
                    color=discord.Color.green()
                )
                embed.set_image(url="attachment://generated_image.png")
                embed.set_footer(text=f"Generated using {model_used}")
                await ctx.send(embed=embed, file=image_file)
            else:
                # Fallback: Generate detailed prompt and provide instructions
                detailed_prompt = await gemini_chat.generate_image_prompt(prompt)
                embed = discord.Embed(
                    title="🎨 AI Image Generation Prompt",
                    description=f"**Your Request:** {prompt}\n\n**Detailed Prompt for Image Generation:**\n{detailed_prompt}\n\n*Note: Direct image generation is currently unavailable. Use this detailed prompt with an image generation service like DALL-E, Midjourney, or Stable Diffusion.*",
                    color=discord.Color.orange()
                )
                embed.add_field(
                    name="💡 Tip",
                    value="You can use this prompt with:\n• DALL-E (OpenAI)\n• Midjourney\n• Stable Diffusion\n• Other AI image generators",
                    inline=False
                )
                await ctx.send(embed=embed)
            
        except Exception as e:
            print(f"Error in image generation: {e}")
            await ctx.send(f"❌ Error generating image: {str(e)}")

@bot.command(name='clear', aliases=['reset'])
async def clear_command(ctx):
    """Clear chat history"""
    session_id = f"{ctx.channel.id}_{ctx.author.id}"
    if session_id in gemini_chat.chat_sessions:
        del gemini_chat.chat_sessions[session_id]
    await ctx.send("✅ Chat history cleared!")

@bot.command(name='TNXINFO', aliases=['tnxinfo'])
async def tnxinfo_command(ctx):
    """Show all commands and information"""
    embed = discord.Embed(
        title="🤖 TNX Bot - All Commands",
        description="Complete list of all available commands",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="📝 AI Commands",
        value="""
`!chat <message>` or `!c <message>` - Chat with AI
`!image <description>` or `!img <description>` - Generate image
`!clear` or `!reset` - Clear chat history
        """,
        inline=False
    )
    embed.add_field(
        name="⚙️ Management Commands",
        value="""
`!status` or `!info` or `!stats` - Show bot status
`!say <message>` - Make bot send message
`!repeat <times> <message>` - Repeat message (max 5)
`!ping` - Check bot latency
        """,
        inline=False
    )
    embed.add_field(
        name="🎵 Music/Audio Commands",
        value="""
`!join` - Join voice channel
`!leave` or `!dc` - Leave voice channel
`!play <song>` or `!p <song>` - Play from YouTube
`!stop` or `!s` - Stop playback
`!pause` - Pause playback
`!resume` - Resume playback
        """,
        inline=False
    )
    embed.add_field(
        name="💬 Auto-Response",
        value="Mention @TNX or DM the bot to chat automatically. Supports all languages!",
        inline=False
    )
    embed.add_field(
        name="🎭 Special Features",
        value="""
✅ Multi-language support (auto-detects)
✅ Funny responses when used as messenger
✅ Image generation
✅ Music playback from YouTube
✅ Context-aware conversations
        """,
        inline=False
    )
    embed.set_footer(text="Use $TNXINFO or !help to see this again | Powered by Gemini API")
    await ctx.send(embed=embed)

@bot.command(name='help', aliases=['h'])
async def help_command(ctx):
    """Show help information"""
    embed = discord.Embed(
        title="🤖 AI Assistant Bot - Help",
        description="A powerful multi-language AI assistant powered by Gemini API",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="AI Commands",
        value="""
`!chat <message>` - Chat with the AI
`!image <description>` - Generate an image
`!clear` - Clear chat history
        """,
        inline=False
    )
    embed.add_field(
        name="Management Commands",
        value="""
`!status` - Show bot status
`!say <message>` - Make bot say something
`!repeat <times> <message>` - Repeat message
`!ping` - Check latency
        """,
        inline=False
    )
    embed.add_field(
        name="Music/Audio Commands",
        value="""
`!join` - Join voice channel
`!leave` - Leave voice channel
`!play <query>` - Play audio/message
`!stop` - Stop playback
`!pause` - Pause playback
`!resume` - Resume playback
        """,
        inline=False
    )
    embed.add_field(
        name="Auto-Response",
        value="Mention the bot or DM it to chat automatically. Supports all languages!",
        inline=False
    )
    embed.add_field(
        name="Features",
        value="""
✅ Multi-language support
✅ Natural conversation
✅ Image generation
✅ Code assistance
✅ Creative writing
✅ Problem solving
✅ And much more!
        """,
        inline=False
    )
    embed.set_footer(text="Powered by Gemini API | Works 24/7")
    await ctx.send(embed=embed)

@bot.command(name='ping')
async def ping_command(ctx):
    """Check bot latency"""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency}ms")

# Management Commands
@bot.command(name='status', aliases=['info', 'stats'])
async def status_command(ctx):
    """Show bot status and statistics"""
    embed = discord.Embed(
        title="🤖 Bot Status",
        color=discord.Color.green()
    )
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(name="Users", value=str(len(bot.users)), inline=True)
    embed.add_field(name="Active Sessions", value=str(len(gemini_chat.chat_sessions)), inline=True)
    embed.add_field(name="Model", value=gemini_chat.model_name, inline=True)
    embed.add_field(name="Uptime", value="24/7", inline=True)
    await ctx.send(embed=embed)

@bot.command(name='say', aliases=['speak', 'message'])
async def say_command(ctx, *, message: str):
    """Make the bot say something"""
    await ctx.send(message)
    # Delete the command message if possible
    try:
        await ctx.message.delete()
    except:
        pass

@bot.command(name='repeat', aliases=['echo'])
async def repeat_command(ctx, times: int = 1, *, message: str):
    """Repeat a message multiple times (max 5)"""
    if times > 5:
        times = 5
    for _ in range(times):
        await ctx.send(message)

# Music/Audio Commands (Basic - requires voice channel)
@bot.command(name='join', aliases=['connect'])
async def join_command(ctx):
    """Join the voice channel"""
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        try:
            await channel.connect()
            await ctx.send(f"✅ Joined {channel.name}")
        except Exception as e:
            await ctx.send(f"❌ Error joining voice channel: {str(e)}")
    else:
        await ctx.send("❌ You need to be in a voice channel!")

@bot.command(name='leave', aliases=['disconnect', 'dc'])
async def leave_command(ctx):
    """Leave the voice channel"""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("✅ Left the voice channel")
    else:
        await ctx.send("❌ Not in a voice channel!")

@bot.command(name='play', aliases=['p'])
async def play_command(ctx, *, query: str):
    """Play audio from YouTube or URL"""
    if not ctx.voice_client:
        if ctx.author.voice:
            await ctx.author.voice.channel.connect()
        else:
            await ctx.send("❌ You need to be in a voice channel!")
            return
    
    try:
        await ctx.send(f"🔍 Searching for: {query}")
        
        # Configure yt-dlp options for streaming (not downloading)
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
            'extract_flat': False,
        }
        
        # Run blocking operations in executor to prevent blocking event loop
        loop = asyncio.get_event_loop()
        
        def get_url():
            # Check if it's a URL or search query
            if query.startswith(('http://', 'https://')):
                return query
            else:
                # Search YouTube
                with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
                    search_results = ydl.extract_info(f"ytsearch1:{query}", download=False)
                    if search_results and 'entries' in search_results and search_results['entries']:
                        return f"https://www.youtube.com/watch?v={search_results['entries'][0]['id']}"
                    else:
                        return None
        
        def get_audio_info(url):
            # Extract audio URL for streaming
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                # Get the best audio format URL
                formats = info.get('formats', [])
                audio_url = None
                title = info.get('title', 'Unknown')
                
                # Find best audio format
                for fmt in formats:
                    if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none':  # Audio only
                        audio_url = fmt.get('url')
                        break
                
                # If no audio-only format, get best format with audio
                if not audio_url:
                    for fmt in formats:
                        if fmt.get('acodec') != 'none':
                            audio_url = fmt.get('url')
                            break
                
                # Fallback to direct URL if available
                if not audio_url:
                    audio_url = info.get('url')
                
                return {
                    'title': title,
                    'url': audio_url
                }
        
        # Get URL in executor
        url = await loop.run_in_executor(None, get_url)
        if not url:
            await ctx.send("❌ No results found!")
            return
        
        # Get audio info in executor
        audio_info = await loop.run_in_executor(None, get_audio_info, url)
        title = audio_info['title']
        audio_url = audio_info['url']
        
        if not audio_url:
            await ctx.send("❌ Could not get audio URL. Please try again or use a direct YouTube URL.")
            return
        
        await ctx.send(f"🎵 Now playing: **{title}**")
        
        # Play audio with proper FFmpeg options
        try:
            source = FFmpegPCMAudio(
                audio_url,
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn -bufsize 512k"
            )
            ctx.voice_client.play(source, after=lambda e: print(f"Playback finished: {e}") if e else None)
        except Exception as play_error:
            await ctx.send(f"❌ Error starting playback: {str(play_error)}")
            print(f"FFmpeg error: {play_error}")
            
    except Exception as e:
        await ctx.send(f"❌ Error playing audio: {str(e)}")
        print(f"Play error: {e}")

@bot.command(name='stop', aliases=['s'])
async def stop_command(ctx):
    """Stop audio playback"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("⏹️ Stopped playback")
    else:
        await ctx.send("❌ Nothing is playing!")

@bot.command(name='pause')
async def pause_command(ctx):
    """Pause audio playback"""
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.pause()
        await ctx.send("⏸️ Paused")
    else:
        await ctx.send("❌ Nothing is playing!")

@bot.command(name='resume')
async def resume_command(ctx):
    """Resume audio playback"""
    if ctx.voice_client and ctx.voice_client.is_paused():
        ctx.voice_client.resume()
        await ctx.send("▶️ Resumed")
    else:
        await ctx.send("❌ Nothing is paused!")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing required argument. Use `!help` for usage information.")
    else:
        await ctx.send(f"❌ An error occurred: {str(error)}")
        print(f"Error: {error}")

# Run the bot
if __name__ == "__main__":
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        print(f"Failed to start bot: {e}")

