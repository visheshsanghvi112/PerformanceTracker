from telegram import Update
from telegram.ext import ContextTypes
import datetime
from summaries import send_summary

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Performance Bot!\n\n"
        "Use /sales or /purchase to log your work.\n"
        "Admins can use /today /week /month for summaries.\n\n"
        "Example:\n"
        "Client: Apollo\nLocation: Bandra\nOrders: 3\nAmount: ₹24000\nRemarks: Good conversation"
    )

async def sales_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['type'] = 'Sales'
    await update.message.reply_text(
        "🧾 *Sales Entry Format:*\n"
        "`Client: Apollo`\n`Location: Bandra`\n`Orders: 3`\n`Amount: ₹24000`\n`Remarks: Good conversation`",
        parse_mode='Markdown'
    )

async def purchase_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['type'] = 'Purchase'
    await update.message.reply_text(
        "📦 *Purchase Entry Format:*\n"
        "`Client: ABC Suppliers`\n`Location: Lower Parel`\n`Orders: 2`\n`Amount: ₹18000`\n`Remarks: Delivered new stock`",
        parse_mode='Markdown'
    )

async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    await send_summary(update, context, "Today's", today_date)

async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    week_ago = datetime.datetime.now() - datetime.timedelta(days=7)
    week_ago = week_ago.replace(hour=0, minute=0, second=0, microsecond=0)
    await send_summary(update, context, "Weekly", week_ago)

async def month_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    month_ago = datetime.datetime.now() - datetime.timedelta(days=30)
    month_ago = month_ago.replace(hour=0, minute=0, second=0, microsecond=0)
    await send_summary(update, context, "Monthly", month_ago) 