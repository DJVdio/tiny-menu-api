# Tiny Menu API

智能点餐系统后端服务 - 让厨师和客户更好地互动的点餐平台

## 功能特性

- 🔐 用户认证（厨师/客户两种角色）
- 🤖 每日AI菜品推荐
- 🍽️ 客户选菜功能
- 👨‍🍳 厨师选择制作菜品
- 📖 完整菜谱管理
- 🔒 JWT身份验证
- 📊 RESTful API设计

## 技术栈

- **FastAPI** - 现代化的Python Web框架
- **MySQL** - 关系型数据库
- **SQLAlchemy** - ORM框架
- **Alembic** - 数据库迁移工具
- **JWT** - 身份认证
- **Pydantic** - 数据验证

## 项目结构

```
tiny-menu-api/
├── app/
│   ├── models/          # 数据库模型
│   ├── schemas/         # Pydantic模型
│   ├── routers/         # API路由
│   ├── utils/           # 工具函数
│   ├── config.py        # 配置文件
│   ├── database.py      # 数据库连接
│   └── main.py          # 主应用
├── alembic/             # 数据库迁移
├── scripts/             # 初始化脚本
├── requirements.txt     # 依赖包
├── .env.example         # 环境变量示例
└── run.py              # 启动脚本
```

## 快速开始

### 1. 安装依赖

```bash
cd tiny-menu-api
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 复制环境变量示例文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接
# DATABASE_URL=mysql+pymysql://用户名:密码@localhost:3306/tiny_menu
```

### 3. 创建数据库

在MySQL中创建数据库：

```sql
CREATE DATABASE tiny_menu CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 4. 初始化数据库

```bash
# 使用初始化脚本（会自动创建表并添加示例数据）
python scripts/init_db.py
```

或者使用Alembic进行迁移：

```bash
# 生成迁移文件
alembic revision --autogenerate -m "Initial migration"

# 执行迁移
alembic upgrade head
```

### 5. 启动服务

```bash
# 方式1：使用run.py
python run.py

# 方式2：直接使用uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

服务启动后访问：http://localhost:8000

## API文档

启动服务后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 示例账号

初始化数据库后，可以使用以下账号登录：

| 角色 | 用户名 | 密码 |
|------|--------|------|
| 厨师 | chef1 | password123 |
| 客户 | customer1 | password123 |
| 客户 | customer2 | password123 |

## 主要API端点

### 认证模块
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录

### 菜品管理
- `GET /api/dishes` - 获取所有菜品
- `GET /api/dishes/{id}` - 获取菜品详情（含菜谱）
- `POST /api/dishes` - 创建菜品（仅厨师）
- `GET /api/dishes/recommendations/today` - 获取今日推荐
- `POST /api/dishes/recommendations/generate` - 生成推荐（仅厨师）

### 客户选菜
- `POST /api/customer-selections` - 选择菜品
- `GET /api/customer-selections/my-selections` - 我的选择
- `GET /api/customer-selections/all` - 所有客户选择（仅厨师）
- `DELETE /api/customer-selections/{id}` - 取消选择

### 厨师选菜
- `POST /api/chef-selections` - 选择制作菜品
- `GET /api/chef-selections/my-selections` - 我的选择
- `DELETE /api/chef-selections/{id}` - 取消选择

## 业务流程

1. **用户注册登录**
   - 客户和厨师分别注册账号
   - 登录后获取JWT token

2. **每日推荐**
   - 系统每天AI推荐菜品给客户
   - 厨师可以手动触发推荐生成

3. **客户选菜**
   - 客户从推荐菜品中选择喜欢的菜
   - 可以选择多个菜品

4. **厨师选菜**
   - 厨师查看所有客户选择的菜品
   - 从中选择要制作的菜品
   - 可以查看完整的菜谱

## 数据库模型

### 用户表 (users)
- 用户名、邮箱、密码（加密）
- 角色（chef/customer）

### 菜品表 (dishes)
- 菜名、描述、菜谱、食材
- 烹饪时间、难度、分类

### 每日推荐表 (daily_recommendations)
- 日期、菜品关联

### 客户选择表 (customer_selections)
- 客户ID、菜品ID、日期

### 厨师选择表 (chef_selections)
- 厨师ID、客户选择ID、菜品ID、日期

## 开发说明

### 添加新的API路由

1. 在 `app/routers/` 创建新的路由文件
2. 在 `app/main.py` 中注册路由

### 数据库迁移

```bash
# 修改模型后生成迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 安全建议

1. 修改 `.env` 中的 `SECRET_KEY`
2. 生产环境使用强密码
3. 配置CORS只允许特定域名
4. 使用HTTPS
5. 定期更新依赖包

## 许可证

MIT License
