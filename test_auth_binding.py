"""
测试注册、登录和绑定功能
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def print_response(title, response):
    """打印响应信息"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")

def test_auth_and_binding():
    """测试完整的注册、登录、绑定流程"""

    # 1. 注册一个厨师
    print("\n\n🧑‍🍳 测试 1: 注册厨师账户")
    chef_data = {
        "username": "chef_test",
        "email": "chef@test.com",
        "password": "password123",
        "role": "chef",
        "full_name": "测试厨师"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=chef_data)
    print_response("注册厨师", response)

    # 2. 注册一个顾客
    print("\n\n👤 测试 2: 注册顾客账户")
    customer_data = {
        "username": "customer_test",
        "email": "customer@test.com",
        "password": "password123",
        "role": "customer",
        "full_name": "测试顾客"
    }
    response = requests.post(f"{BASE_URL}/api/auth/register", json=customer_data)
    print_response("注册顾客", response)

    # 3. 厨师登录
    print("\n\n🔐 测试 3: 厨师登录")
    chef_login = {
        "username": "chef_test",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=chef_login)
    print_response("厨师登录", response)

    if response.status_code == 200:
        chef_token = response.json()["token"]
        chef_user = response.json()["user"]
        print(f"\n✅ 厨师登录成功！")
        print(f"   - Token: {chef_token[:50]}...")
        print(f"   - User ID: {chef_user['id']}")
        print(f"   - Username: {chef_user['username']}")
        print(f"   - Name: {chef_user['name']}")
        print(f"   - Role: {chef_user['role']}")
    else:
        print("\n❌ 厨师登录失败！")
        return

    # 4. 顾客登录
    print("\n\n🔐 测试 4: 顾客登录")
    customer_login = {
        "username": "customer_test",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", json=customer_login)
    print_response("顾客登录", response)

    if response.status_code == 200:
        customer_token = response.json()["token"]
        customer_user = response.json()["user"]
        print(f"\n✅ 顾客登录成功！")
        print(f"   - Token: {customer_token[:50]}...")
        print(f"   - User ID: {customer_user['id']}")
        print(f"   - Username: {customer_user['username']}")
        print(f"   - Name: {customer_user['name']}")
        print(f"   - Role: {customer_user['role']}")
    else:
        print("\n❌ 顾客登录失败！")
        return

    # 5. 顾客申请绑定厨师
    print("\n\n🤝 测试 5: 顾客申请绑定厨师")
    binding_request = {
        "chef_username": "chef_test"
    }
    headers = {"Authorization": f"Bearer {customer_token}"}
    response = requests.post(
        f"{BASE_URL}/api/binding-requests",
        json=binding_request,
        headers=headers
    )
    print_response("创建绑定请求", response)

    if response.status_code == 201:
        binding = response.json()
        print(f"\n✅ 绑定请求创建成功！")
        print(f"   - Binding ID: {binding['id']}")
        print(f"   - Customer: {binding['customerName']} (ID: {binding['customerId']})")
        print(f"   - Chef: {binding['chefName']} (ID: {binding['chefId']})")
        print(f"   - Status: {binding['status']}")
        binding_id = binding['id']
    else:
        print("\n❌ 绑定请求创建失败！")
        return

    # 6. 厨师查看待处理的绑定请求
    print("\n\n📋 测试 6: 厨师查看待处理的绑定请求")
    headers = {"Authorization": f"Bearer {chef_token}"}
    response = requests.get(
        f"{BASE_URL}/api/binding-requests?chefId={chef_user['id']}",
        headers=headers
    )
    print_response("查看绑定请求", response)

    if response.status_code == 200:
        requests_list = response.json()
        print(f"\n✅ 查询成功！共有 {len(requests_list)} 个待处理请求")
        for req in requests_list:
            print(f"   - Request ID: {req['id']}")
            print(f"     顾客: {req['customerName']}")
            print(f"     状态: {req['status']}")

    # 7. 厨师接受绑定请求
    print("\n\n✅ 测试 7: 厨师接受绑定请求")
    update_data = {"status": "accepted"}  # 前端使用 'accepted'
    response = requests.put(
        f"{BASE_URL}/api/binding-requests/{binding_id}",
        json=update_data,
        headers=headers
    )
    print_response("接受绑定请求", response)

    if response.status_code == 200:
        binding = response.json()
        print(f"\n✅ 绑定请求已接受！")
        print(f"   - 新状态: {binding['status']}")

    # 8. 查看我的绑定关系
    print("\n\n📋 测试 8: 厨师查看已绑定的顾客")
    response = requests.get(
        f"{BASE_URL}/api/bindings/my-bindings",
        headers=headers
    )
    print_response("查看我的绑定关系", response)

    print("\n\n" + "="*60)
    print("✨ 测试完成！")
    print("="*60)

if __name__ == "__main__":
    try:
        test_auth_and_binding()
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
