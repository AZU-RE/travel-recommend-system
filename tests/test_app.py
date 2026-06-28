import tempfile
import unittest
from pathlib import Path

from app import app, calculate_match_score, generate_recommend_reason
from init_db import init_database


class TravelSystemTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test.db"
        init_database(self.db_path)
        app.config.update(TESTING=True, DATABASE=str(self.db_path))
        self.client = app.test_client()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_home_and_admin_pages(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, 200)
        self.assertIn("乌镇", response.get_data(as_text=True))

    def test_score_weights_and_recommend_reason(self):
        preference = {
            "season": "春季", "style_type": "小桥流水",
            "budget_level": "中等预算", "play_days": "2-3天",
            "people_type": "情侣",
        }
        spot = {
            "name": "乌镇", "season": "春季,秋季", "style_type": "小桥流水,古韵文化",
            "budget_level": "中等预算", "play_days": "2-3天", "suitable_people": "情侣,家庭",
        }
        score, details = calculate_match_score(preference, spot)
        self.assertEqual(score, 100)
        self.assertEqual(details["season"], 30)
        self.assertIn("匹配度为 100%", generate_recommend_reason(preference, spot, score))

    def test_recommendation_is_sorted_and_saved(self):
        response = self.client.post(
            "/recommend",
            data={
                "season": "春季", "style_type": "小桥流水",
                "budget_level": "中等预算", "play_days": "2-3天",
                "people_type": "情侣",
            },
        )
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("乌镇", html)
        self.assertIn("100", html)
        self.assertLess(html.index("乌镇"), html.index("哈尔滨冰雪大世界"))

    def test_admin_crud(self):
        add = self.client.post(
            "/admin/add",
            data={
                "name": "测试景点", "province": "测试省", "city": "测试市",
                "season": "春季", "style_type": "山水自然",
                "budget_level": "低预算", "play_days": "1天",
                "suitable_people": "个人", "introduction": "测试简介",
                "route_suggestion": "入口→终点",
            },
            follow_redirects=True,
        )
        self.assertIn("测试景点", add.get_data(as_text=True))

    def register_and_login(self):
        return self.client.post(
            "/register",
            data={"username": "traveler", "password": "secret123", "confirm_password": "secret123"},
            follow_redirects=True,
        )

    def test_register_login_and_profile(self):
        response = self.register_and_login()
        self.assertEqual(response.status_code, 200)
        self.assertIn("个人中心", response.get_data(as_text=True))
        self.client.get("/logout")
        login = self.client.post(
            "/login",
            data={"username": "traveler", "password": "secret123"},
            follow_redirects=True,
        )
        self.assertIn("traveler", login.get_data(as_text=True))

    def test_history_favorite_and_comment(self):
        self.register_and_login()
        self.client.get("/detail/1")
        favorite = self.client.post("/favorite/1", follow_redirects=True)
        self.assertIn("已收藏", favorite.get_data(as_text=True))
        comment = self.client.post(
            "/detail/1/comment",
            data={"content": "春天的水乡氛围很适合慢慢游览。"},
            follow_redirects=True,
        )
        self.assertIn("春天的水乡氛围", comment.get_data(as_text=True))
        profile = self.client.get("/profile").get_data(as_text=True)
        self.assertIn("乌镇", profile)
        self.assertIn("春天的水乡氛围", profile)

    def test_profile_requires_login(self):
        response = self.client.get("/profile")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])


if __name__ == "__main__":
    unittest.main()
