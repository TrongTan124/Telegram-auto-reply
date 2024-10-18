from telethon import TelegramClient, events
import asyncio
import time
from datetime import datetime

# Nhập API ID và API Hash từ Telegram Developer Platform
api_id = '12345678'
api_hash = 'abcd1234xxxxxxxxxxxxxxxxxx'

# Tạo Telegram Client
client = TelegramClient('auto_reply_session.session', api_id, api_hash)

# Dictionary lưu thông tin người đã được trả lời: {user_id: {"last_reply_time": timestamp, "waiting_for_manual": bool}}
replied_users = {}

# Tin nhắn tự động
auto_reply_message = (
    "<<Message auto reply>> Hiện tại tôi đang bận hoặc không có internet. "
    "Xin hãy để lại lời nhắn đầy đủ, tôi sẽ trả lời bạn ngay khi có thể."
)

# File log để ghi nhật ký
LOG_FILE = "telegram_auto_reply.log"

# Hàm ghi log
def write_log(message):
    """Ghi log vào file với thời gian hiện tại."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# Hàm xác định thời gian offline threshold dựa trên giờ hiện tại
def get_offline_threshold():
    """Trả về thời gian offline threshold dựa vào khung giờ."""
    current_hour = datetime.now().hour
    if 9 <= current_hour < 18:
        return 600  # 10 phút (600 giây)
    else:
        return 300  # 5 phút (300 giây)

# Lưu thời gian hoạt động gần nhất
last_activity = time.time()

# Xử lý tin nhắn gửi đi để cập nhật trạng thái hoạt động
@client.on(events.NewMessage(outgoing=True))
async def outgoing_handler(event):
    global last_activity

    # Cập nhật thời gian hoạt động
    last_activity = time.time()

    # Nếu bạn đã gửi tin nhắn thủ công cho ai đó, xóa người đó khỏi danh sách chờ phản hồi
    if event.chat_id in replied_users:
        del replied_users[event.chat_id]
        write_log(f"Đã xóa {event.chat_id} khỏi danh sách chờ phản hồi sau khi bạn gửi tin nhắn thủ công.")

# Xử lý tin nhắn đến và bỏ qua tin nhắn nhóm
@client.on(events.NewMessage(incoming=True))
async def incoming_handler(event):
    global last_activity

    # Kiểm tra xem tin nhắn có phải từ cuộc trò chuyện cá nhân không
    if event.is_private:
        sender = await event.get_sender()
        offline_threshold = get_offline_threshold()

        # Lấy thông tin người dùng từ danh sách đã trả lời (nếu có)
        user_data = replied_users.get(sender.id, {"last_reply_time": 0, "waiting_for_manual": False})

        # Nếu đã gửi tin nhắn tự động và đang chờ phản hồi thủ công, bỏ qua
        if user_data["waiting_for_manual"]:
            write_log(f"Bỏ qua tin nhắn từ {sender.id}, đang chờ bạn gửi tin thủ công.")
            return

        # Nếu bạn đang offline và chưa gửi tin nhắn tự động cho người này
        if time.time() - last_activity > offline_threshold and user_data["last_reply_time"] == 0:
            await event.reply(auto_reply_message)
            replied_users[sender.id] = {
                "last_reply_time": time.time(),
                "waiting_for_manual": True  # Đánh dấu cần phản hồi thủ công
            }
            write_log(f"Đã gửi tin nhắn tự động tới {sender.id}.")
        else:
            write_log(f"Bỏ qua tin nhắn từ {sender.id}, bạn đang online hoặc đã gửi trước đó.")
    else:
        write_log(f"Bỏ qua tin nhắn từ nhóm {event.chat_id}.")

# Hàm kiểm tra các tin nhắn chưa được phản hồi
async def check_unreplied():
    while True:
        offline_threshold = get_offline_threshold()
        current_time = time.time()

        # Duyệt qua danh sách người dùng đã được trả lời
        for user_id, data in list(replied_users.items()):
            # Nếu đã quá thời gian chờ và chưa phản hồi thủ công, ghi log
            if data["waiting_for_manual"] and current_time - data["last_reply_time"] > offline_threshold:
                write_log(f"Đang chờ bạn gửi tin nhắn thủ công cho {user_id}.")

        await asyncio.sleep(60)  # Đợi 1 phút trước khi kiểm tra lại

# Chạy Telegram client và kiểm tra tin nhắn chưa được phản hồi
async def main():
    write_log("Auto-reply bot đã bắt đầu chạy.")
    await client.start()

    # Chạy hàm kiểm tra các tin nhắn chưa được phản hồi song song với client
    await asyncio.gather(
        client.run_until_disconnected(),
        check_unreplied()
    )

# Khởi chạy
if __name__ == '__main__':
    asyncio.run(main())
