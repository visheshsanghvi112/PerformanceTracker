import datetime
import csv
from io import StringIO
from sheets import get_all_records
from config import ADMIN_IDS
from telegram.constants import ParseMode

async def send_summary(update, context, label, from_date):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ You're not authorized to view the summary.")
        return

    data = get_all_records()
    results = []

    for entry in data:
        try:
            entry_date = datetime.datetime.strptime(entry['Date'], "%d-%m-%Y")
            if entry_date >= from_date:
                results.append(entry)
        except:
            continue

    if not results:
        await update.message.reply_text(f"📭 No entries found for this {label.lower()}.")
        return

    # Table-style summary
    header = f"{'Date':<12} {'Name':<18} {'Type':<10} {'Client':<15} {'Orders':<6} {'Amount':<10} {'Location':<12} {'Remarks'}"
    lines = [header, "-" * 100]
    for entry in results:
        lines.append(
            f"{entry['Date']:<12} {entry['Name']:<18} {entry['Type']:<10} {entry['Client']:<15} {entry['Orders']:<6} ₹{entry['Amount']:<9} {entry['Location']:<12} {entry['Remarks']}"
        )
    table_text = "\n".join(lines)

    await update.message.reply_text(
        f"📊 *{label} Summary:*\n\n<pre>{table_text}</pre>",
        parse_mode=ParseMode.HTML
    )

    # CSV file generation
    csv_buffer = StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=results[0].keys())
    writer.writeheader()
    writer.writerows(results)
    csv_buffer.seek(0)

    await context.bot.send_document(
        chat_id=update.effective_chat.id,
        filename=f"{label.lower()}_summary.csv",
        document=csv_buffer,
        caption=f"🗂 {label} summary as CSV"
    ) 