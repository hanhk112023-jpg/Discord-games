# 仙途無盡 — Tiên Đồ Vô Tận

Một **bot tu chân / tiên hiệp** viết bằng Python, chạy được trên **cả Discord lẫn Telegram**, theo lối
**kinh điển, trường kỳ, khắc nghiệt**:
không thanh máu, không con số, không bảng nhiệm vụ, không một chữ "EXP" nào.
Mọi thứ được kể bằng văn — như đọc *Phàm Nhân Tu Tiên* hay *Tiên Nghịch*, chỉ khác là ngươi tự viết phần của mình.

> *"Ngươi mở mắt. Ngọn đèn đã cạn dầu tự bao giờ.*
> *Chân khí đã đi được một vòng châu thân mà không đứt quãng — ngươi bắt đầu hiểu vì sao người ta gọi đây là 'công phu'."*

---

## Bên trong có gì

| | |
|---|---|
| **Ngôn ngữ** | Python 3.10+ |
| **Thư viện** | discord.py 2.x (hybrid: mọi lệnh chạy được cả `!lenh` lẫn `/lenh`) · aiogram 3 cho bản Telegram |
| **Boss & PK** | chiến trường yêu vương cả thế giới cùng đánh, chia công theo dấu chân để lại; PK có cược, thắng ăn cả |
| **Dữ liệu** | SQLite qua `aiosqlite` (không cần cài server) |
| **Lệnh** | 39 lệnh, đều có bản prefix và bản slash |
| **Tranh** | 18 bức thuỷ mặc do model ảnh dựng riêng: cảnh giới, địa danh, kim đan, binh khí, linh đan |
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

python tools/mophong.py        # diễn tập Discord trong terminal: chạy hết mọi hệ thống
python tools/web_dienrap.py    # mở http://localhost:8080 — Discord, chơi thử ngay trong trình duyệt

python tools/tele_thutap.py            # Telegram, trong terminal — gõ lệnh, ~1 bấm nút thứ nhất
python tools/tele_thutap.py --tu-dong  # tự chạy trọn kịch bản: nhập đạo → boss → PK → kiểm tra sổ sách
python tools/tele_dienrap.py           # Telegram, trong trình duyệt — khung chat giả lập, nút bấm thật
```

`tools/web_dienrap.py` dùng **đúng bộ máy** mà bot Discord dùng, chỉ khác cái miệng kể chuyện —
tiện để đọc thử văn phong, xem tranh và thanh ảnh trước khi dựng bot.

## Dựng bot thật

```bash
cp .env.example .env      # dán DISCORD_TOKEN vào
python run.py

# bản Telegram — chạy song song với bản Discord được, cùng một CSDL, cùng một thế giới
python run_tele.py        # cần TELEGRAM_TOKEN trong .env
```

Bot Telegram tạo ở @BotFather; không cần bật inline mode — mọi thứ đi qua lệnh và nút bấm,
`/menu` và `/help` liệt kê đủ.

Trong Developer Portal nhớ bật **Message Content Intent** và **Server Members Intent**.
Đặt `GUILD_ID` trong `.env` khi thử nghiệm để slash command hiện ra ngay (không phải chờ Discord đồng bộ toàn cục).

---

## Mười bậc thang trời — sáu mươi mốt bậc chân

```
Luyện Khí (13 tầng) → Trúc Cơ → Kết Đan → Nguyên Anh → Hóa Thần
        → Luyện Hư → Hợp Thể → Đại Thừa → Độ Kiếp → Chân Tiên
