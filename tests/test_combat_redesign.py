"""Unit tests for redesigned combat, cultivation, equipment, tower, and mini-app actions."""
import asyncio
import json
import random
import unittest
from pathlib import Path
from unittest.mock import patch

from aiohttp import CookieJar
from aiohttp.test_utils import TestClient, TestServer

from tuchan.db import Kho, TuSi
from tuchan.data.vatpham import DANH_MUC
from tuchan.he.chiendau import BenThamChien, giao_dau
from tuchan.he.sanquai import KHU_VUC, san_quai, vuot_thap
from tuchan.he.tuluyen import luyen_tap, dot_pha
from tuchan.tele import mini
from tuchan.tele.long import Long, TinDen


class CombatRedesignTests(unittest.TestCase):
    def test_stats_calculation(self):
        ts = TuSi(user_id=1, ten="Lâm Phong", canh_gioi=1, tang=3, can_cot=1.2, tu_chat=1.1)
        stats = ts.tinh_chi_so()
        self.assertGreater(stats["hp_max"], 100)
        self.assertGreater(stats["mp_max"], 50)
        self.assertGreater(stats["cong"], 10)
        self.assertGreater(stats["thu"], 5)
        self.assertGreater(stats["luc_chien"], 100)
        self.assertGreater(stats["tu_vi_sec"], 0)

    def test_equipment_and_enhancement_stats(self):
        ts = TuSi(user_id=1, ten="Lâm Phong", canh_gioi=1, tang=1)
        base_stats = ts.tinh_chi_so()

        # Equip weapon
        ts.dat_trang_bi("vu_khi", "thanh_cuong_kiem")
        self.assertEqual(ts.lay_trang_bi()["vu_khi"], "thanh_cuong_kiem")
        stats_equipped = ts.tinh_chi_so()
        self.assertGreater(stats_equipped["cong"], base_stats["cong"])
        self.assertGreater(stats_equipped["luc_chien"], base_stats["luc_chien"])

        # Enhance weapon to +3
        ts.dat_cuong_hoa("thanh_cuong_kiem", 3)
        self.assertEqual(ts.lay_cuong_hoa()["thanh_cuong_kiem"], 3)
        stats_enhanced = ts.tinh_chi_so()
        self.assertGreater(stats_enhanced["cong"], stats_equipped["cong"])
        self.assertGreater(stats_enhanced["luc_chien"], stats_equipped["luc_chien"])

        # Unequip weapon
        ts.thao_trang_bi("vu_khi")
        self.assertNotIn("vu_khi", ts.lay_trang_bi())
        stats_unequipped = ts.tinh_chi_so()
        self.assertEqual(stats_unequipped["cong"], base_stats["cong"])

    def test_numeric_turn_combat(self):
        rng = random.Random(42)
        p1 = BenThamChien(
            ten="Người chơi",
            canh_gioi=1,
            tang=1,
            hp=1000,
            hp_max=1000,
            mp=200,
            mp_max=200,
            cong=120,
            thu=40,
            bao_kich=25,
            toc_do=105,
        )
        p2 = BenThamChien(
            ten="Yêu Lang",
            canh_gioi=1,
            tang=1,
            hp=600,
            hp_max=600,
            mp=100,
            mp_max=100,
            cong=80,
            thu=30,
            bao_kich=10,
            toc_do=90,
        )
        tran_dau = giao_dau(p1, p2, rng=rng)
        self.assertTrue(tran_dau.thang == p1 or tran_dau.thang == p2)
        self.assertGreater(len(tran_dau.van), 0)
        log_text = " ".join(tran_dau.van)
        self.assertTrue("sát thương" in log_text)
        self.assertTrue("HP:" in log_text)


class HuntingAndTowerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kho = Kho(":memory:")
        await self.kho.mo()
        self.ts = TuSi(user_id=1, guild_id=1, ten="Lâm Phong", canh_gioi=1, tang=5, linh_thach=100)
        await self.kho.tao_tu_si(self.ts)

    async def asyncTearDown(self):
        await self.kho.dong()

    async def test_hunting_zones_exist(self):
        self.assertGreaterEqual(len(KHU_VUC), 4)
        for ma, zone in KHU_VUC.items():
            self.assertTrue(ma)
            self.assertTrue(zone["ten"])
            self.assertTrue(zone["quai"])

    async def test_hunt_monster(self):
        ts = await self.kho.lay_tu_si(1)
        res = await san_quai(self.kho, ts, "thao_nguyen_lang", rng=random.Random(123))
        self.assertTrue(hasattr(res, "thanh_cong"))
        self.assertTrue(hasattr(res, "van"))
        self.assertGreater(len(res.van), 0)

    async def test_demon_tower_climbing(self):
        ts = await self.kho.lay_tu_si(1)
        self.assertEqual(ts.thap_tang(), 1)
        res = await vuot_thap(self.kho, ts, rng=random.Random(123))
        self.assertTrue(hasattr(res, "thanh_cong"))
        self.assertTrue(hasattr(res, "van"))
        if res.thanh_cong:
            updated = await self.kho.lay_tu_si(1)
            self.assertEqual(updated.thap_tang(), 2)


class CultivationTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kho = Kho(":memory:")
        await self.kho.mo()
        self.ts = TuSi(user_id=1, guild_id=1, ten="Lâm Phong", canh_gioi=1, tang=1, linh_thach=50, tu_vi=0)
        await self.kho.tao_tu_si(self.ts)

    async def asyncTearDown(self):
        await self.kho.dong()

    async def test_meditation_gains_tu_vi(self):
        ts = await self.kho.lay_tu_si(1)
        kq = await luyen_tap(self.kho, ts)
        self.assertTrue(kq.thanh_cong)
        self.assertGreater(ts.tu_vi, 0)
        self.assertTrue(any("Tu vi" in line for line in kq.van))

    async def test_breakthrough_progression(self):
        ts = await self.kho.lay_tu_si(1)
        ts.tu_vi = 5000
        await self.kho.luu(ts)
        kq = await dot_pha(self.kho, ts, rng=random.Random(42))
        self.assertTrue(kq.thanh_cong)
        updated = await self.kho.lay_tu_si(1)
        self.assertGreater(updated.tang, 1)


class ActionApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kho = Kho(":memory:")
        await self.kho.mo()
        self.dong = mini.nhan(self.kho)
        self.dong.core = Long(self.kho, 1, self.dong.lo, rng=random.Random(7))
        self.client = TestClient(TestServer(mini.tao_app(self.dong)), cookie_jar=CookieJar(unsafe=True))
        await self.client.start_server()
        with patch.object(mini, "CHO_KHACH", True):
            await self.client.post("/vao", json={})
        await self.client.post("/gui", json={"text": "/dangky Lâm Phong"})
        await self.client.post("/nut", json={"nut": "xt:con_nha_vo"})
        await self.client.post("/nut", json={"nut": "gt:nam"})

    async def asyncTearDown(self):
        await self.client.close()
        await self.kho.dong()

    async def test_action_tu_luyen(self):
        res = await self.client.post("/api/action/tu-luyen", json={})
        self.assertEqual(res.status, 200)
        data = await res.json()
        self.assertTrue(data.get("ok"))
        self.assertIn("van", data)

    async def test_action_san_quai(self):
        res = await self.client.post("/api/action/san-quai", json={"ma_quai": "thao_nguyen_lang"})
        self.assertEqual(res.status, 200)
        data = await res.json()
        self.assertTrue(data.get("ok"))
        self.assertIn("thang", data)
        self.assertIn("van", data)

    async def test_action_tran_thap(self):
        res = await self.client.post("/api/action/tran-thap", json={})
        self.assertEqual(res.status, 200)
        data = await res.json()
        self.assertTrue(data.get("ok"))
        self.assertIn("tang", data)

    async def test_action_equip_and_enhance(self):
        uid = mini.doc_pien(next(iter(self.client.session.cookie_jar)).value)
        await self.kho.them_vat(uid, "thanh_cuong_kiem", 1)
        ts = await self.kho.lay_tu_si(uid)
        ts.linh_thach += 500
        await self.kho.luu(ts)

        # Equip
        res = await self.client.post("/api/action/trang-bi", json={"ma": "thanh_cuong_kiem"})
        self.assertEqual(res.status, 200)
        data = await res.json()
        self.assertTrue(data.get("ok"))

        # Verify state reflects equipped item
        state = await (await self.client.get("/api/state")).json()
        tb = state["nhan_vat"]["trang_bi"]
        self.assertIn("vu_khi", tb)
        self.assertEqual(tb["vu_khi"]["ma"], "thanh_cuong_kiem")

        # Enhance
        res_enh = await self.client.post("/api/action/cuong-hoa", json={"ma": "thanh_cuong_kiem"})
        self.assertEqual(res_enh.status, 200)
        data_enh = await res_enh.json()
        self.assertTrue(data_enh.get("ok"))
        self.assertEqual(data_enh.get("cap_moi"), 1)

        # Unequip
        res_unequip = await self.client.post("/api/action/thao-trang-bi", json={"slot": "vu_khi"})
        self.assertEqual(res_unequip.status, 200)
        data_unequip = await res_unequip.json()
        self.assertTrue(data_unequip.get("ok"))


class TelegramCommandsTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.kho = Kho(":memory:")
        await self.kho.mo()
        self.lo = mini.LoMini()
        self.core = Long(self.kho, 1, self.lo, rng=random.Random(42))
        self.ts = TuSi(user_id=100, guild_id=1, ten="Lâm Phong", canh_gioi=1, tang=3, linh_thach=200)
        await self.kho.tao_tu_si(self.ts)

    async def asyncTearDown(self):
        await self.kho.dong()

    async def test_cmd_sanquai(self):
        tin = TinDen(user_id=100, chat_id=100, ten="Lâm Phong", loai="lenh", data="/sanquai")
        await self.core.xu_ly(tin)
        html = self.lo.chat[100][-1]["html"]
        self.assertIn("Sơn Dã Trảm Yêu", html)

    async def test_cmd_tranthap(self):
        tin = TinDen(user_id=100, chat_id=100, ten="Lâm Phong", loai="lenh", data="/tranthap")
        await self.core.xu_ly(tin)
        html = self.lo.chat[100][-1]["html"]
        self.assertIn("Trấn Yêu Tháp", html)

    async def test_cmd_nhanvat_sheet(self):
        tin = TinDen(user_id=100, chat_id=100, ten="Lâm Phong", loai="lenh", data="/nv")
        await self.core.xu_ly(tin)
        html = self.lo.chat[100][-1]["html"]
        self.assertIn("Hồ sơ tu sĩ", html)
        self.assertIn("LỰC CHIẾN", html)
        self.assertIn("Công Kích", html)
        self.assertIn("Phòng Ngự", html)


if __name__ == "__main__":
    unittest.main()
