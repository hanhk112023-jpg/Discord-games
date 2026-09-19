/* Telegram Mini App: server-authoritative state, shared command engine, no mock rewards. */
(() => {
  "use strict";
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const tg = window.Telegram?.WebApp;
  const esc = (value) =>
    String(value ?? "").replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  const icon = (name) =>
    `<svg aria-hidden="true"><use href="#i-${name}"/></svg>`;
  const number = (n) => Number(n || 0).toLocaleString("vi-VN");
  const types = {
    phap_bao: "Pháp bảo",
    dan_duoc: "Đan dược",
    duoc_lieu: "Linh thảo",
    vat_lieu: "Vật liệu",
    ky_vat: "Kỳ vật",
    ngoc_gian: "Ngọc giản",
  };
  const pages = {
    home: ["Động phủ", "Gác lại hồng trần, trở về với con đường của ngươi."],
    boss: [
      "Ải yêu vương",
      "Vào bí cảnh, thử đạo tâm. Qua một ải, tiến một bước.",
    ],
    bag: ["Túi càn khôn", "Một tấc càn khôn, cất giữ vạn mối cơ duyên."],
    explore: [
      "Du ngoạn",
      "Ngoài kia là núi sông, cũng là con đường của ngươi.",
    ],
    craft: ["Đan phòng", "Luyện tinh hoa đất trời, dưỡng một thân tiên cốt."],
    sect: ["Tông môn", "Tầm sư học đạo, cùng đồng môn viết tiếp tiên đồ."],
    codex: [
      "Vạn vật phổ",
      "Linh thảo, tiên đan và những pháp bảo trong truyền thuyết.",
    ],
  };
  let state = null,
    page = "home",
    selectedStage = null,
    filter = "all",
    cursor = 0;
  let busy = false,
    ready = false,
    polling = false,
    previousState = "",
    toastTimer;
  let motion = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  try {
    if (localStorage.getItem("tien-motion") === "off") motion = false;
  } catch (_) {}

  function toast(text) {
    $("#bao").textContent = text;
    $("#bao").hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      $("#bao").hidden = true;
    }, 4200);
  }
  function haptic(type = "light") {
    try {
      tg?.HapticFeedback?.impactOccurred(type);
    } catch (_) {}
  }
  function effect(kind) {
    if (!motion) return;
    const el = $("#action-effect");
    el.className = "";
    void el.offsetWidth;
    el.className = kind;
    setTimeout(() => {
      el.className = "";
    }, 1200);
    haptic(kind === "battle" ? "heavy" : "light");
  }
  function setMotion() {
    document.body.classList.toggle("no-motion", !motion);
    $("#motion-toggle").textContent = `Hiệu ứng: ${motion ? "Bật" : "Tắt"}`;
    $("#motion-toggle").setAttribute("aria-pressed", String(motion));
  }
  setMotion();
  $("#motion-toggle").onclick = () => {
    motion = !motion;
    setMotion();
    try {
      localStorage.setItem("tien-motion", motion ? "on" : "off");
    } catch (_) {}
  };

  try {
    tg?.ready();
    tg?.expand();
    tg?.setHeaderColor("#0c1917");
    tg?.setBackgroundColor("#0c1917");
    tg?.BackButton?.onClick(() => {
      const dialog = $("dialog[open]");
      if (dialog) dialog.close();
      else if (page !== "home") navigate("home");
      else tg.close();
      updateBack();
    });
  } catch (_) {}
  function updateBack() {
    try {
      if (page !== "home" || $("dialog[open]")) tg?.BackButton?.show();
      else tg?.BackButton?.hide();
    } catch (_) {}
  }
  function openDialog(id) {
    $$("dialog[open]").forEach((d) => d.close());
    $(id).showModal();
    updateBack();
  }
  $$("dialog").forEach((d) => {
    d.addEventListener("close", updateBack);
    d.addEventListener("click", (e) => {
      if (e.target === d) {
        const r = d.getBoundingClientRect();
        if (
          e.clientX < r.left ||
          e.clientX > r.right ||
          e.clientY < r.top ||
          e.clientY > r.bottom
        )
          d.close();
      }
    });
  });
  function navigate(next) {
    if (!pages[next]) return;
    page = next;
    $$("dialog[open]").forEach((d) => d.close());
    $$(".page").forEach((el) => {
      el.hidden = el.id !== `page-${next}`;
    });
    $$("[data-page]").forEach((el) =>
      el.classList.toggle("active", el.dataset.page === next),
    );
    $("#page-title").textContent = pages[next][0];
    $("#page-crumb").textContent = pages[next][0];
    $("#page-subtitle").textContent = pages[next][1];
    if (next === "boss") renderBoss();
    if (next === "bag") renderBag();
    if (next === "codex") renderCodex();
    window.scrollTo({ top: 0, behavior: motion ? "smooth" : "instant" });
    updateBack();
    haptic();
  }
  async function api(path, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const res = await fetch(path, {
        method: body === undefined ? "GET" : "POST",
        credentials: "include",
        headers:
          body === undefined ? {} : { "Content-Type": "application/json" },
        body: body === undefined ? undefined : JSON.stringify(body),
        signal: controller.signal,
      });
      const text = await res.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (_) {
        data = { loi: text };
      }
      if (!res.ok) {
        const error = new Error(
          data.loi || "Không thể kết nối. Vui lòng thử lại.",
        );
        error.status = res.status;
        throw error;
      }
      return data;
    } catch (e) {
      if (e.name === "AbortError")
        throw new Error(
          "Kết nối chậm. Kiểm tra nhật ký trước khi thao tác lại.",
        );
      throw e;
    } finally {
      clearTimeout(timer);
    }
  }
  const command = (text) => api("/gui", { text });
  const callback = (nut, msg = null) => api("/nut", { nut, msg });
  async function syncState() {
    const next = await api("/api/state");
    const serialized = JSON.stringify(next);
    state = next;
    if (serialized !== previousState) {
      previousState = serialized;
      render();
    }
  }
  function safeStory(html) {
    const doc = new DOMParser().parseFromString(html, "text/html");
    function walk(node) {
      if (node.nodeType === Node.TEXT_NODE)
        return document.createTextNode(node.textContent);
      const allowed = ["B", "I", "CODE", "STRONG", "EM", "BR"];
      const el = document.createElement(
        allowed.includes(node.nodeName) ? node.nodeName.toLowerCase() : "span",
      );
      node.childNodes.forEach((child) => el.append(walk(child)));
      return el;
    }
    const fragment = document.createDocumentFragment();
    doc.body.childNodes.forEach((node) => fragment.append(walk(node)));
    return fragment;
  }
  function renderMessage(t) {
    const chat = $("#chat");
    $(".chat-empty", chat)?.remove();
    let bubble = $(`.bong[data-id="${Number(t.id)}"]`, chat);
    if (!bubble) {
      bubble = document.createElement("div");
      bubble.className = "bong";
      bubble.dataset.id = t.id;
      chat.append(bubble);
    }
    bubble.replaceChildren();
    if (t.anh) {
      const img = document.createElement("img");
      img.src = "/tranh/" + t.anh.split("/").map(encodeURIComponent).join("/");
      img.alt = "Minh họa câu chuyện";
      img.loading = "lazy";
      bubble.append(img);
    }
    if (t.phim) {
      const video = document.createElement("video");
      video.src = "/thanh/" + encodeURIComponent(t.phim);
      video.controls = true;
      video.playsInline = true;
      video.preload = "none";
      bubble.append(video);
    }
    bubble.append(safeStory(t.html || ""));
    $(`.hangnut[data-for="${Number(t.id)}"]`, chat)?.remove();
    if (t.nut?.length) {
      const group = document.createElement("div");
      group.className = "hangnut";
      group.dataset.for = t.id;
      t.nut.forEach((row) => {
        const line = document.createElement("div");
        line.className = "day";
        row.forEach((n) => {
          const button = document.createElement("button");
          button.textContent = n.l;
          button.onclick = async () => {
            if (String(n.u).startsWith("url:")) {
              const url = String(n.u).slice(4);
              if (!/^https:\/\//i.test(url)) return;
              if (tg?.initData) tg.openLink(url);
              else window.open(url, "_blank", "noopener,noreferrer");
              return;
            }
            await perform(() => callback(n.u, t.id), button);
          };
          line.append(button);
        });
        group.append(line);
      });
      bubble.after(group);
    }
    chat.scrollTop = chat.scrollHeight;
  }
  async function syncMessages() {
    const data = await api("/keo?since=" + cursor);
    // Server restarts clear transient messages, not persistent character data.
    if (data.moc < cursor) {
      cursor = 0;
      return;
    }
    (data.tin || []).forEach(renderMessage);
    cursor = data.moc || cursor;
    if (data.bao) toast(data.bao);
  }
  async function perform(fn, button, fx) {
    if (busy) return;
    if (!ready) {
      toast(
        "Chưa kết nối được với cửa động. Hãy tải lại trang hoặc mở lại từ Telegram.",
      );
      return;
    }
    busy = true;
    const disabled = button?.disabled;
    if (button) button.disabled = true;
    document.body.setAttribute("aria-busy", "true");
    try {
      await fn();
      if (fx) effect(fx);
      await syncMessages();
      await syncState();
      openDialog("#journal-dialog");
      $("#chat").scrollTop = $("#chat").scrollHeight;
    } catch (e) {
      toast(e.message);
    } finally {
      busy = false;
      if (button) button.disabled = disabled;
      document.body.removeAttribute("aria-busy");
    }
  }
  async function run(text, button, fx) {
    if (!ready) {
      toast("Đang chờ kết nối. Nếu chưa vào được, hãy tải lại trang.");
      return;
    }
    if (!state?.nhan_vat && !["/chidan", "/menu"].includes(text)) {
      register();
      return;
    }
    await perform(() => command(text), button, fx);
  }
  function register() {
    if (!ready || !state) {
      toast("Chưa kết nối được với cửa động. Hãy tải lại trang.");
      return;
    }
    $("#register-error").textContent = "";
    openDialog("#register-dialog");
  }
  function art(item, count = false) {
    return `<div class="item-art"><img src="${esc(item.anh)}" alt="${esc(item.ten)}" loading="lazy">${count ? `<span>×${number(item.so_luong)}</span>` : ""}</div>`;
  }
  function render() {
    const nv = state.nhan_vat;
    $("#wallet-value").textContent = nv ? number(nv.linh_thach) : "—";
    $("#character-name").textContent = nv
      ? nv.ten
      : "Đang chờ một mối tiên duyên";
    $("#realm-name").textContent = nv ? nv.canh_gioi : "Phàm nhân";
    $("#cultivator-sect").textContent = nv ? nv.mon_phai : "CHƯA NHẬP ĐẠO";
    $("#cultivation-value").textContent = nv
      ? `${number(nv.tu_vi)} / ${number(nv.tu_vi_can)}`
      : "Chưa nhập đạo";
    $("#cultivation-progress").style.width = nv
      ? `${Math.min(100, (nv.tu_vi / Math.max(1, nv.tu_vi_can)) * 100)}%`
      : "0%";
    $("#hero-action span").textContent = nv
      ? nv.da_chet
        ? "Chuyển thế, nhập đạo"
        : "Tọa thiền tu luyện"
      : "Bước vào tiên đồ";
    $("#practice-hint").textContent = state.cho.luyentap
      ? `Hồi phục · ${Math.ceil(state.cho.luyentap / 60)} phút`
      : "Hấp thu linh khí đất trời";
    document.title = nv
      ? `${nv.ten} · Tiên Đồ Vô Tận`
      : "Tiên Đồ Vô Tận · Telegram Mini App";
    const preview = state.tui.length
      ? state.tui.slice(0, 4)
      : ["thanh_cuong_kiem", "hoi_khi_dan", "hoang_tinh_thao", "long_van_ngoc"]
          .map((m) => state.vat_pham.find((v) => v.ma === m))
          .filter(Boolean);
    $("#bag-preview-grid").innerHTML = preview
      .map(
        (v) =>
          `<button class="mini-item" data-item="${esc(v.ma)}" data-owned="${state.tui.length ? "1" : "0"}">${art(v, !!state.tui.length)}<small>${esc(v.ten)}</small></button>`,
      )
      .join("");
    $("#bag-preview-note").textContent = state.tui.length
      ? `${state.tui.length} loại vật phẩm đang cất trong túi.`
      : "Minh họa từ Vạn vật phổ · Chưa sở hữu vật phẩm.";
    if (!$("#origin").options.length) {
      $("#origin").innerHTML = state.xuat_than
        .map((x) => `<option value="${esc(x.ma)}">${esc(x.ten)}</option>`)
        .join("");
      originChange();
    }
    if (page === "bag") renderBag();
    if (page === "boss") renderBoss();
    if (page === "codex") renderCodex();
  }
  function renderBag() {
    if (!state) return;
    const nv = state.nhan_vat;
    $("#vitals").innerHTML = nv
      ? `<div class="vital">Thân thể <b>${nv.than_the}/100</b></div><div class="vital">Đạo tâm <b>${nv.dao_tam}/100</b></div><div class="vital">Bí cảnh <b>${nv.da_qua}/7 ải</b></div>`
      : "";
    const items = state.tui.filter(
      (v) =>
        filter === "all" ||
        v.loai === filter ||
        (filter === "other" &&
          !["phap_bao", "dan_duoc", "duoc_lieu"].includes(v.loai)),
    );
    $("#inventory").innerHTML = items.length
      ? items.map((v) => itemCard(v, true)).join("")
      : `<div class="empty-state">${icon("bag")}<p>${nv ? "Chưa có vật phẩm trong ngăn này." : "Ngươi chưa có hành trang. Hãy khai danh nhập đạo."}</p><button class="btn outline" ${nv ? 'data-page="explore"' : "data-register"}>${nv ? "Du ngoạn tìm kỳ duyên" : "Khai danh nhập đạo"}</button></div>`;
  }
  function itemCard(v, owned = false) {
    return `<button class="item-card rarity-${v.pham}" data-item="${esc(v.ma)}" data-owned="${owned ? "1" : "0"}">${art(v, owned)}<strong>${esc(v.ten)}</strong><small>${esc(types[v.loai] || "Vật phẩm")} · ${v.pham} phẩm</small></button>`;
  }
  function renderCodex() {
    if (!state) return;
    const q = $("#item-search").value.trim().toLocaleLowerCase("vi");
    const matches = state.vat_pham.filter((v) =>
      v.ten.toLocaleLowerCase("vi").includes(q),
    );
    $("#codex").innerHTML = matches.length
      ? matches.map((v) => itemCard(v)).join("")
      : '<div class="empty-state"><p>Chưa tìm thấy vật phẩm mang tên này.</p></div>';
  }
  function itemDetail(ma, owned) {
    const v = (owned ? state.tui : state.vat_pham).find((v) => v.ma === ma);
    if (!v) return;
    const equipped = owned && state.nhan_vat?.phap_bao === ma;
    $("#item-dialog").innerHTML =
      `<button class="dialog-close icon-btn" data-close aria-label="Đóng">${icon("close")}</button><img class="item-detail-image" src="${esc(v.anh)}" alt="${esc(v.ten)}"><span class="eyebrow">${esc(types[v.loai])} · ${v.pham} PHẨM</span><h2>${esc(v.ten)}</h2><p class="item-description">${esc(v.mo_ta)}</p><p class="muted">${owned ? `Đang có: ${number(v.so_luong)}${equipped ? " · Đang trang bị" : ""}` : "Vạn vật phổ · Đây là thông tin tham khảo, không phải vật phẩm đang sở hữu."}</p><div class="item-detail-actions">${owned && v.loai === "dan_duoc" ? `<button class="btn gold" data-callback="bd:uong:${esc(ma)}">Dùng một viên</button>` : ""}${owned && v.loai === "phap_bao" ? `<button class="btn gold" data-callback="bd:deo:${esc(ma)}" ${equipped ? "disabled" : ""}>${equipped ? "Đang trang bị" : "Trang bị pháp bảo"}</button>` : ""}${owned && v.gia > 1 ? `<button class="btn outline" data-callback="bd:ban:${esc(ma)}">Bán một món</button>` : ""}</div>`;
    openDialog("#item-dialog");
  }
  function renderBoss() {
    if (!state) return;
    if (!selectedStage)
      selectedStage =
        state.ai.find((a) => a.trang_thai === "mo")?.ma || state.ai[0].ma;
    const labels = {
      mo: "Sẵn sàng thử sức",
      khoa: "Chưa mở",
      da_qua: "Đã vượt ải",
    };
    $("#stage-list").innerHTML = state.ai
      .map(
        (a) =>
          `<button class="stage-card ${a.ma === selectedStage ? "selected" : ""} ${a.trang_thai === "khoa" ? "locked" : ""}" data-stage="${a.ma}" aria-pressed="${a.ma === selectedStage}"><img src="${a.anh}" alt=""><span><small>ẢI ${String(a.so).padStart(2, "0")}</small><strong>${esc(a.ten)}</strong><p>${labels[a.trang_thai]}</p></span>${icon(a.trang_thai === "da_qua" ? "check" : a.trang_thai === "khoa" ? "lock" : "arrow")}</button>`,
      )
      .join("");
    const a = state.ai.find((a) => a.ma === selectedStage);
    const cooldown = state.cho.bicanh;
    const disabled =
      a.trang_thai !== "mo" || cooldown > 0 || state.nhan_vat?.da_chet;
    const caption =
      a.trang_thai === "da_qua"
        ? "Đã nhận chiến lợi phẩm"
        : a.trang_thai === "khoa"
          ? "Cửa ải chưa mở"
          : cooldown
            ? `Hồi kiếm khí · ${cooldown}s`
            : "Khiêu chiến yêu vương";
    $("#stage-detail").innerHTML =
      `<div class="stage-visual"><img src="${a.anh}" alt="${esc(a.ten)}"><span class="stage-label">BÍ CẢNH · ẢI ${String(a.so).padStart(2, "0")}</span></div><div class="stage-body"><span class="eyebrow">${esc(a.hieu)}</span><h2>${esc(a.ten)}</h2><p class="muted">Yêu cầu: ${esc(a.canh_gioi)}</p><p class="stage-description">${esc(a.mo_ta)}</p><div class="reward-mini"><img src="/tranh/vatpham/vat_lieu.svg" alt="Linh thạch"><span>${a.linh_thach} linh thạch</span><img src="${a.thuong.anh}" alt="${esc(a.thuong.ten)}"><span>${esc(a.thuong.ten)} ×1</span></div><button class="btn gold wide" data-command="/bicanh ${a.ma}" data-effect="battle" ${disabled ? "disabled" : ""}>${icon("sword")}${caption}</button><p class="stage-note">Bóng chiếu cá nhân · Qua ải trước để mở ải sau · Thất bại có thể thử lại</p></div>`;
  }
  function originChange() {
    const x = state?.xuat_than.find((x) => x.ma === $("#origin").value);
    $("#origin-description").textContent = x
      ? `${x.mo_ta}\n${x.linh_can}.`
      : "";
  }
  $("#origin").onchange = originChange;
  $("#item-search").oninput = renderCodex;
  $("#hero-action").onclick = (e) => {
    if (!state?.nhan_vat) register();
    else
      run(
        state.nhan_vat.da_chet ? "/chuyenthe" : "/luyentap",
        e.currentTarget,
        "cultivate",
      );
  };
  $("#profile-open").onclick = (e) =>
    state?.nhan_vat ? run("/nhanvat", e.currentTarget) : register();
  $("#journal-open").onclick = () => openDialog("#journal-dialog");
  $("#mobile-more").onclick = () => openDialog("#more-dialog");
  document.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b || b.disabled) return;
    if (b.hasAttribute("data-close")) b.closest("dialog")?.close();
    else if (b.dataset.page) navigate(b.dataset.page);
    else if (b.hasAttribute("data-register")) register();
    else if (b.dataset.command) run(b.dataset.command, b, b.dataset.effect);
    else if (b.dataset.callback) perform(() => callback(b.dataset.callback), b);
    else if (b.dataset.stage) {
      selectedStage = b.dataset.stage;
      renderBoss();
    } else if (b.dataset.item && state)
      itemDetail(b.dataset.item, b.dataset.owned === "1");
    else if (b.dataset.filter) {
      filter = b.dataset.filter;
      $$("#bag-filters button").forEach((el) =>
        el.classList.toggle("active", el === b),
      );
      renderBag();
    }
  });
  $("#register-form").onsubmit = async (e) => {
    e.preventDefault();
    if (busy) return;
    const form = new FormData(e.target);
    const name = String(form.get("name")).trim();
    if (name.length < 2) {
      $("#register-error").textContent = "Đạo hiệu cần ít nhất hai ký tự.";
      return;
    }
    busy = true;
    const b = $('button[type="submit"]', e.target);
    b.disabled = true;
    try {
      await command("/dangky " + name);
      await callback("xt:" + form.get("origin"));
      await callback("gt:" + form.get("gender"));
      await syncMessages();
      await syncState();
      if (!state.nhan_vat)
        throw new Error("Chưa hoàn tất nhập đạo. Hãy mở nhật ký để tiếp tục.");
      $("#register-dialog").close();
      toast(`Đạo hữu ${state.nhan_vat.ten}, tiên đồ đã mở.`);
      effect("cultivate");
    } catch (err) {
      $("#register-error").textContent = err.message;
    } finally {
      b.disabled = false;
      busy = false;
    }
  };
  $("#command-form").onsubmit = async (e) => {
    e.preventDefault();
    const value = $("#inp").value.trim();
    if (!value || busy) return;
    await perform(async () => {
      await command(value);
      $("#inp").value = "";
    }, $("#btn"));
  };
  async function poll() {
    if (ready && !busy && !polling && !document.hidden) {
      polling = true;
      try {
        await syncMessages();
        await syncState();
        $("#connection").innerHTML =
          `<i></i> ${tg?.initData ? "Telegram đã kết nối" : "Chế độ trải nghiệm"}`;
      } catch (_) {
        $("#connection").textContent = "Mất kết nối · đang thử lại";
      } finally {
        polling = false;
      }
    }
    setTimeout(poll, 4000);
  }
  async function start() {
    try {
      const data = await api("/vao", { initData: tg?.initData || "" });
      $("#connection").innerHTML =
        `<i></i> ${data.chinh_chu ? "Telegram đã kết nối" : "Chế độ trải nghiệm"}`;
      $("#register-mode").textContent = data.chinh_chu
        ? "Tiến độ được lưu theo tài khoản Telegram của ngươi."
        : "Đang trải nghiệm ngoài Telegram. Tiến độ gắn với cookie trình duyệt này.";
      await syncState();
      await syncMessages();
      ready = true;
      poll();
    } catch (e) {
      $("#connection").textContent = "Chưa kết nối";
      toast(e.message);
      if (!e.status || e.status >= 500) setTimeout(start, 5000);
    }
  }
  start();
})();