```

Mười cái tên ấy là cách người đời gọi cho gọn. Đi thật thì phải đếm từng bậc nhỏ:

| Cảnh giới | Số bậc | Cách gọi |
|---|---|---|
| Luyện Khí | 13 | tầng một → tầng mười ba |
| Trúc Cơ … Đại Thừa | 5 mỗi bậc | sơ kỳ · trung kỳ · hậu kỳ · đỉnh phong · **đại viên mãn** |
| Độ Kiếp | 9 | nhất trọng → cửu trọng, mỗi trọng là một lần lôi kiếp |
| Chân Tiên | 4 | Địa Tiên · Thiên Tiên · Kim Tiên · **Đại La** |

Cộng lại: **61 bậc**. Lên bậc không phải là "chúc mừng bạn đã lên cấp":

> *"Kim đan nứt. Từ trong mảnh vỡ, một anh nhi bé bằng nắm tay ngồi dậy. Nó mở mắt.*
> *Nó có khuôn mặt của ngươi, nhưng bình thản hơn ngươi rất nhiều. Ngươi nhìn nó, và lần đầu tiên ngươi hiểu:*
> *cái thân xác này, từ nay chỉ là một bộ áo."*

Xung quan lên **cảnh giới mới** có tỉ lệ thành công rất thấp (34% ở Trúc Cơ, giảm dần).
Thất bại chia ba mức: khép cửa ải, kinh mạch đứt (nằm dưỡng thương), và **tẩu hoả nhập ma** (tổn đạo tâm; từ Đại Thừa trở lên có thể chết).
Thất bại nhiều lần thì tích thành cảm ngộ — lần sau dễ hơn một chút. Đó là tất cả sự tử tế mà thế giới này dành cho ngươi.

### Chín cửa ải (`!kiepnan`)

Trước mỗi cảnh giới lớn, trời đặt sẵn một người gác cửa. Mỗi cửa được kể thành một cảnh riêng,
có thể qua đẹp (cộng vận cho cú xung quan ngay sau đó) hoặc hỏng nặng (mất đạo hạnh, nằm liệt, và ở bậc cao thì mất mạng).

| Cửa | Trước bậc | Nội dung |
|---|---|---|
| **Tẩy Tuỷ Phạt Mao** | Trúc Cơ | ép tạp chất ra khỏi tuỷ; qua đẹp thì căn cốt tăng vĩnh viễn |
| **Ngưng Đan** | Kết Đan | ngưng kim đan — **quyết định phẩm chất đan, theo ngươi tới cuối đời** |
| **Tâm Ma Kiếp** | Nguyên Anh | ba ma cảnh moi từ chỗ đau nhất của ngươi ra |
| **Tam Tai Chi Kiếp** | Hóa Thần | phong tai · hoả tai · lôi tai, đủ ba |
| **Phá Hư Khảo** | Luyện Hư | xé không gian, bước vào chỗ "không có gì", rồi nhớ đường về |
| **Hợp Đạo Khảo** | Hợp Thể | thần hồn và nhục thân giằng nhau bảy ngày |
| **Đại Thừa Tâm Ma** | Đại Thừa | tâm ma lần hai, nặng hơn, nhiều đợt hơn |
| **Tiểu Thiên Kiếp** | Độ Kiếp | lôi kiếp mở màn; sau đó **mỗi trọng trong chín trọng là một lần sét nữa** |
| **Cửu Trọng Đại Kiếp** | Chân Tiên | chín đạo. Qua được thì mây tách ra, và phía sau mây có bậc thang |

### Kim đan chín phẩm (`!kimdan`)

Cửa Kết Đan sinh ra một viên kim đan mang **phẩm chất từ 1 tới 9** (tuỳ tâm tính, tư chất, số lần từng thất bại,
và linh khí trời đất lúc ấy). Con số ấy **không bao giờ hiện ra dưới dạng con số** — người chơi chỉ đọc được:

> *Hạ phẩm — "Viên đan méo một bên, bề mặt rỗ như đá ong…"*
> *Cực phẩm — "Tròn tới mức nhìn lâu thấy chóng mặt. Trên mặt đan có một tầng vân sáng chảy chậm như sữa…"*

Nó ngầm ảnh hưởng tốc độ tu luyện, sức chiến, và tỉ lệ vượt mọi cửa ải về sau. Không sửa lại được. Không có đường tắt.

---

## Các lệnh

Mọi lệnh dùng được cả hai kiểu: `!luyentap` hoặc `/luyentap`.

**Nhân vật** · `dangky` (chọn xuất thân bằng menu, khai tên bằng modal) · `nhanvat` · `tuido` · `nhatky` · `banghieu` · `chuyenthe` · `xoaminh`

**Tu luyện** · `luyentap` (một canh giờ một lần) · `thiennhien` (nhanh gấp bội, có thể gặp ma nhiễm / kỵ sĩ / tẩu hoả) · `dotpha` (dùng được đan hỗ trợ) · `uongdan` · `duongthuong`

**Phiêu lưu** · `khampha` (8 địa danh, mỗi nơi có bảng gặp gỡ riêng) · `diadanh` · `timduoc` · `duykysi`

**Luyện chế** · `sotay` · `luyendan` · `luyenkhi` · `deo` (nhỏ tinh huyết nhận chủ pháp bảo) · `vatpham`

**Tông môn** · `monphai` · `gianhap` · `roimon` · `nhiemvu nhan|di|nop`

**Đối đầu** · `thidau @người [cược]` (đối phương phải bấm *Ứng chiến*; cược bằng linh thạch, hai bên cùng trừ trước trận,
thắng ăn cả; `sinhtu:true` thì thắng thua tính bằng mạng) · `tolich [số]` · `huthach`

**Yêu vương** · `boss` (chiến trường; tự hiện nút *Triệu yêu vương* khi chưa có boss) · `daboss` · `bosssach` *(admin gọi đích danh từng con)*

**Giao thương** · `cuahang` · `mua` · `ban` · `tang @người [vật]` · `taolinhthach @người [số]`

**Trời đất** · `thientuong` · `khoisukien` *(cần quyền Quản lý máy chủ)* · `chidan`

**Thư tịch** · `canhgioi` (bia mười bậc, 61 bậc chân) · `kiepnan` (chín cửa ải) · `binhkhi` (Binh Khí Phổ, lọc theo phẩm) · `linhdan` (Đan Phổ) · `kimdan` (chín phẩm kim đan)

---

## Thế giới

* **6 xuất thân**: phàm nhân, con nhà võ, thế gia sa sút, tán tu lang bạt, đạo đồng quét sân, cô nhi thời loạn.
  Mỗi lai lịch cho tư chất / căn cốt / đạo tâm / hành trang khác nhau, và một **lời thề** riêng.
* **6 tông môn**: Thanh Vân Môn, Huyền Vũ Tông, Vạn Dược Cốc, Liệt Hoả Kiếm Trai, U Minh Quỷ Đạo, Vọng Hải Tự —
  mỗi môn có công pháp riêng (ảnh hưởng tốc độ tu luyện, sức chiến, tỉ lệ thành đan), quy củ riêng, và cái giá riêng.
  *U Minh Quỷ Đạo cho tu vi nhanh gấp rưỡi thiên hạ, đổi lại mỗi bước tiến đều có mùi tanh.*
* **8 địa danh** từ Thanh Khê Sơn tới Cửu U Hàn Uyên, có yêu cầu cảnh giới và độ nguy hiểm riêng.
* **Chợ bốn tầng**: chợ ngoài ai cũng vào; lều bạt mở cho kẻ đã trúc cơ; gian nhà đá không cửa sổ cho kẻ đã kết đan;
  và một cái chợ họp giữa mây, ba năm một lần, chỉ hoá thần trở lên mới nhận được thiếp mời.
* **76 vật phẩm**: dược liệu, vật liệu, đan dược, pháp bảo (đều có mô tả, không có "ATK +15").
* **26 món binh khí thuộc 17 chủng loại** — kiếm, đao, thương, phi kiếm, cung, ti tuyến, chuỳ, phù lục, hộ giáp,
  pháp chung, ấn, phướn, bút, quạt, đan đỉnh, bảo kính, trảm đài. **Mỗi loại có bộ câu ra đòn riêng**:
  cầm trọng kiếm thì đánh khác cầm Truy Nguyệt Cung, và người đọc trận đấu nhận ra ngay.
* **21 loại linh đan**: đan phá quan cho từng cảnh giới (Trúc Cơ Đan → Hóa Thần Đan), đan hộ thể độ kiếp
  (Độ Ách Đan, Kim Cang Hộ Thể Đan, Ngưng Thần Đan), đan phá chướng, đan giấu khí tức, đan kéo thọ,
  và cả **Huyết Bồ Đề** — tăng tu vi rất nhanh, đổi lại sát nghiệp và đạo tâm.
* **37 công thức** đan phương / đồ hình luyện khí, học được qua ngọc giản nhặt ngoài đường hoặc tông môn ban cho.
* **10 loại địch**: từ Xích Mao Lang tới Cổ Thi Tướng, mỗi con có thủ đoạn riêng, được nhắc tên ngay trong lời kể trận đấu.
* **7 thiên biến** tự nổ ra theo thời gian (nửa giờ một lần gieo quẻ, 14% xảy ra) hoặc do quản trị kích hoạt:
  Linh Khí Triều Tịch, Ma Khí Nhiễu Loạn, Cổ Tích Khai Mở, Hội Võ Giang Hồ, Đại Hạn, Tinh Vẫn Giáng Thế, Huyết Nguyệt.
  Chúng nhân/chia tỉ lệ tu luyện, độ nguy hiểm, giá cả, tỉ lệ kỳ ngộ của **mọi người trong máy chủ**.

### Yêu vương — chiến trường của cả thế giới

Trời gieo quẻ nửa canh giờ một lần; ai đến trước bấm *Triệu yêu vương*, hoặc quản trị gọi đích danh qua `!bosssach`.
Yêu vương **hiện ra một lần cho cả thế giới**: huyết mạch riêng, không hồi phục, tới hạn thì tự mang mình về núi.

* Người cảnh giới quá thấp bị chặn ngay trước cửa trận — lời kể tự nó giải thích vì sao (*đó không phải đi đánh, mà là đi nộp mình*).
* Bị đánh nằm thì **chiến trường vẫn chờ**: dấu chân trên cát còn nguyên, hồi sức xong bấm *Đánh tiếp*.
* Hạ được boss: mỗi người nhận đạo hạnh **theo phần công mình để lại**; ai bỏ mạng giữa chiến trường chịu thương tích nặng hơn thua PK thường.
  Ai tranh giải mà chết thì thiên hạ còn nhớ tên lâu hơn thường lệ.

### PK — thắng ăn cả, và có người làm chứng

`/pk <tên> [cược]` treo lời thách lên vách đá. Tiền cược **hai bên bị trừ ngay lúc treo** — không có chuyện thắng rồi bùng.
Đối phương bấm *Ứng chiến* (hoặc `/ungchien <mã>`) thì giao định: luật thường, hoặc *sinh tử* — thắng thua tính bằng mạng,
và cả hai đạo tâm cùng ghi một vệt dài vào thủ ký. Khước từ thì kẻ treo thách mất một ít đạo tâm; quá hẹn không ai thưa,
lời thách tự tan như chưa từng có.

`tuchan/he/chiendau.py` không in ra sát thương. Nó tính sức chiến ngầm (cảnh giới, tầng, pháp bảo,
công pháp tông môn, căn cốt, thương thế, đạo tâm), gieo từng hiệp, rồi chọn câu kể theo **độ chênh của hiệp đó**:

> *"Hàn Lập bước tới một bước. Chỉ một bước, mà khoảng cách mười trượng biến mất.*
> *Thạch Giáp Thú co mình lại chịu trọn một đòn rồi phản kích.*
> *Đòn cuối cùng đến khi Hàn Lập vừa hụt hơi — Hàn Lập bay ngược ra sau, đập vào một thân cây, và cây gãy."*

Kết trận có một câu bình, khác nhau tuỳ thắng đậm, thắng sát nút, thua đậm hay thua trong gang tấc.

---


---

## ⛩ Cửa động — Telegram Mini App

Mọi thứ bot làm được trong chat, Mini App làm được trong một cái động mở ngay trong
Telegram: bàn đá, đèn dầu, nút bấm, ảnh thuỷ mặc, thanh ảnh — cùng một cuốn sổ sinh tử,
không có bản sao luật chơi.

```bash
python run_tele.py --mini     # cửa động cổng 8080 + bot (nếu có TELEGRAM_TOKEN)
python3 -m tuchan.tele.mini   # riêng cửa động — khách lang thang không cần token
```

* **Trong Telegram**: người dùng bấm *Vào động* (nút menu bot hoặc nút trong `/menu`).
  `initData` do Telegram ký được kiểm bằng HMAC đúng chuẩn — vào cửa là nhập danh chính chủ,
  không cần mật khẩu, không có ai đội lốt ai.
* **Ngoài Telegram** (browser thường): vẫn chơi được như một chiếu diễn tập — uid âm,
  sổ riêng, không đụng tới người thật.
* `TELE_MINIAPP_URL` trong `.env` = đường https công khai của cửa động; khi có, bot tự
  dựng nút menu toàn cục và gửi lời mời tới từng người trong danh bạ.

## 🕰 Trực 24/7 bằng GitHub Actions (không máy chủ, không tiền)

`tools/workflows/live-mini.yml` là ca trực: mỗi phiên sống ~5 tiếng rưỡi, cuối phiên chốt sổ
lên nhánh `du-tru`, rồi `workflow_run` nối tiếp phiên sau — cổng gần như không khép.
Runner là nhà trọ nên phiên bản này **không có session trong RAM**: cookie tự ký HMAC,
mọi trạng thái nằm trong sqlite.

```bash
bash tools/bat-workflows.sh          # nạp workflow (token máy không được ghi .github/workflows)
```

Cần chuẩn bị, theo thứ tự quan trọng:

1. **Secret** `TELEGRAM_TOKEN` — thiếu thì cửa động vẫn mở cho khách, nhưng bot thật không đứng lớp.
2. **Cài `aiohttp`** — đã có trong `requirements.txt`.
3. *(tuỳ chọn)* `ACTIONS_PAT` (fine-grained, *Actions: write*) — nếu có, mỗi phiên tự đẩy nhịp
   `repository_dispatch` để phiên sau thức ngay trong giây; không có thì cron 14 phút một lần
   vẫn bắt nhịp (thụt lò tối đa ~15 phút mỗi phiên).
4. *(tuỳ chọn)* bật **Settings → Pages → Deploy from a branch → `gh-pages` / root** — khi repo
   *public*, link vĩnh viễn `https://<user>.github.io/<repo>/` sẽ tự lần ra cửa động mới nhất
   (mỗi phiên Actions ghi `mini.json`). Repo riêng tư thì bỏ qua: nút *Vào động* trong bot
   vẫn đưa thẳng vào cửa — đó mới là cửa chính.

