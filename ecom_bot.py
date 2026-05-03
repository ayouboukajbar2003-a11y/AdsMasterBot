#!/usr/bin/env python3
import os
import logging
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8647674072:AAEZ9Vbb2gG-NdjY8JCLRYC1vVYimwIVTmQ"

CREATIVE_PROMPT = """أنت خبير تسويق متخصص في إعلانات ecommerce للسوق الخليجي السعودي.
مهمتك تكتب:
1. Script UGC بالسعودي (hook + problem + solution + proof + CTA)
2. Caption جاهز للنشر على TikTok/Snapchat/Meta
3. Hashtags مناسبة بالعربي والإنجليزي
4. نصائح للتصوير
القواعد:
- اللهجة سعودية خليجية دايماً
- CTA يذكر الدفع عند الاستلام دايماً
- احترم سياسات TikTok بدون claims طبية مباشرة"""

LANDING_PAGE_PROMPT = """أنت خبير بناء landing pages للـ ecommerce الخليجي COD.
ابني landing page HTML كاملة:
- RTL عربي كامل، Mobile-first
- Sections: Hero, Benefits, Before/After, Testimonials, Order Form, FAQ
- COD form مع: الاسم، الجوال، المدينة، الكمية
- مدن الخليج في dropdown
- Urgency elements وCTA أخضر"""

RESEARCH_PROMPT = """أنت خبير product research للـ ecommerce الخليجي COD.
لكل منتج اذكر:
1. الاسم والوصف
2. ليش رابح في الخليج؟
3. target audience
4. هامش الربح المتوقع
5. keywords لـ PiPiADS
6. مستوى المنافسة
7. توصيتك النهائية
ركز على السعودية الإمارات الكويت قطر COD فقط"""

def detect_agent(text: str) -> str:
    text_lower = text.lower()
    landing_words = ["landing", "لاندينج", "صفحة", "page", "html", "ابني", "بني", "متجر"]
    research_words = ["research", "منتج", "product", "ابحث", "بحث", "trending", "نيش", "niche", "رابح", "سوق"]
    landing_score = sum(1 for w in landing_words if w in text_lower)
    research_score = sum(1 for w in research_words if w in text_lower)
    if landing_score > 0 and landing_score >= research_score:
        return "landing"
    elif research_score > 0:
        return "research"
    return "creative"

def call_claude_api(system_prompt: str, user_message: str) -> str:
    """يستدعي Claude API مباشرة بدون library"""
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not api_key:
        # طباعة كل الـ environment variables للتشخيص
        env_keys = [k for k in os.environ.keys()]
        return f"❌ API Key مو موجود\nكل الـ vars: {env_keys[:20]}"

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}]
    }

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=60
        )

        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            return f"❌ API Error {response.status_code}: {response.text[:500]}"

    except Exception as e:
        return f"❌ Request Error: {str(e)}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    status = f"✅ موجود ({api_key[:10]}...)" if api_key else "❌ مو موجود"
    welcome = f"""🤖 Gulf Ecom Bot — 3 Agents

API Key: {status}

عندي 3 خبراء:
🎨 Creative — اكتب لي script لمنتج X
📄 Landing Page — ابني لي landing page
🔍 Research — ابحث منتجات رابحة

كلمني بالعربي 💪"""
    await update.message.reply_text(welcome)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    waiting_msg = await update.message.reply_text("⏳ كنخدم عليها...")
    agent = detect_agent(user_message)
    if agent == "creative":
        system, label = CREATIVE_PROMPT, "🎨 Creative Agent"
    elif agent == "landing":
        system, label = LANDING_PAGE_PROMPT, "📄 Landing Page Agent"
    else:
        system, label = RESEARCH_PROMPT, "🔍 Research Agent"
    response = call_claude_api(system, user_message)
    await waiting_msg.delete()
    full = f"{label}\n{'─'*30}\n\n{response}"
    chunks = [full[i:i+4000] for i in range(0, len(full), 4000)]
    for chunk in chunks:
        await update.message.reply_text(chunk)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.error(f"Error: {context.error}")

def main():
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    print(f"🤖 Starting... API Key: {'OK-' + api_key[:10] if api_key else 'MISSING'}")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    print("🚀 Running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
