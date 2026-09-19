"""Không cần token/mạng: python -m unittest discover -s tests -v."""
import asyncio
import hashlib
import hmac
import json
import random
import time
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from urllib.parse import urlencode

from aiohttp import CookieJar
from aiohttp.test_utils import TestClient, TestServer

from tuchan import config
from tuchan.db import Kho, TuSi
from tuchan.he import bicanh
from tuchan.tele import mini
from tuchan.tele.long import Long, TinDen, LoNhip, NGUON_TIN
from tuchan.tele.trang_thai import lay


class AuthTests(unittest.TestCase):
    def signed(self, age=0):
        parts = {'auth_date': str(int(time.time()) - age),
                 'user': json.dumps({'id': 123, 'first_name': 'Đạo hữu'})}
        key = hmac.new(b'WebAppData', b'test-token', hashlib.sha256).digest()
        message = '\n'.join(f'{k}={v}' for k, v in sorted(parts.items()))
        parts['hash'] = hmac.new(key, message.encode(), hashlib.sha256).hexdigest()
        return urlencode(parts)

    @patch.object(config, 'TELEGRAM_TOKEN', 'test-token')
    def test_telegram_signature_and_expiry(self):
        self.assertEqual(mini.kiem_dau_init(self.signed())['u'], 123)
        self.assertIsNone(mini.kiem_dau_init(self.signed() + 'x'))
        self.assertIsNone(mini.kiem_dau_init(self.signed(86410)))
        self.assertIsNone(mini.kiem_dau_init(self.signed(-100)))

    def test_session_signature_and_expiry(self):
        session = mini.lam_pien(-123)
        self.assertEqual(mini.doc_pien(session), -123)
        self.assertIsNone(mini.doc_pien(session + 'x'))
        self.assertIsNone(mini.doc_pien(None))
        with patch('tuchan.tele.mini.time.time', return_value=time.time() + mini.TUOI_PHIEN + 1):
            self.assertIsNone(mini.doc_pien(session))


class MiniTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kho = Kho(':memory:')
        await self.kho.mo()
        self.dong = mini.nhan(self.kho)
        self.dong.core = Long(self.kho, 1, self.dong.lo, rng=random.Random(7))
        self.client = TestClient(TestServer(mini.tao_app(self.dong)), cookie_jar=CookieJar(unsafe=True))
        await self.client.start_server()
        with patch.object(mini, 'CHO_KHACH', True):
            self.assertEqual((await self.client.post('/vao', json={})).status, 200)

    async def asyncTearDown(self):
        await self.client.close()
        await self.kho.dong()

    async def test_register_state_and_persistence(self):
        for path, body in [('/gui', {'text':'/dangky Tiểu Đạo'}),
                           ('/nut', {'nut':'xt:con_nha_vo'}), ('/nut', {'nut':'gt:nu'})]:
            self.assertEqual((await self.client.post(path, json=body)).status, 200)
        r = await self.client.get('/api/state')
        state = await r.json()
        self.assertEqual(state['nhan_vat']['ten'], 'Tiểu Đạo')
        self.assertEqual(state['tui'][0]['so_luong'], 1)
        self.assertEqual(len(state['ai']), 7)
        self.assertEqual(r.headers['Cache-Control'], 'no-store')
        with patch.object(mini, 'CHO_KHACH', True):
            await self.client.post('/vao', json={})
        again = await (await self.client.get('/api/state')).json()
        self.assertEqual(again['nhan_vat'], state['nhan_vat'])

    async def test_invalid_inputs_and_csrf(self):
        for path, payload in [('/vao', []), ('/vao', {'initData':123}),
                              ('/gui', {'text':{}}), ('/gui', {'text':'a'*501}),
                              ('/nut', {'nut':[], 'msg':'bad'})]:
            self.assertEqual((await self.client.post(path, json=payload)).status, 400)
        self.assertEqual((await self.client.get('/keo?since=abc')).status, 400)
        self.assertEqual((await self.client.post('/gui', data='{"text":"/menu"}')).status, 415)
        self.assertEqual((await self.client.post('/gui', json={'text':'/menu'},
                           headers={'Origin':'https://evil.example'})).status, 403)

    async def test_no_invalid_auth_guest_downgrade(self):
        self.assertEqual((await self.client.post('/vao', json={'initData':'fake'})).status, 401)
        with patch.object(mini, 'CHO_KHACH', False):
            self.assertEqual((await self.client.post('/vao', json={})).status, 401)

    async def test_sessions_are_required_and_guests_are_separate(self):
        old = next(iter(self.client.session.cookie_jar)).value
        self.client.session.cookie_jar.clear()
        self.assertEqual((await self.client.get('/api/state')).status, 401)
        self.assertEqual((await self.client.post('/gui', json={'text':'/menu'})).status, 401)
        with patch.object(mini, 'CHO_KHACH', True):
            await self.client.post('/vao', json={})
        new = next(iter(self.client.session.cookie_jar)).value
        self.assertNotEqual(mini.doc_pien(old), mini.doc_pien(new))

    async def test_all_assets_exist_and_serve(self):
        state = await lay(self.kho, -1)
        urls = {v['anh'] for v in state['vat_pham']} | {a['anh'] for a in state['ai']}
        urls.update({'/', '/mong.css', '/dong.js', '/tranh/dong_phu.jpg',
                     '/fonts/be-vietnam-pro-latin-400-normal.woff2'})
        for url in urls:
            r = await self.client.get(url)
            self.assertEqual(r.status, 200, url)
            await r.read()

    async def test_reply_transport_and_primary_mini_button(self):
        tele = mini.LoMini()
        tele.MA_NGUON = "telegram"
        lo = LoNhip(tele, self.dong.lo)
        core = Long(self.kho, 1, lo)
        await core.xu_ly(TinDen(123, 123, "Đạo hữu", "lenh", "/menu", nguon="mini"))
        self.assertTrue(self.dong.lo.chat[123])
        self.assertFalse(tele.chat)
        self.assertEqual(NGUON_TIN.get(), "")
        tele.MA_URL_NUT = True
        with patch.object(config, "TELE_MINIAPP_URL", "https://game.example"):
            await core.xu_ly(TinDen(123, 123, "Đạo hữu", "lenh", "/start", nguon="telegram"))
        buttons = [n for t in tele.chat[123] for row in t['nut'] for n in row]
        self.assertEqual(buttons[0]['u'], 'url:https://game.example')
        # Message IDs may coincide across transports; edits must never cross them.
        from tuchan.tele.hien_thi import Trang
        web_msg = self.dong.lo.chat[123][0]['id']
        original = tele.chat[123][0]['html']
        token = NGUON_TIN.set('mini')
        try:
            await lo.sua(123, web_msg, Trang(html='web only'))
        finally:
            NGUON_TIN.reset(token)
        self.assertEqual(tele.chat[123][0]['html'], original)
        self.assertEqual(self.dong.lo.chat[123][0]['html'], 'web only')

    async def test_message_edits_use_returned_id(self):
        from tuchan.tele.hien_thi import Trang
        msg = await self.dong.lo.gui(-1, Trang(html='before'))
        await self.dong.lo.sua(-1, msg, Trang(html='after'))
        self.assertEqual(self.dong.lo.chat[-1][0]['html'], 'after')
        self.assertNotEqual(self.dong.lo.cho_cua(-1), self.dong.lo.cho_cua(1))


class StageTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kho = Kho(':memory:')
        await self.kho.mo()
        await self.kho.tao_tu_si(TuSi(user_id=1, guild_id=1, ten='Kiểm thử', canh_gioi=1))
        self.lo = mini.LoMini()
        self.core = Long(self.kho, 1, self.lo, rng=random.Random(7))

    async def asyncTearDown(self):
        await self.kho.dong()

    async def test_locked_unknown_dead_and_injured(self):
        ts = await self.kho.lay_tu_si(1)
        self.assertFalse((await bicanh.vuot_ai(self.kho, ts, 'missing')).thanh_cong)
        self.assertFalse((await bicanh.vuot_ai(self.kho, ts, bicanh.AI[1].ma)).thanh_cong)
        ts.da_chet = 1
        self.assertFalse((await bicanh.vuot_ai(self.kho, ts, bicanh.AI[0].ma)).thanh_cong)
        ts.da_chet = 0; ts.than_the = 10
        self.assertFalse((await bicanh.vuot_ai(self.kho, ts, bicanh.AI[0].ma)).thanh_cong)
        self.assertEqual(await self.kho.tui(1), {})

    async def test_concurrent_commands_grant_reward_once(self):
        def win(a, b, *_args, **_kw):
            return SimpleNamespace(thang=a, van=['Một kiếm phá ải.'])
        tin = TinDen(user_id=1, chat_id=1, ten='Kiểm thử', loai='lenh', data='/bicanh '+bicanh.AI[0].ma)
        with patch.object(bicanh, 'giao_dau', side_effect=win):
            await asyncio.gather(self.core.xu_ly(tin), self.core.xu_ly(tin))
        ts = await self.kho.lay_tu_si(1)
        self.assertEqual(bicanh.tien_do(ts), 1)
        self.assertEqual(ts.linh_thach, 50)
        self.assertEqual(await self.kho.dem_vat(1,bicanh.THUONG[0]), 1)
        # Reloading the engine reads progress from SQLite, not a Python session.
        self.assertEqual((await lay(self.kho,1))['ai'][0]['trang_thai'], 'da_qua')
        self.assertGreater(await self.kho.con_cho(1,'bicanh'),0)
        self.assertFalse((await bicanh.vuot_ai(self.kho,ts,bicanh.AI[1].ma)).thanh_cong)

    async def test_failure_cooldown_and_realm_gate(self):
        ts = await self.kho.lay_tu_si(1)
        def lose(a,b,*args,**kw):
            return SimpleNamespace(thang=b, van=['Thua trận.'], ton_thuong_ke_thua=15)
        with patch.object(bicanh,'giao_dau', side_effect=lose):
            self.assertFalse((await bicanh.vuot_ai(self.kho,ts,bicanh.AI[0].ma)).thanh_cong)
        ts = await self.kho.lay_tu_si(1)
        self.assertEqual(ts.than_the,85)
        self.assertEqual(bicanh.tien_do(ts),0)
        self.assertEqual(ts.linh_thach,0)
        self.assertEqual(await self.kho.tui(1),{})
        self.assertGreater(await self.kho.con_cho(1,'bicanh'),0)
        ts.ghi_chu='{"bi_canh":1}';ts.canh_gioi=0
        self.assertFalse((await bicanh.vuot_ai(self.kho,ts,bicanh.AI[1].ma)).thanh_cong)

    async def test_complete_seven_stages_and_final_replay(self):
        ts = await self.kho.lay_tu_si(1)
        ts.canh_gioi = 9
        await self.kho.luu(ts)
        def win(a, b, *_args, **_kw):
            return SimpleNamespace(thang=a, van=['Một kiếm phá ải.'])
        with patch.object(bicanh, 'giao_dau', side_effect=win):
            for index, boss in enumerate(bicanh.AI):
                await self.kho.dat_cho(1, 'bicanh', 0)
                ts = await self.kho.lay_tu_si(1)
                kq = await bicanh.vuot_ai(self.kho, ts, boss.ma)
                self.assertTrue(kq.thanh_cong)
                self.assertEqual(bicanh.tien_do(await self.kho.lay_tu_si(1)), index + 1)
        ts = await self.kho.lay_tu_si(1)
        self.assertEqual(ts.linh_thach, 1400)
        self.assertEqual(len(await self.kho.tui(1)), 7)
        self.assertTrue(all(a['trang_thai'] == 'da_qua' for a in (await lay(self.kho, 1))['ai']))
        self.assertFalse((await bicanh.vuot_ai(self.kho, ts, bicanh.AI[-1].ma)).thanh_cong)

    async def test_reward_transaction_rollback(self):
        ts = await self.kho.lay_tu_si(1)
        # Force an SQLite failure after the progress update and before the reward.
        await self.kho.conn.execute("CREATE TRIGGER reject_reward BEFORE INSERT ON tui_do BEGIN SELECT RAISE(ABORT, 'test'); END")
        await self.kho.conn.commit()
        ts.ghi_chu='{"bi_canh":1}';ts.linh_thach=50
        with self.assertRaises(Exception):
            await self.kho.luu_bi_canh(ts,'hoi_khi_dan',60,'test')
        persisted = await self.kho.lay_tu_si(1)
        self.assertEqual(bicanh.tien_do(persisted),0)
        self.assertEqual(persisted.linh_thach,0)
        self.assertEqual(await self.kho.tui(1),{})
        self.assertEqual(await self.kho.con_cho(1,'bicanh'),0)


if __name__ == '__main__':
    unittest.main()
