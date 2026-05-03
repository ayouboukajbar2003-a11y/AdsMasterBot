#!/usr/bin/env python3
"""
🤖 Gulf Ecom Bot — 3 Agents
- Agent 1: Creative (Scripts + Captions)
- Agent 2: Landing Page (HTML)
- Agent 3: Product Research
"""

import os
import logging
import anthropic
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes

# ============ CONFIG ============
TELEGRAM_TOKEN = "8647674072:AAEZ9Vbb2gG-NdjY8JCLRYC1vVYimwIVTmQ"
ANTHROPIC_API_KEY = os.getenv("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", "")  # ضع مفتاحك هنا

# ============ AGENTS PROMPTS ============

CREATIVE_PROMPT = """أنت خبير تسويق متخصص في إعلانات ecommerce للسوق الخليجي السعودي.
مهمتك تكتب:
1. Script UGC بالسعودي (hook + problem + solution + proof + CTA)
2. Caption جاهز للنشر على TikTok/Snapchat/Meta
3. Hashtags مناسبة بالعربي والإنجليزي
4. نصائح للتصوير

القواعد:
- اللهجة سعودية خليجية دايماً
- مو لهجة مغربية أو مصرية
- CTA يذكر "الدفع عند الاستلام" دايماً
- احترم سياسات TikTok — بدون claims طبية مباشرة
- استخدم العاطفة والقصة مو الكلام الطبي

الرد يكون منظم وواضح بالعربي."""

LANDING_PAGE_PROMPT = """أنت خبير بناء landing pages للـ ecommerce الخليجي COD.
مهمتك تبني landing page HTML كاملة احترافية.

المتطلبات:
- RTL عربي كامل
- Mobile-first تصميم
- ألوان: أخضر للـ CTA، أبيض وداكن للخلفية
- Sections: Hero, Benefits, Before/After, Testimonials, Order Form, FAQ
- COD form مع: الاسم، الجوال، المدينة، الكمية
- مدن الخليج في الـ dropdown
- Urgency elements
- Social proof

أعط HTML كامل جاهز للنسخ مباشرة."""

RESEARCH_PROMPT = """أنت خبير product research للـ ecommerce الخليجي COD.
مهمتك تحلل المنتجات وتعطي توصيات مبنية على البيانات.

عند البحث عن منتجات اذكر:
1. اسم المنتج + وصف مختصر
2. ليش هو رابح في الخليج؟
3. target audience
4. هامش الربح المتوقع
5. keywords للبحث على PiPiADS
6. المنافسة (عالية/متوسطة/منخفضة)
7. توصيتك النهائية

ركز على: السعودية، الإمارات، الكويت، قطر
نموذج البيع: COD فقط
تجنب: منتجات تحتاج تصاريح معقدة"""

# ============ DETECT AGENT ============

def detect_agent(text: str) -> str:
    """يحدد أي agent يستخدم بناءً على الرسالة"""
    text_lower = text.lower()

    # Creative keywords
    creative_words = ["creative", "script", "سكريبت", "كريتيف", "caption", "كابشن",
                     "فيديو", "video", "اكتب", "ولد", "إعلان", "ad", "ugc",
                     "hook", "هوك", "نص", "كتب"]

    # Landing page keywords
    landing_words = ["landing", "لاندينج", "صفحة", "page", "html", "موقع",
                    "ابني", "بني", "store", "متجر"]

    # Research keywords
    research_words = ["research", "ريسيرش", "منتج", "product", "ابحث", "بحث",
                     "trending", "ترند", "pipiads", "نيش", "niche", "رابح",
                     "winning", "سوق", "market"]

    creative_score = sum(1 for w in creative_words if w in text_lower)
    landing_score = sum(1 for w in landing_words if w in text_lower)
    research_score = sum(1 for w in research_words if w in text_lower)

    if landing_score >= creative_score and landing_score >= research_score and landing_score > 0:
        return "landing"
    elif research_score >= creative_score and research_score > 0:
        return "research"
    else:
        return "creative"  # default

# ============ CALL CLAUDE ============

async def call_claude(system_prompt: str, user_message: str) -> str:
    """يستدعي Claude API"""
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}]
        )
        return message.content[0].text
    except Exception as e:
        return f"❌ خطأ في الـ API: {str(e)}\nتأكد من الـ ANTHROPIC_API_KEY"

# ============ HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """رسالة الترحيب"""
    welcome = """🤖 *Gulf Ecom Bot — 3 Agents*

أهلاً! أنا مساعدك الذكي للـ ecommerce الخليجي.

عندي 3 خبراء جاهزين:

🎨 *Agent 1 — Creative*
اكتب: "اكتب لي script لمنتج كيتو ACV"

📄 *Agent 2 — Landing Page*
اكتب: "ابني لي landing page لمنتج X"

🔍 *Agent 3 — Product Research*
اكتب: "ابحث لي على منتجات رابحة للسعودية"

---
كلمني بالعربي بشكل طبيعي وأنا أفهم! 💪"""

    await update.message.reply_text(welcome, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """أمثلة الاستخدام"""
    help_text = """📖 *أمثلة الاستخدام*

🎨 *Creative Agent:*
• "اكتب script لمنتج كيتو ACV للسعودية"
• "ولد caption لمنتج بواسير TikTok"
• "اكتب لي 3 hooks لمنتج تخسيس"

📄 *Landing Page Agent:*
• "ابني landing page لكيتو ACV سعر 149 ريال"
• "صفحة بيع لمنتج كريم بواسير COD"

🔍 *Research Agent:*
• "ابحث على منتجات رابحة للسعودية"
• "شنو أحسن niche دابا في الخليج"
• "حلل منتج car organizer للخليج"

---
_الـ bot يحدد تلقائياً أي agent يستخدم_ ✅"""

    await update.message.reply_text(help_text, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة كل رسالة"""
    user_message = update.message.text
    chat_id = update.message.chat_id

    # رسالة انتظار
    waiting_msg = await update.message.reply_text("⏳ كنخدم عليها...")

    # حدد الـ agent
    agent = detect_agent(user_message)

    # اختر الـ system prompt
    if agent == "creative":
        system = CREATIVE_PROMPT
        agent_label = "🎨 Creative Agent"
    elif agent == "landing":
        system = LANDING_PAGE_PROMPT
        agent_label = "📄 Landing Page Agent"
    else:
        system = RESEARCH_PROMPT
        agent_label = "🔍 Research Agent"

    # استدعي Claude
    response = await call_claude(system, user_message)

    # احذف رسالة الانتظار
    await waiting_msg.delete()

    # ابعث الجواب
    header = f"*{agent_label}*\n{'─' * 30}\n\n"

    # قسم الرسالة إذا طويلة (Telegram limit 4096)
    full_response = header + response

    if len(full_response) <= 4096:
        await update.message.reply_text(full_response, parse_mode="Markdown")
    else:
        # ابعث على أجزاء
        chunks = [full_response[i:i+4000] for i in range(0, len(full_response), 4000)]
        for i, chunk in enumerate(chunks):
            if i == 0:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            else:
                await update.message.reply_text(chunk)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الأخطاء"""
    logging.error(f"Error: {context.error}")
    if update and update.message:
        await update.message.reply_text("❌ صرا خطأ — حاول مرة أخرى")

# ============ MAIN ============

def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    print("🤖 Gulf Ecom Bot starting...")
    print("✅ Telegram Token: OK")
    print(f"✅ Anthropic API: {'OK' if ANTHROPIC_API_KEY else '❌ Missing!'}")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Errors
    app.add_error_handler(error_handler)

    print("🚀 Bot is running!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
