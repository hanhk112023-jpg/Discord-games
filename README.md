# Tiên Đồ Vô Tận · Telegram Mini App

Game tu tiên tiếng Việt, lấy **Telegram Mini App làm giao diện chính**. Một thân áo vải,
một ý niệm trường sinh: nhập đạo, tọa thiền, vượt ải yêu vương, thu thập pháp bảo.
Bot Telegram là cửa vào game và kênh lệnh phụ trợ, dùng chung nhân vật và SQLite với Mini App.

## Có gì mới?

- **Động phủ** tông ngọc bích–vàng cổ, tranh tiên sơn, đạo hạnh và thanh tu vi lấy từ máy chủ.
- **7 ải yêu vương cá nhân**: mở lần lượt theo cảnh giới, lưu tiến độ mỗi kiếp, thưởng một lần mỗi ải.
- **Túi càn khôn** có ảnh vật phẩm, lọc loại, xem chi tiết, dùng đan, trang bị và bán vật phẩm.
- **Vạn vật phổ** gồm 76 vật phẩm có tìm kiếm; đồ tham khảo được phân biệt với đồ đang sở hữu.
- **Du ngoạn, đan phòng, tông môn** nối trực tiếp vào lõi lệnh hiện có; kết quả kể qua ngăn nhật ký.
- **Hiệu ứng** linh khí, vòng đạo hạnh, ra đòn, chuyển màn và haptic Telegram. Có nút tắt,
  tự tôn trọng thiết lập `prefers-reduced-motion`.
- Giao diện co giãn cho điện thoại/máy tính, điều hướng dưới màn hình trên mobile,
  font tiếng Việt và ảnh phục vụ ngay từ ứng dụng.
- Đã loại bỏ bot, cogs, giao diện, công cụ diễn tập và dependency Discord.

## Chạy ngay, không cần token

Yêu cầu Python 3.10+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

Mở **http://localhost:8080**. Ứng dụng lắng nghe `0.0.0.0`, dùng API cùng origin;
không cần Node hay build frontend. Không có token thì mở chế độ trải nghiệm khách.

Bấm **Bước vào tiên đồ**, nhập đạo hiệu, chọn xuất thân. Tu luyện để tích lũy tu vi,
trang bị pháp bảo trong túi, rồi vào **Ải yêu vương** để thử sức.

**Lưu ý về khách:** danh tính gắn với cookie trình duyệt, không phải IP, không tự chuyển sang
nhân vật Telegram. Nếu không đặt `MINI_SESSION_SECRET` và không có token, khóa cookie thay đổi
khi khởi động lại. Muốn giữ phiên khách qua restart, đặt secret ngẫu nhiên dài trong `.env`
(ví dụ tạo bằng `python -c "import secrets; print(secrets.token_hex(32))"`). Không commit secret.

## Đưa vào Telegram

1. Tạo bot ở **@BotFather**, đặt `TELEGRAM_TOKEN` trong `.env` trên máy chủ.
2. Triển khai app tại một URL **HTTPS** ổn định, trỏ reverse proxy vào `WEB_PORT` (mặc định 8080).
   Proxy cần giữ đúng `Host` và truyền `X-Forwarded-Proto: https`.
3. Đặt `TELE_MINIAPP_URL=https://ten-mien-cua-ban` rồi chạy `python run.py`.
4. Mở bot, bấm **Chơi Tiên Đồ** ở menu hoặc nút trong `/start`.
   Có thể cấu hình Main Mini App trong BotFather bằng cùng URL này.

`python run.py` luôn chạy Mini App; nếu có token thì khởi động thêm bot.
`python run_tele.py --mini` tương đương. `python run_tele.py` chỉ chạy bot khi cần.

Khi có token, máy chủ mặc định **chỉ chấp nhận phiên Telegram đã xác thực**.
`initData` được kiểm HMAC và thời gian ký, không tin `initDataUnsafe` hay user ID từ frontend.
Chữ ký sai/hết hạn trả 401, không âm thầm hạ thành khách. `TELE_ALLOW_GUEST=1` chỉ dùng khi
chủ động muốn mở trải nghiệm web song song. Đăng nhập chính chủ dùng cookie HttpOnly/Secure.

