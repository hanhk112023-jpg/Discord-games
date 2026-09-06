# 仙途無盡 — Tiên Đồ Vô Tận

Một **bot Discord tu chân / tiên hiệp** viết bằng Python, theo lối **kinh điển, trường kỳ, khắc nghiệt**:
không thanh máu, không con số, không bảng nhiệm vụ, không một chữ "EXP" nào.
Mọi thứ được kể bằng văn — như đọc *Phàm Nhân Tu Tiên* hay *Tiên Nghịch*, chỉ khác là ngươi tự viết phần của mình.

> *"Ngươi mở mắt. Ngọn đèn đã cạn dầu tự bao giờ.*
> *Chân khí đã đi được một vòng châu thân mà không đứt quãng — ngươi bắt đầu hiểu vì sao người ta gọi đây là 'công phu'."*

---

## Bên trong có gì

| | |
|---|---|
| **Ngôn ngữ** | Python 3.10+ |
| **Thư viện** | discord.py 2.x — `commands.Bot` với **hybrid command**: mọi lệnh chạy được cả `!lenh` lẫn `/lenh` |
| **Dữ liệu** | SQLite qua `aiosqlite` (không cần cài server) |
| **Lệnh** | 35 lệnh, đều có bản prefix và bản slash |
| **Tranh** | 8 bức thuỷ mặc do model ảnh dựng riêng cho từng cảnh giới / địa danh |
| **Thanh ảnh** | 3 đoạn phim ngắn (Ken Burns + lời kể + gió + tiếng ngân trầm) đính kèm vào các khoảnh khắc lớn |
| **Lời kể** | 3 đoạn thu âm tiếng Việt cho nhập đạo, kết đan, và lời lão bán trà |

### Nguyên tắc văn phong (áp dụng cho toàn bộ mã nguồn)

* Người chơi **không bao giờ** đọc thấy con số của chính mình. Máy vẫn tính, nhưng phép tính nằm dưới lớp da.
  `tuchan/vanphong.py` là chỗ duy nhất đổi số thành chữ:

  | Trong máy | Người chơi đọc |
  |---|---|
  | `tu_vi = 118/120` | *"Chân khí đầy tới mức chèn cả vào kinh mạch. Mỗi lần thu công, ngươi nghe trong xương có tiếng rạn rất khẽ."* |
  | `than_the = 22` | *"Nội thương chưa lành hẳn. Sắc mặt ngươi trắng bệch, môi khô, đi được trăm bước thì phải dừng."* |
  | `dao_tam = 31` | *"Trong lúc vận công, thi thoảng ngươi nghe một giọng nói rất giống giọng mình, khuyên ngươi làm điều không nên."* |
  | `cooldown = 40 phút` | *"Đợi thêm nửa canh giờ nữa rồi hẵng ngồi xuống. Vội trên đường tu là cách chết chậm mà chắc."* |

* Không có "nhiệm vụ" — chỉ có **một vị chấp sự già gọi ngươi lại, nói vài câu, rồi quay đi**.
* Thất bại là chuyện thường, và thất bại có giá: mất đạo hạnh, gãy xương, tổn đạo tâm, mất đồ trong túi, và ở cảnh giới cao thì **chết hẳn** (còn `chuyenthe` để đầu thai, mang sang kiếp sau đúng một chút dư âm).

---

## Chạy thử trong ba mươi giây (không cần bot)

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python tools/mophong.py        # diễn tập trong terminal: chạy hết mọi hệ thống
python tools/web_dienrap.py    # mở http://localhost:8080 — chơi thử ngay trong trình duyệt
```

`tools/web_dienrap.py` dùng **đúng bộ máy** mà bot Discord dùng, chỉ khác cái miệng kể chuyện —
tiện để đọc thử văn phong, xem tranh và thanh ảnh trước khi dựng bot.

## Dựng bot thật

```bash
cp .env.example .env      # dán DISCORD_TOKEN vào
python run.py
```

Trong Developer Portal nhớ bật **Message Content Intent** và **Server Members Intent**.
Đặt `GUILD_ID` trong `.env` khi thử nghiệm để slash command hiện ra ngay (không phải chờ Discord đồng bộ toàn cục).

---

## Mười bậc thang trời

```
Luyện Khí (13 tầng) → Trúc Cơ → Kết Đan → Nguyên Anh → Hóa Thần
        → Luyện Hư → Hợp Thể → Đại Thừa → Độ Kiếp → Chân Tiên
