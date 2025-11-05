"""
初始化数据库并添加示例数据
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.dish import Dish
from app.utils.auth import get_password_hash


def init_db():
    """初始化数据库表"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


def add_sample_data():
    """添加示例数据"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        existing_users = db.query(User).count()
        if existing_users > 0:
            print("Database already has data, skipping sample data creation.")
            return

        print("Adding sample users...")

        # 创建示例用户
        users = [
            User(
                username="chef1",
                email="chef1@tinymenu.com",
                hashed_password=get_password_hash("password123"),
                role="chef",
                full_name="张大厨"
            ),
            User(
                username="customer1",
                email="customer1@tinymenu.com",
                hashed_password=get_password_hash("password123"),
                role="customer",
                full_name="李顾客"
            ),
            User(
                username="customer2",
                email="customer2@tinymenu.com",
                hashed_password=get_password_hash("password123"),
                role="customer",
                full_name="王顾客"
            ),
        ]

        for user in users:
            db.add(user)

        print("Adding sample dishes...")

        # 创建示例菜品
        dishes = [
            Dish(
                name="宫保鸡丁",
                description="经典川菜，鸡肉嫩滑，花生酥脆，酸甜微辣",
                recipe="""
1. 鸡胸肉切丁，用料酒、盐、淀粉腌制15分钟
2. 干辣椒切段，花椒、姜蒜切末
3. 调制酱汁：酱油、醋、糖、淀粉、水混合
4. 热油爆香花椒、干辣椒、姜蒜
5. 下鸡丁快速翻炒至变色
6. 加入花生米翻炒
7. 倒入调好的酱汁，翻炒均匀即可
                """,
                ingredients="鸡胸肉300g, 花生米100g, 干辣椒10个, 花椒1勺, 姜蒜适量, 酱油2勺, 醋1勺, 糖1勺",
                cooking_time=25,
                difficulty="medium",
                category="川菜"
            ),
            Dish(
                name="番茄炒蛋",
                description="家常菜，番茄酸甜，鸡蛋嫩滑",
                recipe="""
1. 鸡蛋打散，加少许盐
2. 番茄切块
3. 热油炒鸡蛋，炒至七成熟盛出
4. 另起锅，炒番茄至出汁
5. 加入炒好的鸡蛋
6. 加盐、糖调味，翻炒均匀即可
                """,
                ingredients="鸡蛋3个, 番茄2个, 盐适量, 糖少许, 油适量",
                cooking_time=10,
                difficulty="easy",
                category="家常菜"
            ),
            Dish(
                name="红烧肉",
                description="浓油赤酱，肥而不腻，入口即化",
                recipe="""
1. 五花肉切块，冷水下锅焯水
2. 锅中放少许油，加冰糖炒糖色
3. 下肉块翻炒上色
4. 加料酒、酱油、八角、桂皮
5. 加水没过肉，大火烧开转小火
6. 炖1.5小时至软烂
7. 大火收汁即可
                """,
                ingredients="五花肉500g, 冰糖30g, 酱油3勺, 料酒2勺, 八角2个, 桂皮1块, 姜片适量",
                cooking_time=120,
                difficulty="medium",
                category="家常菜"
            ),
            Dish(
                name="麻婆豆腐",
                description="经典川菜，麻辣鲜香，豆腐嫩滑",
                recipe="""
1. 豆腐切块，用盐水浸泡
2. 牛肉末加料酒腌制
3. 热油炒牛肉末至变色
4. 加豆瓣酱、花椒炒香
5. 加水烧开，下豆腐
6. 小火煮5分钟
7. 用水淀粉勾芡
8. 撒花椒粉、葱花即可
                """,
                ingredients="嫩豆腐1块, 牛肉末100g, 豆瓣酱2勺, 花椒1勺, 葱姜蒜适量",
                cooking_time=20,
                difficulty="medium",
                category="川菜"
            ),
            Dish(
                name="清蒸鲈鱼",
                description="粤菜经典，鱼肉鲜嫩，原汁原味",
                recipe="""
1. 鲈鱼清洗干净，两面划刀
2. 鱼身抹盐，放姜片腌制10分钟
3. 水烧开后，鱼上锅蒸8分钟
4. 蒸好后倒掉汤汁
5. 铺上葱丝、姜丝
6. 淋热油激发香味
7. 浇上蒸鱼豉油即可
                """,
                ingredients="鲈鱼1条, 姜适量, 葱适量, 蒸鱼豉油3勺, 油适量",
                cooking_time=15,
                difficulty="easy",
                category="粤菜"
            ),
            Dish(
                name="干煸四季豆",
                description="四季豆焦香，咸香微辣",
                recipe="""
1. 四季豆摘去两头，掰成段
2. 热油煸炒四季豆至表皮起皱
3. 盛出备用
4. 锅中留底油，炒肉末至变色
5. 加干辣椒、花椒爆香
6. 倒入四季豆翻炒
7. 加盐、酱油调味即可
                """,
                ingredients="四季豆300g, 猪肉末100g, 干辣椒10个, 花椒1勺, 姜蒜适量",
                cooking_time=20,
                difficulty="medium",
                category="川菜"
            ),
            Dish(
                name="糖醋里脊",
                description="酸甜可口，外酥里嫩",
                recipe="""
1. 里脊肉切条，加盐、料酒腌制
2. 裹上淀粉和蛋液
3. 油温七成热时炸至金黄
4. 调制糖醋汁：番茄酱、醋、糖、水淀粉
5. 锅中倒入糖醋汁，煮至浓稠
6. 放入炸好的肉条，快速翻炒均匀
7. 撒白芝麻即可
                """,
                ingredients="里脊肉300g, 淀粉适量, 鸡蛋1个, 番茄酱3勺, 醋2勺, 糖3勺",
                cooking_time=30,
                difficulty="medium",
                category="家常菜"
            ),
            Dish(
                name="酸辣土豆丝",
                description="酸辣爽口，开胃下饭",
                recipe="""
1. 土豆切细丝，泡水去淀粉
2. 干辣椒切段
3. 热油爆香花椒、干辣椒
4. 下土豆丝大火快炒
5. 加醋、盐翻炒
6. 出锅前加少许鸡精即可
                """,
                ingredients="土豆2个, 干辣椒5个, 花椒1勺, 醋2勺, 盐适量",
                cooking_time=10,
                difficulty="easy",
                category="家常菜"
            ),
        ]

        for dish in dishes:
            db.add(dish)

        db.commit()
        print(f"Successfully added {len(users)} users and {len(dishes)} dishes!")
        print("\n示例账号：")
        print("厨师账号: chef1 / password123")
        print("客户账号: customer1 / password123")
        print("客户账号: customer2 / password123")

    except Exception as e:
        print(f"Error adding sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing Tiny Menu Database...")
    init_db()
    add_sample_data()
    print("\nDatabase initialization completed!")