### Cấu hình

| Biến | Mục đích |
| --- | --- |
| `TELEGRAM_TOKEN` | Token máy chủ từ BotFather; trống để chạy thử web |
| `TELE_MINIAPP_URL` | URL HTTPS cho nút mở Mini App |
| `WEB_PORT` | Cổng HTTP, mặc định `8080` |
| `DB_PATH` | SQLite, mặc định `data/tienlo.sqlite3` |
| `TELE_GUILD` | Mã thế giới, mặc định `1`; giữ tên cũ để tương thích dữ liệu |
| `TELE_ADMIN_IDS` | Telegram user ID có quyền triệu boss thế giới/đổi trời, phân cách dấu phẩy |
| `BOSS_XAC_SUAT` | Xác suất yêu vương thế giới thức tỉnh mỗi lần gieo quẻ |
| `CAP_TOC` | `1` để rút ngắn hồi chiêu khi thử nghiệm, không dùng production |
| `TELE_ALLOW_GUEST` | `1` để cho khách web chơi kể cả khi đã có token |
| `MINI_SESSION_SECRET` | Khóa cookie riêng; nếu trống dùng token bot hoặc khóa tạm |

Chạy **một tiến trình game** cho mỗi SQLite. Lõi bot và Mini App dùng cùng khóa xử lý lệnh;
vòng tuần tra cũng dùng khóa đó. Không chạy nhiều worker lên cùng sổ vì các cuộc giao đấu,
phiên đăng ký và khóa điều phối nằm trong tiến trình.

Dùng ổ đĩa bền vững, sao lưu SQLite bằng backup API; không commit CSDL vào Git.
Các script `tools/actions_giu.py` và `tools/workflows/` là công cụ triển khai thử cũ,
**không được chạy tự động**, không phải cam kết hosting 24/7. Nên dùng máy chủ/container có
volume bền vững cho game thật.

## Bảy ải huyễn cảnh

Các ải là **bóng chiếu cá nhân**, độc lập với boss thế giới. Không cần quyền admin để tham gia.
Dùng cùng bộ máy giao đấu, cảnh giới, pháp bảo, đạo tâm và thân thể như phần còn lại của game.

| Ải | Bóng yêu vương | Cảnh giới tối thiểu | Thưởng lần đầu |
| --- | --- | --- | --- |
| 1 | Thiết Nha Trư Vương | Luyện Khí tầng 1 | 50 linh thạch + Hồi Khí Đan |
| 2 | Xích Diệm Xà Vương | Trúc Cơ | 100 linh thạch + Thanh Cương Kiếm |
| 3 | Bạch Cốt Tinh Tôn | Kết Đan | 150 linh thạch + Yêu Đan |
| 4 | U Thuỷ Giao Long | Nguyên Anh | 200 linh thạch + U Đàm Liên |
| 5 | Huyết Ma Tôn | Hóa Thần | 250 linh thạch + Long Văn Ngọc |
| 6 | Thập Vạn Lôi Thú | Luyện Hư | 300 linh thạch + Lạc Lô Tinh Kim |
| 7 | Cửu U Ma Vương | Hợp Thể | 350 linh thạch + Độ Ách Đan |

- Phải qua ải trước, đủ cảnh giới, còn sống và không trọng thương; thân thể ít nhất 20.
- Ải đầu giảm sức mạnh so với yêu vương thật để phù hợp người mới. Không đảm bảo thắng.
- Thất bại mất tối đa 20 thân thể, không chết trong huyễn cảnh, không mất tiến độ. Có thể dưỡng thương và thử lại.
- Hồi kiếm khí 60 giây mỗi trận (co giãn theo chế độ thử nghiệm).
- Thưởng + tiến độ + hồi chiêu + nhật ký ghi trong cùng transaction SQLite.
- Máy chủ kiểm tra mọi điều kiện; bấm đúp hoặc gửi lại lệnh không nhận thưởng trùng.
- Tiến độ nằm trong `tu_si.ghi_chu.bi_canh`; nhân vật mới/chuyển thế bắt đầu lại từ ải đầu.

