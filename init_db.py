"""初始化旅游推荐系统 SQLite 数据库。"""

import sqlite3
import os
from pathlib import Path
from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "travel.db"

# name, province, city, season, style_type, budget_level, play_days,
# suitable_people, introduction, route_suggestion
SCENIC_SPOTS = [
    ("乌镇", "浙江", "嘉兴", "春季,秋季", "小桥流水,古韵文化,摄影人文", "中等预算,高预算", "1天,2-3天", "个人,情侣,家庭", "白墙黛瓦、石桥流水与摇橹船共同构成温柔的江南古镇画卷。", "西栅入口→草木本色染坊→昭明书院→白莲塔→西市河夜景"),
    ("苏州园林", "江苏", "苏州", "春季,秋季", "古韵文化,小桥流水,摄影人文", "低预算,中等预算", "1天,2-3天", "个人,情侣,家庭", "拙政园、留园等古典园林以移步换景展现东方造园艺术。", "拙政园→苏州博物馆→狮子林→平江路"),
    ("杭州西湖", "浙江", "杭州", "春季,秋季", "山水自然,古韵文化,城市烟火", "低预算,中等预算,高预算", "1天,2-3天", "个人,情侣,朋友,家庭", "湖山与城市相依，兼具自然景观、历史人文与休闲氛围。", "断桥→白堤→孤山→曲院风荷→苏堤日落"),
    ("扬州瘦西湖", "江苏", "扬州", "春季", "小桥流水,古韵文化,摄影人文", "中等预算", "1天,2-3天", "个人,情侣,家庭", "春日花木与亭桥水榭相映，是体验扬州慢生活的代表景点。", "南门→长堤春柳→徐园→五亭桥→二十四桥"),
    ("婺源", "江西", "上饶", "春季,秋季", "山水自然,摄影人文,古韵文化", "中等预算", "2-3天,4-5天", "个人,情侣,朋友", "油菜花田、徽派村落与秋日晒秋形成极具辨识度的乡村景观。", "篁岭→江岭→李坑→思溪延村"),
    ("青岛海岸", "山东", "青岛", "夏季,秋季", "海滨休闲,城市烟火,摄影人文", "低预算,中等预算,高预算", "2-3天,4-5天", "情侣,朋友,家庭", "红瓦绿树、碧海蓝天与鲜活的啤酒海鲜文化相融合。", "栈桥→大学路→八大关→第二海水浴场→五四广场"),
    ("厦门鼓浪屿", "福建", "厦门", "春季,夏季,秋季,冬季", "海滨休闲,摄影人文,城市烟火", "中等预算,高预算", "2-3天,4-5天", "个人,情侣,朋友,家庭", "无车小岛上分布着万国建筑、文艺街巷与安静海岸。", "三丘田码头→最美转角→菽庄花园→日光岩→龙头路"),
    ("桂林山水", "广西", "桂林", "春季,夏季,秋季", "山水自然,摄影人文", "中等预算,高预算", "2-3天,4-5天,一周以上", "个人,情侣,朋友,家庭", "喀斯特峰林倒映漓江，乘竹筏可感受山水画卷般的景色。", "桂林市区→杨堤→九马画山→兴坪古镇→阳朔"),
    ("承德避暑山庄", "河北", "承德", "夏季,秋季", "古韵文化,山水自然", "低预算,中等预算", "1天,2-3天", "个人,情侣,家庭", "皇家园林融汇江南水乡与北方山地景观，是经典避暑目的地。", "丽正门→宫殿区→湖泊区→平原区→山区"),
    ("长白山", "吉林", "延边", "夏季,秋季,冬季", "山水自然,雪山度假,摄影人文", "中等预算,高预算", "2-3天,4-5天", "情侣,朋友,家庭", "天池、瀑布、森林和冬季雪原共同构成长白山四季风景。", "北坡游客中心→天池→长白瀑布→绿渊潭"),
    ("北京香山", "北京", "北京", "秋季", "山水自然,摄影人文,古韵文化", "低预算,中等预算", "1天", "个人,情侣,朋友,家庭", "深秋红叶漫山，是北京代表性的季节摄影与登高目的地。", "东门→勤政殿→双清别墅→香炉峰"),
    ("西安古城", "陕西", "西安", "春季,秋季", "古韵文化,城市烟火,摄影人文", "低预算,中等预算,高预算", "2-3天,4-5天", "个人,情侣,朋友,家庭", "城墙、博物馆、历史街区与地方美食共同呈现古都魅力。", "陕西历史博物馆→大雁塔→古城墙→钟鼓楼→回民街"),
    ("南京栖霞山", "江苏", "南京", "秋季", "山水自然,摄影人文,古韵文化", "低预算,中等预算", "1天,2-3天", "个人,情侣,朋友,家庭", "秋季枫叶与古寺石刻相映，适合轻徒步和人文摄影。", "栖霞寺→舍利塔→千佛岩→始皇临江处→枫林湖"),
    ("九寨沟", "四川", "阿坝", "夏季,秋季", "山水自然,摄影人文", "中等预算,高预算", "2-3天,4-5天", "个人,情侣,朋友,家庭", "彩林、海子、瀑布和雪峰层次丰富，秋季色彩尤为绚丽。", "日则沟→则查洼沟→树正沟"),
    ("平遥古城", "山西", "晋中", "春季,秋季,冬季", "古韵文化,城市烟火,摄影人文", "低预算,中等预算", "1天,2-3天", "个人,情侣,朋友,家庭", "保存完整的明清古城格局适合体验晋商文化与民俗生活。", "古城墙→日升昌票号→县衙→明清街→双林寺"),
    ("哈尔滨冰雪大世界", "黑龙江", "哈尔滨", "冬季", "雪山度假,城市烟火,摄影人文", "中等预算,高预算", "2-3天,4-5天", "情侣,朋友,家庭", "大型冰雕在夜色中点亮，与中央大街共同构成北国冬日童话。", "索菲亚教堂→中央大街→松花江→冰雪大世界"),
    ("长白山雪景", "吉林", "延边", "冬季", "雪山度假,山水自然,摄影人文", "高预算", "2-3天,4-5天", "情侣,朋友,家庭", "雾凇、雪原、温泉与滑雪项目适合完整的冬季度假体验。", "万达度假区→滑雪场→雪地温泉→长白山北坡"),
    ("丽江古城", "云南", "丽江", "春季,秋季,冬季", "古韵文化,城市烟火,摄影人文", "中等预算,高预算", "2-3天,4-5天", "个人,情侣,朋友,家庭", "纳西民居、石板街巷与玉龙雪山背景形成独特高原古城风貌。", "大水车→四方街→木府→狮子山→束河古镇"),
    ("阿尔卑斯雪山", "瑞士", "因特拉肯", "冬季", "雪山度假,山水自然,摄影人文", "高预算", "4-5天,一周以上", "个人,情侣,朋友,家庭", "壮阔雪峰、山地列车和成熟滑雪设施代表经典欧洲冬季度假风格。", "因特拉肯→少女峰→格林德瓦→劳特布龙嫩"),
    ("中国雪乡", "黑龙江", "牡丹江", "冬季", "雪山度假,古韵文化,摄影人文", "中等预算,高预算", "2-3天,4-5天", "情侣,朋友,家庭", "厚重积雪覆盖木屋与街巷，呈现浓郁东北民俗和童话雪景。", "雪韵大街→观景栈道→梦幻家园→羊草山日出"),
]


