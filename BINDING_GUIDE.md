# 厨师-顾客绑定功能使用指南

## 功能概述

此功能允许顾客申请绑定厨师，厨师同意后可以查看顾客每天点的菜。

## 业务规则

1. **用户名唯一性**：注册时 username 不能重复
2. **身份选择**：用户注册时必须选择身份（chef 或 customer）
3. **绑定申请**：顾客根据厨师的 username 申请绑定
4. **厨师审批**：厨师可以同意或拒绝绑定请求
5. **自我绑定限制**：用户不能绑定自己
6. **查看权限**：厨师只能查看已绑定顾客每天点的菜

## API 使用示例

### 1. 用户注册

**顾客注册：**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "password123",
    "role": "customer",
    "full_name": "Alice Wang"
  }'
```

**厨师注册：**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "chef_bob",
    "email": "bob@example.com",
    "password": "password123",
    "role": "chef",
    "full_name": "Bob Chen"
  }'
```

### 2. 用户登录

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "password123"
  }'
```

响应示例：
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "role": "customer",
    "full_name": "Alice Wang",
    "created_at": "2025-11-06T12:00:00"
  }
}
```

**重要**：将返回的 `access_token` 用于后续请求的认证。

### 3. 顾客申请绑定厨师

顾客需要知道厨师的 username 来申请绑定：

```bash
curl -X POST "http://localhost:8000/api/bindings/request" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {顾客的token}" \
  -d '{
    "chef_username": "chef_bob"
  }'
```

响应示例：
```json
{
  "id": 1,
  "chef_id": 2,
  "customer_id": 1,
  "chef_username": "chef_bob",
  "customer_username": "alice",
  "status": "pending",
  "created_at": "2025-11-06T12:30:00",
  "updated_at": null
}
```

**错误情况**：
- 厨师不存在：404 Not Found
- 试图绑定自己：400 Bad Request - "Cannot bind to yourself"
- 已存在绑定请求：400 Bad Request

### 4. 厨师查看待处理的绑定请求

```bash
curl -X GET "http://localhost:8000/api/bindings/pending" \
  -H "Authorization: Bearer {厨师的token}"
```

响应示例：
```json
[
  {
    "id": 1,
    "chef_id": 2,
    "customer_id": 1,
    "chef_username": "chef_bob",
    "customer_username": "alice",
    "status": "pending",
    "created_at": "2025-11-06T12:30:00",
    "updated_at": null
  }
]
```

### 5. 厨师处理绑定请求

**同意绑定：**
```bash
curl -X PUT "http://localhost:8000/api/bindings/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {厨师的token}" \
  -d '{
    "status": "approved"
  }'
```

**拒绝绑定：**
```bash
curl -X PUT "http://localhost:8000/api/bindings/1" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {厨师的token}" \
  -d '{
    "status": "rejected"
  }'
```

响应示例：
```json
{
  "id": 1,
  "chef_id": 2,
  "customer_id": 1,
  "chef_username": "chef_bob",
  "customer_username": "alice",
  "status": "approved",
  "created_at": "2025-11-06T12:30:00",
  "updated_at": "2025-11-06T12:35:00"
}
```

### 6. 查看我的绑定关系

**顾客查看**：
```bash
curl -X GET "http://localhost:8000/api/bindings/my-bindings" \
  -H "Authorization: Bearer {顾客的token}"
```

返回顾客绑定的所有厨师列表（包括 pending, approved, rejected 状态）。

**厨师查看**：
```bash
curl -X GET "http://localhost:8000/api/bindings/my-bindings" \
  -H "Authorization: Bearer {厨师的token}"
```

返回所有已同意绑定的顾客列表（只显示 approved 状态）。

### 7. 解除绑定关系

顾客或厨师都可以解除绑定：

```bash
curl -X DELETE "http://localhost:8000/api/bindings/1" \
  -H "Authorization: Bearer {token}"
```

### 8. 顾客选菜

顾客登录后可以选择菜品：

```bash
curl -X POST "http://localhost:8000/api/customer-selections" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {顾客的token}" \
  -d '{
    "dish_id": 1
  }'
```

### 9. 厨师查看绑定顾客的选菜

厨师只能看到已绑定顾客今天选择的菜品：

```bash
curl -X GET "http://localhost:8000/api/customer-selections/all" \
  -H "Authorization: Bearer {厨师的token}"
```

响应示例：
```json
[
  {
    "id": 1,
    "user_id": 1,
    "dish_id": 3,
    "date": "2025-11-06",
    "created_at": "2025-11-06T10:00:00"
  }
]
```

## 完整使用流程示例

### 场景：Alice（顾客）绑定 Bob（厨师）

1. **Alice 和 Bob 分别注册账号**
   - Alice 注册为 customer
   - Bob 注册为 chef

2. **Alice 申请绑定 Bob**
   - Alice 通过 Bob 的 username "chef_bob" 发起绑定请求

3. **Bob 收到并同意绑定请求**
   - Bob 查看待处理的绑定请求
   - Bob 同意 Alice 的绑定请求

4. **Alice 每天选择菜品**
   - Alice 登录后从菜单中选择喜欢的菜品

5. **Bob 查看 Alice 的选菜**
   - Bob 登录后可以看到 Alice 今天选择的所有菜品
   - Bob 决定制作哪些菜品

## 注意事项

1. **认证**：所有绑定相关的接口都需要 JWT token 认证
2. **权限**：
   - 只有顾客可以发起绑定请求
   - 只有厨师可以处理绑定请求
   - 厨师只能看到已绑定顾客的选菜
3. **状态管理**：
   - `pending`: 待审批
   - `approved`: 已同意
   - `rejected`: 已拒绝
4. **数据隔离**：厨师看不到未绑定顾客的选菜记录

## 测试建议

使用 Swagger UI 进行测试：http://localhost:8000/docs

1. 先注册两个账号（一个 chef，一个 customer）
2. 分别登录获取 token
3. 在 Swagger UI 右上角点击 "Authorize" 输入 token
4. 按照上述流程测试各个接口
