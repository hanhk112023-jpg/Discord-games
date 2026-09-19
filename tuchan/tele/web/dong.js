/* Động khô — phía người xem.
   Trong Telegram: gửi initData cho servidor ký tên nhập đạo, bật haptic, Back Button.
   Ngoài Telegram (diễn tập): đi cửa khách, mọi thứ vẫn chạy y hệt. */
(function () {
  'use strict';
  const tg = window.Telegram && window.Telegram.WebApp ? window.Telegram.WebApp : null;
  const chat = document.getElementById('chat');
  const inp = document.getElementById('inp');
  const btn = document.getElementById('btn');
  const bao = document.getElementById('bao');
  let moc = 0, gui_dang_bat = false;

  if (tg) {
    try { tg.ready(); tg.expand(); } catch (e) {}
    if (tg.setHeaderColor) { try { tg.setHeaderColor('#17212b'); tg.setBackgroundColor('#17212b'); } catch (e) {} }
    if (tg.BackButton) { try { tg.BackButton.show(); tg.BackButton.onClick(() => tg.close()); } catch (e) {} }
  }

  function rung(kind) { if (tg && tg.HapticFeedback) { try { tg.HapticFeedback.impactOccurred(kind || 'light'); } catch (e) {} } }


  function tao_bong(t) {
    const b = document.createElement('div');
    b.className = 'bong' + (t.me ? ' me' : '');
    b.dataset.id = t.id;
    b.innerHTML = media_cua(t) + (t.html || '');
    return b;
  }

  function tao_nut(t) {
    const k = document.createElement('div');
    k.className = 'hangnut'; k.dataset.nutof = t.id;
    (t.nut || []).forEach(row => {
      const d = document.createElement('div'); d.className = 'day';
      row.forEach(n => {
        const el = document.createElement('button');
        el.textContent = n.l;
        el.onclick = () => {
          rung('medium');
          if (String(n.u).startsWith('url:')) {
            const u = String(n.u).slice(4);
            if (tg && tg.openLink) { try { tg.openLink(u); return; } catch (e) {} }
            window.open(u, '_blank'); return;
          }
          fetch('/nut', { method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ msg: t.id, nut: n.u }) });
        };
        d.appendChild(el);
      });
      k.appendChild(d);
    });
    return k;
  }

  function ve(t) {
    const cu = chat.querySelector(`.bong[data-id="${t.id}"]`);
    if (cu) {
      cu.innerHTML = media_cua(t) + (t.html || '');
      const old = chat.querySelector(`.hangnut[data-nutof="${t.id}"]`);
      if (old) old.remove();
      if ((t.nut || []).length) cu.after(tao_nut(t));
      return;
    }
    const bong = tao_bong(t);
    chat.appendChild(bong);
    if ((t.nut || []).length) chat.appendChild(tao_nut(t));
    chat.scrollTop = chat.scrollHeight;
  }
  function media_cua(t) {
    let m = '';
    if (t.anh) m += `<img src="/tranh/${encodeURIComponent(t.anh)}" alt="" loading="lazy">`;
    if (t.phim) m += `<video src="/thanh/${encodeURIComponent(t.phim)}" controls preload="metadata" playsinline></video>`;
    return m;
  }

  async function gui() {
    const v = inp.value.trim();
    if (!v || gui_dang_bat) return;
    gui_dang_bat = true;
    try {
      await fetch('/gui', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ text: v }) });
      chat.appendChild(Object.assign(document.createElement('div'), { className: 'bong me', textContent: v }));
      chat.scrollTop = chat.scrollHeight;
    } finally { inp.value = ''; gui_dang_bat = false; }
  }

  btn.onclick = () => { rung('light'); gui(); };
  inp.addEventListener('keydown', e => { if (e.key === 'Enter') gui(); });

  async function keo() {
    try {
      const r = await fetch('/keo?since=' + moc, { credentials: 'include' });
      if (!r.ok) return;
      const d = await r.json();
      (d.tin || []).forEach(ve);
      if (d.moc) moc = d.moc;
      if (d.bao) {
        bao.hidden = false; bao.textContent = d.bao;
        if (tg && tg.HapticFeedback) { try { tg.HapticFeedback.notificationOccurred('success'); } catch (e) {} }
        setTimeout(() => { bao.hidden = true; }, 2600);
      }
      document.title = d.la ? `Tiên Đồ — ${d.la}` : 'Tiên Đồ Vô Tận';
    } catch (e) {}
  }

  async function vao_cua() {
    const init = tg && tg.initData ? tg.initData : '';
    try {
      const r = await fetch('/vao', { method: 'POST', credentials: 'include',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ initData: init }) });
      const d = await r.json();
      if (d.ok && !d.chinh_chu && !tg) {
        const g = document.createElement('div'); g.className = 'bong';
        g.innerHTML = '<i>Khách qua ngưỡng — ngươi đang xem cửa động ngoài Telegram, nên chưa có ai ký tên cho ngươi. '
          + 'Cứ gõ <code>/dangky</code> mà vào; khi mở từ bot, initData sẽ tự nhập danh chính chủ.</i>';
        chat.appendChild(g);
      }
    } catch (e) { setTimeout(vao_cua, 800); return; }
    keo();
    setInterval(keo, 1100);
  }

  vao_cua();
})();