def init_database(db_path=DB_PATH, reset=False):
    """创建数据表并写入初始景点数据。"""
    db_path = Path(db_path)
    if reset and db_path.exists():
        db_path.unlink()

    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS scenic_spot (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            province TEXT NOT NULL,
            city TEXT NOT NULL,
            season TEXT NOT NULL,
            style_type TEXT NOT NULL,
            budget_level TEXT NOT NULL,
            play_days TEXT NOT NULL,
            suitable_people TEXT NOT NULL,
            introduction TEXT NOT NULL,
            route_suggestion TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_preference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            season TEXT NOT NULL,
            style_type TEXT NOT NULL,
            budget_level TEXT NOT NULL,
            play_days TEXT NOT NULL,
            people_type TEXT NOT NULL,
            create_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS recommendation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            preference_id INTEGER,
            spot_id INTEGER NOT NULL,
            match_score INTEGER NOT NULL,
            recommend_reason TEXT NOT NULL,
            create_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (preference_id) REFERENCES user_preference(id) ON DELETE CASCADE,
            FOREIGN KEY (spot_id) REFERENCES scenic_spot(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS app_user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            create_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS favorite (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            spot_id INTEGER NOT NULL,
            create_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE (user_id, spot_id),
            FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE,
            FOREIGN KEY (spot_id) REFERENCES scenic_spot(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS browsing_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            spot_id INTEGER NOT NULL,
            view_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE,
            FOREIGN KEY (spot_id) REFERENCES scenic_spot(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS comment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            spot_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            create_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES app_user(id) ON DELETE CASCADE,
            FOREIGN KEY (spot_id) REFERENCES scenic_spot(id) ON DELETE CASCADE
        );
        """
    )

    # 增量迁移：旧数据库缺少 role 字段时只增加字段，不重建、不清空数据。
    user_columns = {
        row[1] for row in cursor.execute("PRAGMA table_info(app_user)").fetchall()
    }
    if "role" not in user_columns:
        cursor.execute(
            "ALTER TABLE app_user ADD COLUMN role TEXT NOT NULL DEFAULT 'user'"
        )

    # 课程设计默认管理员；密码仅保存哈希，可通过环境变量自定义。
    admin_username = os.getenv("TRAVEL_ADMIN_USERNAME", "admin")
    admin_password = os.getenv("TRAVEL_ADMIN_PASSWORD", "admin123")
    admin = cursor.execute(
        "SELECT id FROM app_user WHERE username = ?", (admin_username,)
    ).fetchone()
    if admin is None:
        cursor.execute(
            "INSERT INTO app_user (username, password_hash, role) VALUES (?, ?, 'admin')",
            (admin_username, generate_password_hash(admin_password)),
        )
    else:
        cursor.execute(
            "UPDATE app_user SET role = 'admin' WHERE username = ?",
            (admin_username,),
        )

    count = cursor.execute("SELECT COUNT(*) FROM scenic_spot").fetchone()[0]
    if count == 0:
        cursor.executemany(
            """
            INSERT INTO scenic_spot
            (name, province, city, season, style_type, budget_level,
             play_days, suitable_people, introduction, route_suggestion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            SCENIC_SPOTS,
        )
    connection.commit()
    connection.close()
    print(f"数据库初始化完成：{db_path}，景点数量：{len(SCENIC_SPOTS)}")


if __name__ == "__main__":
    init_database()