```

Mỗi bậc có mô tả riêng về **khí tức người ngoài nhìn thấy**, **thân thể biến đổi ra sao**,
**cảm nhận thiên địa** và **địa vị trong nhân gian**. Lên bậc không phải là "chúc mừng bạn đã lên cấp":

> *"Kim đan nứt. Từ trong mảnh vỡ, một anh nhi bé bằng nắm tay ngồi dậy. Nó mở mắt.*
> *Nó có khuôn mặt của ngươi, nhưng bình thản hơn ngươi rất nhiều. Ngươi nhìn nó, và lần đầu tiên ngươi hiểu:*
> *cái thân xác này, từ nay chỉ là một bộ áo."*

Xung quan lên **cảnh giới mới** có tỉ lệ thành công rất thấp (34% ở Trúc Cơ, giảm dần).
Thất bại chia ba mức: khép cửa ải, kinh mạch đứt (nằm dưỡng thương), và **tẩu hoả nhập ma** (tổn đạo tâm; từ Đại Thừa trở lên có thể chết).
Thất bại nhiều lần thì tích thành cảm ngộ — lần sau dễ hơn một chút. Đó là tất cả sự tử tế mà thế giới này dành cho ngươi.

---

## Các lệnh

Mọi lệnh dùng được cả hai kiểu: `!luyentap` hoặc `/luyentap`.

**Nhân vật** · `dangky` (chọn xuất thân bằng menu, khai tên bằng modal) · `nhanvat` · `tuido` · `nhatky` · `banghieu` · `chuyenthe` · `xoaminh`

**Tu luyện** · `luyentap` (một canh giờ một lần) · `thiennhien` (nhanh gấp bội, có thể gặp ma nhiễm / kỵ sĩ / tẩu hoả) · `dotpha` (dùng được đan hỗ trợ) · `uongdan` · `duongthuong`

**Phiêu lưu** · `khampha` (8 địa danh, mỗi nơi có bảng gặp gỡ riêng) · `diadanh` · `timduoc` · `duykysi`

**Luyện chế** · `sotay` · `luyendan` · `luyenkhi` · `deo` (nhỏ tinh huyết nhận chủ pháp bảo) · `vatpham`

**Tông môn** · `monphai` · `gianhap` · `roimon` · `nhiemvu nhan|di|nop`

**Đối đầu** · `thidau @người` (đối phương phải bấm *Ứng chiến*; thêm `sinhtu:true` thì thắng thua tính bằng mạng)

**Giao thương** · `cuahang` · `mua` · `ban` · `tang @người [vật]` · `taolinhthach @người [số]`

**Trời đất** · `thientuong` · `khoisukien` *(cần quyền Quản lý máy chủ)* · `canhgioi` · `chidan`

---

## Thế giới

* **6 xuất thân**: phàm nhân, con nhà võ, thế gia sa sút, tán tu lang bạt, đạo đồng quét sân, cô nhi thời loạn.
  Mỗi lai lịch cho tư chất / căn cốt / đạo tâm / hành trang khác nhau, và một **lời thề** riêng.
* **6 tông môn**: Thanh Vân Môn, Huyền Vũ Tông, Vạn Dược Cốc, Liệt Hoả Kiếm Trai, U Minh Quỷ Đạo, Vọng Hải Tự —
  mỗi môn có công pháp riêng (ảnh hưởng tốc độ tu luyện, sức chiến, tỉ lệ thành đan), quy củ riêng, và cái giá riêng.
  *U Minh Quỷ Đạo cho tu vi nhanh gấp rưỡi thiên hạ, đổi lại mỗi bước tiến đều có mùi tanh.*
* **8 địa danh** từ Thanh Khê Sơn tới Cửu U Hàn Uyên, có yêu cầu cảnh giới và độ nguy hiểm riêng.
* **~40 vật phẩm**: dược liệu, vật liệu, đan dược, pháp bảo (đều có mô tả, không có "ATK +15").
* **13 công thức** đan phương / đồ hình luyện khí, học được qua ngọc giản nhặt ngoài đường hoặc tông môn ban cho.
* **10 loại địch**: từ Xích Mao Lang tới Cổ Thi Tướng, mỗi con có thủ đoạn riêng, được nhắc tên ngay trong lời kể trận đấu.
* **7 thiên biến** tự nổ ra theo thời gian (nửa giờ một lần gieo quẻ, 14% xảy ra) hoặc do quản trị kích hoạt:
  Linh Khí Triều Tịch, Ma Khí Nhiễu Loạn, Cổ Tích Khai Mở, Hội Võ Giang Hồ, Đại Hạn, Tinh Vẫn Giáng Thế, Huyết Nguyệt.
  Chúng nhân/chia tỉ lệ tu luyện, độ nguy hiểm, giá cả, tỉ lệ kỳ ngộ của **mọi người trong máy chủ**.

### Cách một trận đánh được kể

`tuchan/he/chiendau.py` không in ra sát thương. Nó tính sức chiến ngầm (cảnh giới, tầng, pháp bảo,
công pháp tông môn, căn cốt, thương thế, đạo tâm), gieo từng hiệp, rồi chọn câu kể theo **độ chênh của hiệp đó**:

> *"Hàn Lập bước tới một bước. Chỉ một bước, mà khoảng cách mười trượng biến mất.*
> *Thạch Giáp Thú co mình lại chịu trọn một đòn rồi phản kích.*
> *Đòn cuối cùng đến khi Hàn Lập vừa hụt hơi — Hàn Lập bay ngược ra sau, đập vào một thân cây, và cây gãy."*

Kết trận có một câu bình, khác nhau tuỳ thắng đậm, thắng sát nút, thua đậm hay thua trong gang tấc.

---

## Tranh, tiếng và thanh ảnh

```
assets/tranh/       8 bức thuỷ mặc: bìa, Luyện Khí, Kết Đan, Độ Kiếp,
                    Thanh Vân Môn, Hắc Phong Lâm, đan phòng, đấu pháp