Boss thế giới vẫn hoạt động qua nút **Boss thế giới**, giữ cơ chế nhiều người cùng đánh,
thương tích, thời hạn và chia chiến lợi phẩm theo đóng góp. Chỉ admin (hoặc chế độ diễn tập)
có thể chủ động triệu boss thế giới.

## Lệnh phụ trợ

Trong ngăn **Chuyện trên đường tu** hoặc chat bot:

- Nhân vật: `/dangky`, `/nhanvat`, `/tuido`, `/nhatky`, `/chuyenthe`, `/xoa`.
- Tu luyện: `/luyentap`, `/thiennhien`, `/dotpha`, `/duongthuong`, `/uongdan`.
- Phiêu lưu: `/khampha`, `/diadanh`, `/timduoc`, `/duykysi`.
- Luyện chế: `/sotay`, `/luyendan`, `/luyenkhi`, `/deo`, `/vatpham`.
- Tông môn: `/monphai`, `/gianhap`, `/roimon`, `/nhiemvu`.
- Giao thương: `/cuahang`, `/mua`, `/ban`, `/tang`, `/tl`.
- Boss: `/boss`, `/daboss`, `/bosssach`, `/trieuboss`, `/bicanh <mã_boss>`.
- PK: `/pk <tên> [cược] [sinhtu]`, `/thach`, `/bangpk`.
- Thư tịch: `/canhgioi`, `/kiepnan`, `/binhkhi`, `/linhdan`, `/kimdan`, `/chidan`.
- Telegram: `/start`, `/menu`, `/mini`. Hủy bước nhập tên bằng `/huy`.

Xem [luật tu luyện, cảnh giới, thế giới và PK](docs/LUAT_CHOI.md).
Phần kể chuyện vẫn giữ văn phong tiên hiệp; Mini App bổ sung chỉ số trực quan để dễ thao tác.

## Cấu trúc

```text
run.py                     # Mini App mặc định + bot nếu có token
run_tele.py                # điểm khởi Telegram, tùy chọn chỉ bot
requirements.txt           # aiohttp, aiogram, aiosqlite, python-dotenv
assets/tranh/              # tiên sơn, boss, tranh và SVG nhóm vật phẩm
assets/am/, thanh_anh/     # âm thanh/phim cho các khoảnh khắc trong truyện
tuchan/db.py               # sổ SQLite, transaction thưởng ải
tuchan/data/               # cảnh giới, xuất thân, vật phẩm, boss, tông môn
tuchan/he/                 # luật chơi; bicanh.py là 7 ải cá nhân
tuchan/tele/long.py        # lõi lệnh chung, tuần tự hóa thao tác
tuchan/tele/mini.py        # HTTP, initData, cookie, vòng đời Mini App
tuchan/tele/trang_thai.py  # dữ liệu giao diện lấy từ sổ thật
tuchan/tele/web/           # HTML/CSS/JS và font tự phục vụ
tests/test_mini.py         # kiểm thử xác thực, API, giao đấu, thưởng
```

Tranh động phủ và 7 chân dung yêu vương mới là tranh AI; SVG nhóm vật phẩm được vẽ trong repo.
Vật phẩm có tranh riêng dùng tranh đó, còn lại dùng ảnh theo nhóm, không phải 76 tranh độc lập.
Font Be Vietnam Pro và Noto Serif kèm giấy phép SIL OFL tại `tuchan/tele/web/fonts/`.

## Kiểm thử

```bash
python -m unittest discover -s tests -v
python -m compileall -q tuchan run.py run_tele.py
# Nếu có Node: chỉ kiểm tra cú pháp JS, không phải dependency runtime.
node --check tuchan/tele/web/dong.js
# Diễn tập toàn bộ lõi Telegram trong SQLite thử riêng:
python tools/tele_thutap.py --tu-dong
```

Bộ test dùng CSDL trong bộ nhớ, không cần Telegram token. Bao phủ chữ ký/hết hạn, tách phiên khách,
đăng ký, dữ liệu/ảnh, đầu vào lỗi, CSRF, cửa ải khóa, chết/thương nặng, hồi chiêu, thưởng một lần
khi lệnh đồng thời và rollback khi ghi chiến lợi phẩm lỗi.
