# Mô tả

Do thường xuyên sử dụng telegram để trao đổi công việc. Nên tôi phát triển tính năng cho phép trả lời tự động tin nhắn telegram khi có việc bận hoặc không có internet. 

# Yêu cầu

Chương trình trả lời tự động tin nhắn telegram cần có các tính năng sau:

- Tự động gửi tin nhắn khi offline
- Chỉ trả lời tin nhắn gửi trực tiếp, bỏ qua các tin nhắn trong nhóm
- Khi online mà không trả lời tin nhắn thì ghi nhận offline sau 10p (nếu là 9h - 18h), ghi nhận offline sau 5p ở khoảng thời gian còn lại.
- Không thực hiện gửi lặp tin nhắn với những người đã gửi tin nhắn rồi. Chỉ phản hồi tự động 1 lần cho tới khi được trả lời thủ công
- Tự động trả lời với các người dùng chưa phản hồi
- Đồng thời cũng không tự trả lời tin nhắn mà đã đọc, nhưng chưa phản hồi
- Khi người được phản hồi thì sẽ bỏ ra khỏi danh sách đã trả lời tự động.

# Phát triển

Sử dụng công cụ chatGPT để hỗ trợ sinh ra max nguồn sau.

File autoreply.py trong thư mục

# Triển khai

Đầu tiên là cần một máy chủ có kết nối internet để chạy ứng dụng. Tôi sử dụng máy chủ chạy HĐH Ubuntu 22.04.

Tiếp theo, lấy thông tin kết nối của telegram.

- Truy cập vào link https://my.telegram.org
    - Nhập số điện thoại
    - Nhập mã OTP 
    - Trường hợp có thêm xác thực 2 lớp thì nhập tiếp password

- Sau khi đăng nhập, chọn vào API development tools

- Nhập thông tin để tạo ứng dụng mới:
    - App title: tên cho ứng dụng, ví dụ autoreply
    - Short name: tên viết tắt
    - Platform: desktop
    - Description: không bắt buộc
    - Nhấn Create Application

- Lấy API ID và API Hash. Lưu 2 thông tin này để sử dụng cho chương trình. Cần bảo mật cẩn thận 02 thông tin này.

- Nhập API ID và API Hash vào trong chương trình.

- Chạy thử chương trình bằng lệnh `python autoreply.py`
    - Nhập số điện thoại
    - Nhập mã OTP
    - Nhập mật khẩu
    - Chương trình sẽ tạo ra một file có mở rộng là .session. Từ lần sau sẽ không cần nhập thông tin đăng nhập mỗi khi chạy chương trình nữa.

- Tạo systemd service
    - Tạo file mới `vim /etc/systemd/system/telegram_auto_reply.service`
    - Điền nội dung sau:

    ```sh
    [Unit]
    Description=Telegram Auto Reply Service
    After=network.target

    [Service]
    ExecStart=/usr/bin/python3 /path/to/your/auto_reply_log.py
    WorkingDirectory=/path/to/your/
    Restart=always
    User=your-username
    StandardOutput=append:/path/to/telegram_auto_reply.log
    StandardError=append:/path/to/telegram_auto_reply_error.log

    [Install]
    WantedBy=multi-user.target

    ```

    - Sửa lại đường dẫn tới nơi lưu chương trình. username thì thay bằng user sử dụng trên máy chủ Ubuntu 22.04
    - Kích hoạt và khởi động chương trình

    ```sh
    sudo systemctl daemon-reload
    sudo systemctl enable telegram_auto_reply.service
    sudo systemctl start telegram_auto_reply.service
    sudo systemctl status telegram_auto_reply.service
    ```

    - Kiểm tra log và debug

    ```sh
    sudo journalctl -u telegram_auto_reply.service -f
    ```


# Kết quả

Chương trình sẽ tự động gửi tin nhắn phản hồi khi bạn offline.