assets/am/          3 đoạn lời kể tiếng Việt (nhập đạo, kết đan, lão bán trà)
assets/thanh_anh/   3 đoạn phim ~30–40 giây, mỗi tệp dưới 2 MB
```

Thanh ảnh được dựng bằng `tools/lam_thanh_anh.py` (ffmpeg đi kèm `imageio-ffmpeg`, không cần cài ngoài):
tranh được cho trôi chậm kiểu Ken Burns, hoà hình vào nhau, phủ vignette + hạt nhiễu như phim cũ,
rồi trộn ba lớp tiếng — **lời kể**, **gió** (nhiễu nâu lọc trầm) và **một tiếng ngân 58 Hz** gần như không nghe thấy
nhưng khiến người xem thấy nặng ngực.

Bot tự đính kèm:

| Khoảnh khắc | Tệp |
|---|---|
| Vừa nhập đạo (`dangky`) | `nhap_dao.mp4` |
| Đột phá **lên cảnh giới mới** (`dotpha`) | `dot_pha.mp4` |
| Nghe lão bán trà chỉ đường (`chidan`) | `giang_ho.mp4` |

Dựng lại (khi đổi tranh hoặc lời kể):

```bash
pip install imageio-ffmpeg
python tools/lam_thanh_anh.py            # dựng cả ba
python tools/lam_thanh_anh.py dot_pha    # dựng riêng một cảnh
```

---

## Cấu trúc mã nguồn

```
run.py                     điểm khởi động
tuchan/
  config.py                mọi con số cấu hình, kể cả hệ số co giãn thời gian
  canhgioi.py              10 cảnh giới: tầng, thọ nguyên, khí tức, cảm ngộ
  vanphong.py              đổi số thành chữ — trái tim của văn phong
  db.py                    SQLite: tu sĩ, túi đồ, sổ tay, nhật ký, việc môn, thiên biến
  giaodien.py              KetQua → embed Discord (tự cắt trang, đính tranh & phim)
  bot.py                   TuChanBot, nạp cog, đồng bộ slash
  data/                    thế giới tĩnh: vật phẩm, công thức, môn phái,
                           xuất thân, địa danh, địch thủ, sự kiện, việc môn
  he/                      luật chơi (chạy độc lập, không cần Discord)
    tuluyen · phieuluu · chiendau · luyenche · tongmon · thidau
    giaothuong · nhanvat · thienbien · thienco · ketqua
  cogs/                    tầng Discord, mỏng, chỉ gọi xuống he/
tools/
  mophong.py               diễn tập trong terminal
  web_dienrap.py           diễn tập trong trình duyệt
  lam_thanh_anh.py         dựng thanh ảnh
```

Toàn bộ luật chơi nằm trong `tuchan/he/` và **không import discord** — nhờ vậy có thể chạy thử,
kiểm tra, hay đem gắn vào chỗ khác (web, Telegram…) mà không phải sửa một dòng logic nào.

### Vặn lại các nút

Trong `.env`:

```bash
BOT_PREFIX=!            # đổi tiền tố
HE_SO_THOI_GIAN=1.0     # 0.05 = mọi thời gian chờ ngắn lại 20 lần
CAP_TOC=0               # đặt 1 khi thử nghiệm (tương đương hệ số 0.01)
```

Thời gian chờ mặc định: toạ quan 1 canh giờ · dẫn thiên địa 3 giờ · khám phá 30 phút ·
hái thuốc 20 phút · tỉ thí 15 phút · việc tông môn 2 giờ · dưỡng thương tối đa 6 giờ.

---

*"Đừng vội. Kẻ vội thì chết sớm, mà chết sớm thì không ai nhớ tên."*
