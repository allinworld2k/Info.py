# ================= AUTO INSTALL SYSTEM ================= #
import subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8')

packages = ["python-telegram-bot==20.3","psutil","pywin32","mss","platform","psutil"]
for p in packages:
    subprocess.call([sys.executable,"-m","pip","install",p])

# ================= IMPORTS ================= #
import psutil, win32gui, platform, socket, uuid
import mss, datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# ================= CONFIG ================= #
BOT_TOKEN = "8317448603:AAHvZCuksyy9wSW8UBzXspEl2UxBVIwdOYM"
ADMIN_ID = 6924124167
LOG_FILE = "process_log.txt"
SYSTEM_USERS = ["SYSTEM","LOCAL SERVICE","NETWORK SERVICE"]

# ================= MENU ================= #
def main_menu():
    keyboard = [
        [InlineKeyboardButton("📊 Running Processes", callback_data="process")],
        [InlineKeyboardButton("🖥 Taskbar Apps", callback_data="taskbar")],
        [InlineKeyboardButton("🔥 High CPU Alert", callback_data="highcpu")],
        [InlineKeyboardButton("📷 Remote Screenshot", callback_data="screenshot")],
        [InlineKeyboardButton("📁 Download Log", callback_data="log")],
        [InlineKeyboardButton("🖧 Full System Info", callback_data="system")],
        [InlineKeyboardButton("🔄 Refresh Menu", callback_data="menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# ================= START ================= #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    await update.message.reply_text("✅ Ultimate VPS Panel", reply_markup=main_menu())

# ================= BUTTON HANDLER ================= #
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.from_user.id != ADMIN_ID: return

    async def safe_edit(text, reply_markup=None):
        try:
            if query.message.text != text:
                await query.edit_message_text(text, reply_markup=reply_markup)
        except: pass

    # ================= MENU ================= #
    if query.data=="menu":
        await safe_edit("✅ Ultimate VPS Panel", reply_markup=main_menu())

    # ================= RUNNING PROCESSES ================= #
    elif query.data=="process":
        text="📊 Running Processes (Name + PID):\n\n"
        with open(LOG_FILE,"w",encoding="utf-8") as f:
            for proc in psutil.process_iter(['pid','name','username']):
                try:
                    pid=proc.info['pid']
                    name=proc.info['name']
                    user=proc.info['username']
                    line=f"{name} ({pid})\n"
                    f.write(line)
                    if len(text)<3500: text+=line
                except: pass
        await safe_edit(text[:3500])

    # ================= TASKBAR ================= #
    elif query.data=="taskbar":
        windows=[]
        def enum(hwnd,res):
            if win32gui.IsWindowVisible(hwnd):
                title=win32gui.GetWindowText(hwnd)
                if title: res.append(title)
        win32gui.EnumWindows(enum,windows)
        text="🖥 Taskbar Apps:\n\n"+'\n'.join(windows)
        await safe_edit(text[:3500], reply_markup=main_menu())

    # ================= HIGH CPU ================= #
    elif query.data=="highcpu":
        text="🔥 High CPU Processes (>10%):\n\n"
        for proc in psutil.process_iter(['pid','name','cpu_percent']):
            try:
                if proc.info['cpu_percent']>10:
                    text+=f"{proc.info['pid']} - {proc.info['name']} ({proc.info['cpu_percent']}%)\n"
            except: pass
        await safe_edit(text[:3500], reply_markup=main_menu())

    # ================= REMOTE SCREENSHOT ================= #
    elif query.data=="screenshot":
        try:
            img_path="screenshot.png"
            with mss.mss() as sct:
                sct.shot(output=img_path)
            await query.message.reply_photo(photo=open(img_path,"rb"))
            os.remove(img_path)
        except Exception as e:
            await safe_edit(f"❌ Screenshot failed!\nError: {str(e)}", reply_markup=main_menu())

    # ================= LOG ================= #
    elif query.data=="log":
        await query.message.reply_document(open(LOG_FILE,"rb"))

    # ================= FULL SYSTEM INFO ================= #
    elif query.data=="system":
        try:
            uname = platform.uname()
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
            svmem = psutil.virtual_memory()
            disks = psutil.disk_partitions()
            disk_info = ""
            for disk in disks:
                usage = psutil.disk_usage(disk.mountpoint)
                disk_info += f"{disk.device} ({disk.mountpoint}) - {round(usage.used/1024/1024/1024,2)}GB/{round(usage.total/1024/1024/1024,2)}GB used\n"
            users = psutil.users()
            text = f"🖧 Full System Information:\n\n"
            text += f"System: {uname.system}\nNode Name: {uname.node}\nRelease: {uname.release}\nVersion: {uname.version}\nMachine: {uname.machine}\nProcessor: {uname.processor}\nBoot Time: {boot_time}\n\n"
            text += f"RAM: {round(svmem.total/1024/1024/1024,2)} GB\n\nDisk Info:\n{disk_info}\n"
            text += "Users:\n"
            for u in users:
                text += f"{u.name} (Terminal:{u.terminal})\n"
            text += f"\nHostname: {socket.gethostname()}\nIP Address: {socket.gethostbyname(socket.gethostname())}\n"
            await safe_edit(text, reply_markup=main_menu())
        except Exception as e:
            await safe_edit(f"❌ Failed to fetch system info!\nError: {str(e)}", reply_markup=main_menu())

# ================= KILL COMMAND ================= #
async def kill(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if len(context.args)==1:
        pid=int(context.args[0])
        try:
            p=psutil.Process(pid)
            if p.username() in SYSTEM_USERS:
                await update.message.reply_text("❌ Cannot kill system process!")
            else:
                p.terminate()
                await update.message.reply_text(f"✅ Process {pid} ({p.name()}) terminated.")
        except:
            await update.message.reply_text("❌ Failed to terminate process.")

# ================= RUN BOT ================= #
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start",start))
app.add_handler(CommandHandler("kill",kill))
app.add_handler(CallbackQueryHandler(button_handler))

print("🚀 Ultimate VPS Monitor Bot Started...")
app.run_polling()