/* Telegram Mini App: Lối chơi Tu Tiên Chiến Đấu, Kỹ Năng & Đan Phòng Trực Quan */
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
    phap_bao: "Trang bị",
    dan_duoc: "Đan dược",
    duoc_lieu: "Linh thảo",
    vat_lieu: "Vật liệu",
    ky_vat: "Kỳ vật",
    ngoc_gian: "Ngọc giản",
  };
  const pages = {
    home: ["Tu Luyện", "Ngưng tụ linh khí, rèn luyện thân thể, đột phá cảnh giới."],
    skills: ["Kỹ Năng", "Lĩnh ngộ bí thuật công pháp, thiết lập 4 ô kỹ năng xuất chiêu."],
    combat: ["Chiến Đấu", "Sơn dã săn quái cày đồ, vượt Trấn Yêu Tháp, đại chiến Yêu Vương."],
    bag: ["Túi & Trang Bị", "Cất giữ thần trang, đan dược và kỳ bảo tu chân."],
    craft: ["Đan Phòng", "Mở lò luyện đan, rèn đúc thần binh bằng nguyên liệu thu thập."],
    codex: ["Vạn Vật Phổ", "Bách khoa toàn thư về thần dược và pháp bảo cổ đại."],
  };

  let sessionToken = "";
  try {
    sessionToken = sessionStorage.getItem("tien_do_phien") || "";
  } catch (_) {}
  let state = null,
    page = "home",
    combatTab = "hunt",
    skillCat = "all",
    craftTab = "dan",
    selectedZone = "thanh_khe_son",
    selectedStage = null,
    filter = "all";
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
    const el = $("#bao");
    el.textContent = text;
    el.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      el.hidden = true;
    }, 4000);
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
    if (next === "boss") {
      next = "combat";
      combatTab = "boss";
    } else if (next === "explore") {
      next = "combat";
      combatTab = "hunt";
    }

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

    if (next === "skills") renderSkills();
    if (next === "combat") renderCombat();
    if (next === "bag") renderBag();
    if (next === "craft") renderCraft();
    if (next === "codex") renderCodex();

    window.scrollTo({ top: 0, behavior: motion ? "smooth" : "instant" });
    updateBack();
    haptic();
  }

  async function api(path, body) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 15000);
    try {
      const headers = {
        ...(sessionToken ? { "X-Phien": sessionToken } : {}),
        ...(tg?.initData ? { "X-Telegram-Init-Data": tg.initData } : {}),
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      };
      const res = await fetch(path, {
        method: body === undefined ? "GET" : "POST",
        credentials: "include",
        headers,
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
        throw new Error("Kết nối quá thời gian chờ.");
      throw e;
    } finally {
      clearTimeout(timer);
    }
  }

  async function syncState() {
    const next = await api("/api/state");
    const serialized = JSON.stringify(next);
    state = next;
    if (serialized !== previousState) {
      previousState = serialized;
      render();
    }
  }

  async function perform(fn, button, fx) {
    if (busy) return;
    if (!ready) {
      toast("Đang đồng bộ với máy chủ, hãy thử lại.");
      return;
    }
    busy = true;
    const disabled = button?.disabled;
    if (button) button.disabled = true;
    document.body.setAttribute("aria-busy", "true");
    try {
      const res = await fn();
      if (fx) effect(fx);
      await syncState();
      return res;
    } catch (e) {
      toast(e.message);
    } finally {
      busy = false;
      if (button) button.disabled = disabled;
      document.body.removeAttribute("aria-busy");
    }
  }

  function register() {
    if (!ready || !state) {
      toast("Đang tải dữ liệu, vui lòng đợi giây lát.");
      return;
    }
    $("#register-error").textContent = "";
    openDialog("#register-dialog");
  }

  function art(item, count = false) {
    return `<div class="item-art"><img src="${esc(item.anh)}" alt="${esc(item.ten)}" loading="lazy">${count ? `<span>×${number(item.so_luong)}</span>` : ""}</div>`;
  }

  /* ════════════════════ RENDER CHÍNH ════════════════════ */

  function render() {
    const nv = state?.nhan_vat;
    $("#wallet-value").textContent = nv ? number(nv.linh_thach) : "—";
    $("#cp-top").textContent = nv ? number(nv.luc_chien) : "—";
    $("#cp-display").textContent = nv ? number(nv.luc_chien) : "0";

    $("#character-name").textContent = nv ? nv.ten : "Chưa nhập đạo";
    $("#realm-name").textContent = nv ? nv.canh_gioi : "Phàm nhân";
    $("#cultivator-sect").textContent = nv ? nv.mon_phai : "CHƯA NHẬP ĐẠO";

    // Thanh Khí Huyết (HP) & Chân Khí (MP) & Tu Vi
    if (nv) {
      const hpPercent = Math.max(0, Math.min(100, (nv.hp / Math.max(1, nv.hp_max)) * 100));
      const mpPercent = Math.max(0, Math.min(100, (nv.mp / Math.max(1, nv.mp_max)) * 100));
      const tuviPercent = Math.max(0, Math.min(100, (nv.tu_vi / Math.max(1, nv.tu_vi_can)) * 100));

      $("#hp-text").textContent = `${number(nv.hp)} / ${number(nv.hp_max)}`;
      $("#hp-bar").style.width = `${hpPercent}%`;

      $("#mp-text").textContent = `${number(nv.mp)} / ${number(nv.mp_max)}`;
      $("#mp-bar").style.width = `${mpPercent}%`;

      const valEl = $("#cultivation-value");
      if (valEl) valEl.textContent = `${number(nv.tu_vi)} / ${number(nv.tu_vi_can)}`;
      const pctEl = $("#tuvi-percent");
      if (pctEl) pctEl.textContent = `${tuviPercent.toFixed(1)}%`;
      const progEl = $("#cultivation-progress");
      if (progEl) progEl.style.width = `${tuviPercent}%`;

      $("#tuvi-rate").textContent = number(nv.tu_vi_sec || 1);

      // Nút đột phá phát sáng nếu đủ tu vi
      const btnBt = $("#btn-breakthrough");
      if (nv.tu_vi >= nv.tu_vi_can) {
        btnBt.classList.add("ready-pulse");
        btnBt.innerHTML = `<svg><use href="#i-star" /></svg> ⚡ Đột Phá Ngay!`;
      } else {
        btnBt.classList.remove("ready-pulse");
        btnBt.innerHTML = `<svg><use href="#i-star" /></svg> Đột Phá Cảnh Giới`;
      }

      // Chỉ số chi tiết
      $("#stat-atk").textContent = number(nv.cong);
      $("#stat-def").textContent = number(nv.thu);
      $("#stat-crit").textContent = `${nv.bao_kich}%`;
      $("#stat-spd").textContent = number(nv.toc_do);
      $("#stat-cancot").textContent = nv.can_cot;
      $("#stat-tuchat").textContent = nv.tu_chat;
      $("#stat-daotam").textContent = nv.dao_tam;
      $("#stat-tower").textContent = `Tầng ${nv.thap_tang || 1}`;

      // 4 Ô trang bị
      renderEquipSlots(nv.trang_bi || {});

      // Trạng thái vết thương
      if (nv.dang_bi_thuong) {
        $("#status-tag").innerHTML = `<i></i> Cần điều tức (${nv.con_duong_thuong}s)`;
        $("#status-tag").style.borderColor = "#e63946";
      } else {
        $("#status-tag").innerHTML = `<i></i> Khí huyết sung mãn`;
        $("#status-tag").style.borderColor = "var(--green)";
      }
    }

    if (!$("#origin").options.length && state?.xuat_than) {
      $("#origin").innerHTML = state.xuat_than
        .map((x) => `<option value="${esc(x.ma)}">${esc(x.ten)}</option>`)
        .join("");
      originChange();
    }

    if (page === "skills") renderSkills();
    if (page === "combat") renderCombat();
    if (page === "bag") renderBag();
    if (page === "craft") renderCraft();
    if (page === "codex") renderCodex();
  }

  function renderEquipSlots(tb) {
    const slots = [
      { id: "slot-vu_khi", key: "vu_khi", title: "🗡️ Vũ Khí" },
      { id: "slot-giap", key: "giap", title: "🛡️ Chiến Giáp" },
      { id: "slot-phap_bao", key: "phap_bao", title: "🔮 Pháp Bảo" },
      { id: "slot-ngoc_boi", key: "ngoc_boi", title: "💍 Ngọc Bội" },
    ];

    slots.forEach((s) => {
      const el = $(`#${s.id}`);
      if (!el) return;
      const item = tb[s.key];
      if (item) {
        el.className = "equip-slot-card has-item";
        const cap = item.cap ? ` (+${item.cap})` : "";
        el.innerHTML = `
          <span class="equip-slot-title">${s.title}</span>
          <span class="equip-slot-name">${esc(item.ten)}${cap}</span>
          <span class="equip-slot-stats">+${item.cong} Công | +${item.thu} Thủ | +${item.hp} Máu</span>
          <div class="equip-slot-actions">
            <button class="enhance-btn" onclick="enhanceItem('${esc(item.ma)}')">Cường Hóa</button>
            <button onclick="unequipSlot('${s.key}')">Tháo</button>
          </div>
        `;
      } else {
        el.className = "equip-slot-card";
        el.innerHTML = `
          <span class="equip-slot-title">${s.title}</span>
          <span class="equip-slot-name muted">*(Trống)*</span>
          <span class="equip-slot-stats">Chưa trang bị</span>
          <div class="equip-slot-actions">
            <button onclick="navigate('bag')">Trang Bị</button>
          </div>
        `;
      }
    });
  }

  /* ════════════════════ HÀNH ĐỘNG TU LUYỆN ════════════════════ */

  async function doMeditate() {
    if (!state?.nhan_vat) return register();
    const btn = $("#btn-meditate");
    await perform(async () => {
      const res = await api("/api/action/tu-luyen", {});
      if (res.ok) {
        toast("Tọa thiền hấp thu linh khí thành công!");
        effect("cultivate");
      } else {
        toast(res.loi || "Không thể tọa thiền.");
      }
    }, btn);
  }

  $("#btn-meditate").onclick = doMeditate;
  $("#cultivation-orb-btn").onclick = doMeditate;

  async function doHeal() {
    if (!state?.nhan_vat) return register();
    const btn = $("#btn-heal");
    await perform(async () => {
      const res = await api("/api/action/duong-thuong", {});
      if (res.ok) {
        toast(res.thong_bao || "Khí huyết đã hồi phục 100%!");
        effect("cultivate");
      }
    }, btn);
  }
  $("#btn-heal").onclick = doHeal;

  async function doQuickPill() {
    if (!state?.nhan_vat) return register();
    const pill = state.tui.find((v) => v.loai === "dan_duoc" && v.hieu_qua?.tu_vi);
    if (!pill) {
      toast("Không có đan dược tăng tu vi trong túi càn khôn!");
      return;
    }
    const btn = $("#btn-quick-pill");
    await perform(async () => {
      const res = await api("/api/action/dung-dan", { ma: pill.ma });
      if (res.ok) {
        toast(res.thong_bao);
        effect("cultivate");
      }
    }, btn);
  }
  $("#btn-quick-pill").onclick = doQuickPill;

  /* ════════════════════ ĐỘT PHÁ CẢNH GIỚI ════════════════════ */

  $("#btn-breakthrough").onclick = () => {
    if (!state?.nhan_vat) return register();
    const nv = state.nhan_vat;
    if (nv.tu_vi < nv.tu_vi_can) {
      toast("Tu vi chưa đầy tràn! Hãy tiếp tục tọa thiền tụ khí hoặc săn quái cày tu vi.");
      return;
    }
    const pills = state.tui.filter((v) => v.loai === "dan_duoc" && v.hieu_qua?.dot_pha);
    const select = $("#bt-pill-select");
    select.innerHTML = '<option value="">(Không dùng đan hộ trợ)</option>' +
      pills.map((p) => `<option value="${esc(p.ma)}">${esc(p.ten)} (+${Math.round(p.hieu_qua.dot_pha * 100)}% thành công)</option>`).join("");

    $("#bt-target-realm").textContent = `${nv.canh_gioi} ➔ Cấp kế tiếp`;
    $("#bt-success-rate").textContent = pills.length ? "80% - 100%" : "80%";
    openDialog("#breakthrough-dialog");
  };

  $("#bt-confirm-btn").onclick = async (e) => {
    const dung_dan = $("#bt-pill-select").value || null;
    await perform(async () => {
      const res = await api("/api/action/dot-pha", { dung_dan });
      $("#breakthrough-dialog").close();
      if (res.thanh_cong) {
        toast("Chúc mừng! Đột phá cảnh giới thành công!");
        effect("cultivate");
      } else {
        toast("Xung quan thất bại, hao hụt một phần tu vi.");
      }
    }, e.currentTarget);
  };

  /* ════════════════════ TAB: KỸ NĂNG & CÔNG PHÁP ════════════════════ */

  function renderSkills() {
    if (!state) return;
    const allSkills = state.ky_nang || [];
    const equippedCodes = state.nhan_vat?.ky_nang_trang_bi || [];

    // Render 4 ô kỹ năng xuất chiêu
    const slotsGrid = $("#active-slots-grid");
    let slotsHtml = "";
    for (let i = 0; i < 4; i++) {
      const skillCode = equippedCodes[i];
      const kn = allSkills.find((k) => k.ma === skillCode);
      if (kn) {
        slotsHtml += `
          <div class="active-slot-card has-skill">
            <span class="active-slot-num">Ô ${i + 1}</span>
            <span class="active-slot-icon">${kn.icon}</span>
            <span class="active-slot-name">${esc(kn.ten)}</span>
            <span class="active-slot-mp">MP: ${kn.mp} · Lv.${kn.cap}</span>
            <button class="active-slot-unequip" onclick="thaoKyNang(${i})">Tháo ra</button>
          </div>
        `;
      } else {
        slotsHtml += `
          <div class="active-slot-card">
            <span class="active-slot-num">Ô ${i + 1}</span>
            <span class="active-slot-icon" style="opacity: 0.3;">➕</span>
            <span class="active-slot-name muted">(Trống)</span>
            <span class="active-slot-mp muted">—</span>
          </div>
        `;
      }
    }
    slotsGrid.innerHTML = slotsHtml;

    // Filter tabs
    $$(".skill-cat-btn").forEach((b) =>
      b.classList.toggle("active", b.dataset.skillCat === String(skillCat)),
    );

    const filtered = allSkills.filter(
      (k) => skillCat === "all" || String(k.canh_gioi) === String(skillCat),
    );

    const grid = $("#skill-grid");
    grid.innerHTML = filtered
      .map((k) => {
        const heClass = `he-${k.he.toLowerCase()}`;
        const isEquipped = k.da_trang_bi;
        let actionBtn = "";

        if (!k.da_hoc) {
          const disabled = !k.co_the_hoc ? "disabled" : "";
          actionBtn = `<button class="btn gold" onclick="hocKyNang('${k.ma}')" ${disabled}>Lĩnh Ngộ (${k.gia_hoc_tv} Tu vi, ${k.gia_hoc_lt} LT)</button>`;
        } else {
          const upDisabled = !k.co_the_up ? "disabled" : "";
          const equipBtn = isEquipped
            ? `<button class="btn outline" style="border-color:var(--gold); color:var(--gold);" disabled>✓ Đang Ra Chiêu</button>`
            : `<button class="btn green" onclick="trangBiKyNang('${k.ma}')">Trang Bị</button>`;
          actionBtn = `
            ${equipBtn}
            <button class="btn outline" onclick="nangCapKyNang('${k.ma}')" ${upDisabled}>Nâng Cấp (${k.gia_up_tv} TV, ${k.gia_up_lt} LT)</button>
          `;
        }

        return `
          <div class="skill-card ${isEquipped ? "equipped" : ""}">
            <div class="skill-card-head">
              <div class="skill-card-icon">${k.icon}</div>
              <div class="skill-card-meta">
                <div class="skill-card-name">${esc(k.ten)}</div>
                <div class="skill-badge-row">
                  <span class="element-badge ${heClass}">${esc(k.he)}</span>
                  <span class="skill-realm-tag" style="font-size:10px; color:var(--muted);">${esc(k.canh_gioi_ten)}</span>
                  ${k.da_hoc ? `<span class="skill-level-tag">Cấp ${k.cap}</span>` : ""}
                </div>
              </div>
            </div>

            <div class="skill-stats-box">
              <div class="skill-stat-item">
                <span>Tiêu hao Chân Khí (MP):</span>
                <strong>${k.mp} MP</strong>
              </div>
              ${k.he_so_sat_thuong > 0 ? `
              <div class="skill-stat-item">
                <span>Sát thương uy lực:</span>
                <strong style="color:#ef5350;">x${k.he_so_sat_thuong} Công + ${k.sat_thuong_co_dinh}</strong>
              </div>` : ""}
              ${k.he_so_hoi_phuc > 0 ? `
              <div class="skill-stat-item">
                <span>Hồi phục sinh mệnh:</span>
                <strong style="color:#81c784;">+${Math.round(k.he_so_hoi_phuc * 100)}% Khí Huyết</strong>
              </div>` : ""}
              ${k.he_so_la_chan > 0 ? `
              <div class="skill-stat-item">
                <span>Hộ thể kim quang:</span>
                <strong style="color:#ffd54f;">Giảm ${Math.round(k.he_so_la_chan * 100)}% sát thương</strong>
              </div>` : ""}
              ${k.tang_bao_kich > 0 ? `
              <div class="skill-stat-item">
                <span>Tỷ lệ bạo kích thêm:</span>
                <strong style="color:#ba68c8;">+${k.tang_bao_kich}% Bạo</strong>
              </div>` : ""}
              <div class="skill-stat-item">
                <span>Thời gian hồi chiêu:</span>
                <strong>${k.hoi_chieu} hiệp</strong>
              </div>
            </div>

            <p class="skill-desc">${esc(k.mo_ta)}</p>
            <div class="skill-actions-row">${actionBtn}</div>
          </div>
        `;
      })
      .join("");
  }

  $$(".skill-cat-btn").forEach((b) => {
    b.onclick = () => {
      skillCat = b.dataset.skillCat;
      renderSkills();
    };
  });

  window.hocKyNang = async (ma) => {
    await perform(async () => {
      const res = await api("/api/action/hoc-ky-nang", { ma });
      if (res.ok) {
        toast(res.thong_bao);
        effect("cultivate");
      }
    });
  };

  window.nangCapKyNang = async (ma) => {
    await perform(async () => {
      const res = await api("/api/action/nang-cap-ky-nang", { ma });
      if (res.ok) {
        toast(res.thong_bao);
        effect("cultivate");
      }
    });
  };

  window.trangBiKyNang = async (ma) => {
    const equipped = state.nhan_vat?.ky_nang_trang_bi || [];
    let freeSlot = equipped.length < 4 ? equipped.length : 0;
    await perform(async () => {
      const res = await api("/api/action/trang-bi-ky-nang", { ma, slot: freeSlot });
      if (res.ok) {
        toast(res.thong_bao);
        effect("cultivate");
      }
    });
  };

  window.thaoKyNang = async (slot) => {
    await perform(async () => {
      const res = await api("/api/action/thao-ky-nang", { slot });
      if (res.ok) {
        toast(res.thong_bao);
      }
    });
  };

  /* ════════════════════ TAB: ĐAN PHÒNG & LUYỆN KHÍ ════════════════════ */

  function renderCraft() {
    if (!state) return;
    const allRecipes = state.cong_thuc || [];

    $$(".craft-tab-btn").forEach((b) =>
      b.classList.toggle("active", b.dataset.craftTab === craftTab),
    );

    const recipes = allRecipes.filter((r) => r.loai === craftTab);
    const grid = $("#craft-grid");

    grid.innerHTML = recipes
      .map((r) => {
        const ingredientsHtml = r.nguyen_lieu
          .map(
            (nl) => `
            <div class="ingredient-item ${nl.du ? "enough" : "missing"}">
              <span>${esc(nl.ten)}:</span>
              <span class="ingredient-count">${nl.co} / ${nl.can} ${nl.du ? "✓" : "✗"}</span>
            </div>
          `,
          )
          .join("");

        const btnLabel =
          craftTab === "dan"
            ? (r.du_nguyen_lieu ? "🔥 Luyện 1 Viên" : "Thiếu Dược Liệu")
            : (r.du_nguyen_lieu ? "⚒️ Rèn Bảo Vật" : "Thiếu Khoáng Thạch");

        const actionFn = craftTab === "dan" ? `luyenDan('${r.ma}')` : `luyenKhi('${r.ma}')`;
        const disabled = !r.co_the_luyen ? "disabled" : "";

        return `
          <div class="recipe-card ${r.co_the_luyen ? "can-craft" : ""}">
            <div class="recipe-head">
              <div class="recipe-art"><img src="${esc(r.thanh_pham.anh)}" alt="${esc(r.thanh_pham.ten)}" loading="lazy"></div>
              <div class="recipe-meta">
                <div class="recipe-title">${esc(r.ten)}</div>
                <div class="recipe-target">Thành phẩm: <strong>${esc(r.thanh_pham.ten)}</strong></div>
                <div class="recipe-realm">Yêu cầu: Cảnh giới cấp ${r.canh_gioi_toi_thieu}</div>
              </div>
            </div>
            <div class="ingredient-list">${ingredientsHtml}</div>
            <button class="btn ${r.du_nguyen_lieu ? "gold" : "outline"} craft-btn" onclick="${actionFn}" ${disabled}>${btnLabel}</button>
          </div>
        `;
      })
      .join("");
  }

  $$(".craft-tab-btn").forEach((b) => {
    b.onclick = () => {
      craftTab = b.dataset.craftTab;
      renderCraft();
    };
  });

  window.luyenDan = async (ma) => {
    await perform(async () => {
      const res = await api("/api/action/luyen-dan", { ma });
      if (res.ok) {
        toast(res.thong_bao);
        effect("cultivate");
      }
    });
  };

  window.luyenKhi = async (ma) => {
    await perform(async () => {
      const res = await api("/api/action/luyen-khi", { ma });
      if (res.ok) {
        toast(res.thong_bao);
        effect("battle");
      }
    });
  };

  /* ════════════════════ CHIẾN ĐẤU & SĂN QUÁI ════════════════════ */

  function renderCombat() {
    if (!state) return;
    $$(".sub-tab-btn").forEach((b) =>
      b.classList.toggle("active", b.dataset.combatTab === combatTab),
    );
    $("#combat-view-hunt").hidden = combatTab !== "hunt";
    $("#combat-view-tower").hidden = combatTab !== "tower";
    $("#combat-view-boss").hidden = combatTab !== "boss";

    if (combatTab === "hunt") renderHuntingView();
    else if (combatTab === "tower") renderTowerView();
    else if (combatTab === "boss") renderBoss();
  }

  $$(".sub-tab-btn").forEach((b) => {
    b.onclick = () => {
      combatTab = b.dataset.combatTab;
      renderCombat();
    };
  });

  function renderHuntingView() {
    const zones = state.khu_vuc_san || [];
    if (!zones.length) return;

    $("#zone-selector").innerHTML = zones
      .map(
        (z) =>
          `<button class="zone-btn ${z.ma === selectedZone ? "active" : ""}" data-zone="${z.ma}">${esc(z.ten)} (${esc(z.canh_gioi_ten)})</button>`,
      )
      .join("");

    const currentZone = zones.find((z) => z.ma === selectedZone) || zones[0];
    const grid = $("#monster-grid");

    grid.innerHTML = currentZone.quai
      .map((q) => {
        return `
          <div class="monster-card">
            <div class="monster-head">
              <h4>${esc(q.ten)}</h4>
              <span class="monster-realm-tag">${esc(q.canh_gioi)}</span>
            </div>
            <p class="muted" style="font-size: 11px;">${esc(q.mo_ta)}</p>
            <div class="monster-stats-row">
              <span>❤️ Máu: <strong>${number(q.hp)}</strong></span>
              <span>🗡️ Công: <strong>${number(q.cong)}</strong></span>
              <span>🛡️ Thủ: <strong>${number(q.thu)}</strong></span>
            </div>
            <div class="monster-drops">
              🎁 Nhận: +${number(q.exp)} Tu vi, +${number(q.linh_thach)} Linh thạch<br>
              ${q.roi_do?.length ? `Rơi đồ: ${esc(q.roi_do.join(", "))}` : ""}
            </div>
            <div class="monster-card-actions">
              <button class="btn gold" onclick="startBattle('${esc(q.ma)}', '${esc(q.ten)}')">⚔️ Khiêu Chiến</button>
              <button class="btn outline" onclick="quickHunt('${esc(q.ma)}')">⚡ Săn Nhanh</button>
            </div>
          </div>
        `;
      })
      .join("");
  }

  function renderTowerView() {
    const t = state.tran_thap;
    if (!t) return;
    $("#tower-floor").textContent = t.tang;
    $("#tower-guardian-name").textContent = t.ten;
    $("#tower-guardian-hp").textContent = number(t.hp);
    $("#tower-guardian-atk").textContent = number(t.cong);
    $("#tower-guardian-def").textContent = number(t.thu);
    $("#tower-guardian-rewards").textContent = `+${number(t.exp)} Tu vi, +${number(t.linh_thach)} Linh thạch` + (t.roi_do?.length ? `, Bảo vật: ${t.roi_do.join(", ")}` : "");
  }

  $("#btn-fight-tower").onclick = async (e) => {
    if (!state?.nhan_vat) return register();
    await perform(async () => {
      const res = await api("/api/action/tran-thap", {});
      if (res.ok) {
        showBattleResults(res, "Trấn Yêu Tháp");
      }
    }, e.currentTarget);
  };

  window.quickHunt = async (ma_quai) => {
    if (!state?.nhan_vat) return register();
    await perform(async () => {
      const res = await api("/api/action/san-quai", { ma_quai });
      if (res.ok) {
        if (res.thang) {
          toast("🎉 Săn quái thành công! Thu hoạch tu vi và chiến lợi phẩm!");
          effect("battle");
        } else {
          toast("Thất bại trước yêu thú! Hãy tăng cường tu luyện.");
        }
      }
    });
  };

  /* ════════════════════ TRẬN CHIẾN TRỰC QUAN (BATTLE ARENA) ════════════════════ */

  window.startBattle = async (ma_quai, ten_quai) => {
    if (!state?.nhan_vat) return register();
    await perform(async () => {
      const res = await api("/api/action/san-quai", { ma_quai });
      if (res.ok) {
        showBattleResults(res, ten_quai);
      }
    });
  };

  function showBattleResults(res, ten_doi_thu) {
    const nv = state.nhan_vat;
    $("#battle-p-name").textContent = nv.ten;
    $("#battle-p-realm").textContent = nv.canh_gioi;
    $("#battle-p-hp-text").textContent = `${number(nv.hp)} / ${number(nv.hp_max)}`;
    $("#battle-p-hp-bar").style.width = "100%";
    $("#battle-p-mp-text").textContent = `${number(nv.mp)} / ${number(nv.mp_max)}`;
    $("#battle-p-mp-bar").style.width = "100%";

    $("#battle-e-name").textContent = ten_doi_thu;
    $("#battle-e-realm").textContent = res.tieu_de || "Yêu Thú";
    $("#battle-e-hp-text").textContent = res.thang ? "0 HP (Bại)" : "HP Còn";
    $("#battle-e-hp-bar").style.width = res.thang ? "0%" : "35%";

    // Render các nút kỹ năng trong bảng đấu
    const skillContainer = $("#battle-skills-actions");
    const allSkills = state.ky_nang || [];
    const equippedCodes = state.nhan_vat?.ky_nang_trang_bi || [];

    let skillButtonsHtml = `
      <button class="btn battle-skill-btn" onclick="fastForwardBattle()">
        <span class="battle-skill-btn-title">⚔️ Đánh Thường</span>
        <span class="battle-skill-btn-sub">0 MP</span>
      </button>
    `;

    equippedCodes.forEach((code) => {
      const kn = allSkills.find((k) => k.ma === code);
      if (kn) {
        skillButtonsHtml += `
          <button class="btn battle-skill-btn" onclick="fastForwardBattle()">
            <span class="battle-skill-btn-title">${kn.icon} ${esc(kn.ten)}</span>
            <span class="battle-skill-btn-sub">${kn.mp} MP · Lv.${kn.cap}</span>
          </button>
        `;
      }
    });

    skillButtonsHtml += `
      <button class="btn gold battle-skill-btn" onclick="fastForwardBattle()">
        <span class="battle-skill-btn-title">⚡ Đấu Tự Động</span>
        <span class="battle-skill-btn-sub">Tua nhanh</span>
      </button>
    `;

    skillContainer.innerHTML = skillButtonsHtml;

    const logBox = $("#battle-log-scroll");
    logBox.innerHTML = "";

    const lines = res.van || [];
    let delay = 0;
    lines.forEach((line, idx) => {
      const el = document.createElement("div");
      el.className = "battle-log-line";
      el.innerHTML = line;
      setTimeout(() => {
        logBox.appendChild(el);
        logBox.scrollTop = logBox.scrollHeight;
        if (idx === lines.length - 1) {
          showOverlay(res.thang);
        }
      }, delay);
      delay += motion ? 220 : 20;
    });

    $("#battle-result-overlay").hidden = true;
    openDialog("#battle-dialog");
  }

  window.fastForwardBattle = () => {
    $$(".battle-log-line").forEach((el) => (el.style.display = "block"));
    $("#battle-log-scroll").scrollTop = $("#battle-log-scroll").scrollHeight;
    $("#battle-result-overlay").hidden = false;
  };

  function showOverlay(thang) {
    const overlay = $("#battle-result-overlay");
    const title = $("#battle-result-title");
    title.className = `battle-result-title ${thang ? "win" : "lose"}`;
    title.textContent = thang ? "🏆 CHIẾN THẮNG!" : "💀 BẠI TRẬN!";
    $("#battle-loot-list").innerHTML = thang
      ? "<span>Chiến lợi phẩm và tu vi đã chuyển vào túi càn khôn.</span>"
      : "<span>Hãy điều tức trị thương, học thêm kỹ năng và cường hóa trang bị!</span>";
    overlay.hidden = false;
  }

  $("#battle-btn-close").onclick = () => {
    $("#battle-dialog").close();
  };

  /* ════════════════════ TRANG BỊ & TÚI CÀN KHÔN ════════════════════ */

  function renderBag() {
    if (!state) return;
    const nv = state.nhan_vat;
    $("#vitals").innerHTML = nv
      ? `<div class="vital">Khí huyết <b>${nv.hp}/${nv.hp_max}</b></div><div class="vital">Lực chiến <b>${number(nv.luc_chien)}</b></div><div class="vital">Trấn Tháp <b>Tầng ${nv.thap_tang || 1}</b></div>`
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
      : `<div class="empty-state">${icon("bag")}<p>${nv ? "Chưa có vật phẩm trong ngăn này." : "Ngươi chưa nhập đạo. Hãy khai danh nhập đạo."}</p><button class="btn gold" ${nv ? 'onclick="navigate(\'combat\')"' : "data-register"}>${nv ? "Săn quái kiếm trang bị" : "Khai danh nhập đạo"}</button></div>`;
  }

  function itemCard(v, owned = false) {
    const cap = v.cap ? ` (+${v.cap})` : "";
    return `<button class="item-card rarity-${v.pham}" data-item="${esc(v.ma)}" data-owned="${owned ? "1" : "0"}">${art(v, owned)}<strong>${esc(v.ten)}${cap}</strong><small>${esc(types[v.loai] || "Vật phẩm")} · ${v.pham} phẩm</small></button>`;
  }

  function itemDetail(ma, owned) {
    const v = (owned ? state.tui : state.vat_pham).find((v) => v.ma === ma);
    if (!v) return;

    const nv = state.nhan_vat;
    const tb = nv?.trang_bi || {};
    const isEquipped = owned && Object.values(tb).some((it) => it && it.ma === ma);
    const cap = v.cap ? ` (+${v.cap})` : "";

    let statsHtml = "";
    if (v.cong) statsHtml += `<span style="color:#e63946;">+${v.cong} Công</span> · `;
    if (v.thu) statsHtml += `<span style="color:#457b9d;">+${v.thu} Thủ</span> · `;
    if (v.hp) statsHtml += `<span style="color:#2a9d8f;">+${v.hp} Máu</span> · `;
    if (v.bao_kich) statsHtml += `<span style="color:#e9c46a;">+${v.bao_kich}% Bạo</span>`;

    $("#item-dialog").innerHTML = `
      <button class="dialog-close icon-btn" data-close aria-label="Đóng">${icon("close")}</button>
      <img class="item-detail-image" src="${esc(v.anh)}" alt="${esc(v.ten)}">
      <span class="eyebrow">${esc(types[v.loai] || "Vật phẩm")} · ${v.pham} PHẨM</span>
      <h2>${esc(v.ten)}${cap}</h2>
      ${statsHtml ? `<p style="font-weight:600; font-size:12px; margin: 4px 0 8px;">${statsHtml}</p>` : ""}
      <p class="item-description">${esc(v.mo_ta)}</p>
      <p class="muted">${owned ? `Số lượng: ${number(v.so_luong)}${isEquipped ? " · [Đang trang bị]" : ""}` : "Vạn vật phổ · Tra cứu thông tin tham khảo"}</p>
      <div class="item-detail-actions">
        ${owned && v.slot ? (isEquipped ? `<button class="btn outline" onclick="unequipSlot('${v.slot}')">Tháo Trang Bị</button>` : `<button class="btn gold" onclick="equipItem('${esc(ma)}')">Trang Bị Lên Người</button>`) : ""}
        ${owned && v.slot ? `<button class="btn green" onclick="enhanceItem('${esc(ma)}')">Cường Hóa (+1)</button>` : ""}
        ${owned && v.loai === "dan_duoc" ? `<button class="btn gold" onclick="usePill('${esc(ma)}')">Uống Đan</button>` : ""}
      </div>
    `;
    openDialog("#item-dialog");
  }

  window.equipItem = async (ma) => {
    await perform(async () => {
      const res = await api("/api/action/trang-bi", { ma });
      if (res.ok) {
        toast(res.thong_bao);
        $("#item-dialog").close();
      }
    });
  };

  window.unequipSlot = async (slot) => {
    await perform(async () => {
      const res = await api("/api/action/thao-trang-bi", { slot });
      if (res.ok) {
        toast(res.thong_bao);
        $("#item-dialog").close();
      }
    });
  };

  window.enhanceItem = async (ma) => {
    await perform(async () => {
      const res = await api("/api/action/cuong-hoa", { ma });
      if (res.ok) {
        toast(res.thong_bao);
        $("#item-dialog").close();
      }
    });
  };

  window.usePill = async (ma) => {
    await perform(async () => {
      const res = await api("/api/action/dung-dan", { ma });
      if (res.ok) {
        toast(res.thong_bao);
        $("#item-dialog").close();
      }
    });
  };

  /* ════════════════════ ẢI YÊU VƯƠNG ════════════════════ */

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
            : "Khiêu chiến Yêu Vương";
    $("#stage-detail").innerHTML =
      `<div class="stage-visual"><img src="${a.anh}" alt="${esc(a.ten)}"><span class="stage-label">ẢI YÊU VƯƠNG · ${String(a.so).padStart(2, "0")}</span></div><div class="stage-body"><span class="eyebrow">${esc(a.hieu)}</span><h2>${esc(a.ten)}</h2><p class="muted">Yêu cầu: ${esc(a.canh_gioi)}</p><p class="stage-description">${esc(a.mo_ta)}</p><div class="reward-mini"><img src="/tranh/vatpham/vat_lieu.svg" alt="Linh thạch"><span>${a.linh_thach} linh thạch</span><img src="${a.thuong.anh}" alt="${esc(a.thuong.ten)}"><span>${esc(a.thuong.ten)} ×1</span></div><button class="btn gold wide" onclick="fightBoss('${a.ma}')" ${disabled ? "disabled" : ""}>${icon("sword")}${caption}</button><p class="stage-note">Ải cá nhân thử sức · Hạ gục nhận thần trang quý</p></div>`;
  }

  window.fightBoss = async (ma) => {
    if (!state?.nhan_vat) return register();
    await perform(async () => {
      const res = await api("/api/action/san-quai", { ma_quai: ma });
      if (res.ok) {
        showBattleResults(res, "Ải Yêu Vương");
      }
    });
  };

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

  function originChange() {
    const x = state?.xuat_than.find((x) => x.ma === $("#origin").value);
    $("#origin-description").textContent = x
      ? `${x.mo_ta}\n${x.linh_can}.`
      : "";
  }
  $("#origin").onchange = originChange;
  $("#item-search").oninput = renderCodex;

  $("#profile-open").onclick = () => {
    if (!state?.nhan_vat) register();
    else navigate("home");
  };

  document.addEventListener("click", (e) => {
    const b = e.target.closest("button");
    if (!b || b.disabled) return;
    if (b.hasAttribute("data-close")) b.closest("dialog")?.close();
    else if (b.dataset.page) navigate(b.dataset.page);
    else if (b.dataset.zone) {
      selectedZone = b.dataset.zone;
      renderHuntingView();
    } else if (b.hasAttribute("data-register")) register();
    else if (b.dataset.stage) {
      selectedStage = b.dataset.stage;
      renderBoss();
    } else if (b.dataset.item && state) {
      itemDetail(b.dataset.item, b.dataset.owned === "1");
    } else if (b.dataset.filter) {
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
      await api("/gui", { text: "/dangky " + name });
      await api("/nut", { nut: "xt:" + form.get("origin") });
      await api("/nut", { nut: "gt:" + form.get("gender") });
      await syncState();
      if (!state.nhan_vat)
        throw new Error("Chưa hoàn tất nhập đạo. Hãy thử lại.");
      $("#register-dialog").close();
      toast(`Đạo hữu ${state.nhan_vat.ten}, tiên đồ chiến đấu đã mở!`);
      effect("cultivate");
    } catch (err) {
      $("#register-error").textContent = err.message;
    } finally {
      b.disabled = false;
      busy = false;
    }
  };

  async function poll() {
    if (ready && !busy && !polling && !document.hidden) {
      polling = true;
      try {
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
      if (data?.phien) {
        sessionToken = data.phien;
        try {
          sessionStorage.setItem("tien_do_phien", sessionToken);
        } catch (_) {}
      }
      $("#connection").innerHTML =
        `<i></i> ${data.chinh_chu ? "Telegram đã kết nối" : "Chế độ trải nghiệm"}`;
      $("#register-mode").textContent = data.chinh_chu
        ? "Tiến độ được lưu theo tài khoản Telegram của ngươi."
        : "Đang trải nghiệm ngoài Telegram. Tiến độ gắn với cookie trình duyệt.";
      await syncState();
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