Đường dẫn trycloudflare **đổi theo từng phiên** — đó là lý do tồn tại của hai thứ ở bước 3–4:
người trong bot bấm nút luôn đúng cửa, người ngoài cần Pages làm bảng chỉ đường.

Thử máy CI: Actions → *Sống · cửa động 24/7* → Run workflow → chọn `thu` — bốn phút,
tự điểm chỉ từ `/dangky` tới `/nhanvat` rồi tắt bếp.

---
## Tranh, tiếng và thanh ảnh

**Tranh vật phẩm.** Ngoài tranh cảnh giới / địa danh, các món pháp bảo và đan dược đáng kể đều có bức vẽ riêng
(`Huyết Hà Ma Đao`, `Ngự Phong Phi Kiếm`, `Huyền Thiết Trọng Kiếm`, `Cửu U Hồn Chung`, `Trảm Tiên Đài`,
`Độ Ách Đan`, `Huyết Bồ Đề`), món chưa có tranh riêng thì mượn bức chung của chủng loại
(Binh Khí Phổ cho khí giới, Đan Phổ cho đan dược). Tranh tự hiện khi: hỏi `vatpham`, `deo` nhận chủ pháp bảo,
`uongdan`, luyện chế thành công, mở `binhkhi` / `linhdan` / `kimdan`, và khi kết đan (bức `kim_dan.png`).

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
run.py                     điểm khởi động (Discord)
run_tele.py                điểm khởi động (Telegram)
tuchan/
  config.py                mọi con số cấu hình, kể cả hệ số co giãn thời gian
  canhgioi.py              10 cảnh giới / 61 bậc, chín khảo nghiệm, chín phẩm kim đan
  vanphong.py              đổi số thành chữ — trái tim của văn phong
  db.py                    SQLite: tu sĩ, túi đồ, sổ tay, nhật ký, việc môn, thiên biến
  giaodien.py              KetQua → embed Discord (tự cắt trang, đính tranh & phim)
  bot.py                   TuChanBot, nạp cog, đồng bộ slash
  data/                    thế giới tĩnh: vật phẩm, công thức, môn phái,
                           xuất thân, địa danh, địch thủ, sự kiện, việc môn
  he/                      luật chơi (chạy độc lập, không cần Discord)
    tuluyen · phieuluu · chiendau · luyenche · tongmon · thidau
    giaothuong · nhanvat · thienbien · thienco · ketqua
    kiepnan                chín cửa ải + chín trọng lôi kiếp
    dauboss                chiến trường yêu vương: huyết mạch, chia công, thương tích
    pk                     PK có cược: lời thách, ứng chiến, khước từ, sổ cái linh thạch
    thutich                bia mười bậc, Binh Khí Phổ, Đan Phổ
  cogs/                    tầng Discord, mỏng, chỉ gọi xuống he/
  tele/                    tầng Telegram, mỏng như thế
    long.py                lõi lệnh + điều hướng nút — không import aiogram, test được từ terminal
    hien_thi.py            KetQua → trang HTML Telegram (markdown → tg HTML, cắt trang, caption tranh)
    bot.py                 vỏ aiogram: slash command, gửi ảnh/video, callback nút, nút web_app
    mini.py                cửa động Mini App: verify initData, phiên HMAC, cùng lõi Long
    web/                   màng phủ Telegram cho cửa động (html/css/js, theo theme máy khách)
    vong.py                vòng tuần tra: boss thức tỉnh/lui về, thiên biến, lời thách quá hạn
tools/
  mophong.py               diễn tập Discord trong terminal
  web_dienrap.py           diễn tập Discord trong trình duyệt
  tele_thutap.py           diễn tập Telegram trong terminal (+ --tu-dong: tự diễn, tự kiểm tra sổ sách)
  tele_dienrap.py          diễn tập Telegram trong trình duyệt — bong bóng, nút bấm, tranh, thanh ảnh
  actions_giu.py           chốt sổ / kéo sổ giữa những phiên trực Actions
  workflows/live-mini.yml  ca trực 24/7: cloudflared + Pages + du-tru + workflow_run
  bat-workflows.sh         nạp ca trực lên .github/workflows (một lần)
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
