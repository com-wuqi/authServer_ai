#!/usr/bin/env python3
"""
详细的API功能测试脚本
"""
import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def print_test_header(test_name):
    """打印测试标题"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print('='*60)

def test_health_check():
    """测试健康检查"""
    print_test_header("健康检查")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        assert response.status_code == 200, "健康检查失败"
        print("✅ 健康检查通过")
        return True
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_root_endpoint():
    """测试根路径"""
    print_test_header("根路径访问")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.json()}")
        assert response.status_code == 200, "根路径访问失败"
        print("✅ 根路径访问通过")
        return True
    except Exception as e:
        print(f"❌ 根路径访问失败: {e}")
        return False

def test_user_registration():
    """测试用户注册功能"""
    print_test_header("用户注册测试")

    test_cases = [
        {
            "name": "正常注册",
            "data": {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123",
                "full_name": "Test User"
            },
            "should_succeed": True
        },
        {
            "name": "重复用户注册",
            "data": {
                "username": "testuser",
                "email": "test2@example.com",
                "password": "password123",
                "full_name": "Another User"
            },
            "should_succeed": False
        },
        {
            "name": "重复邮箱注册",
            "data": {
                "username": "testuser2",
                "email": "test@example.com",
                "password": "password123",
                "full_name": "Another User"
            },
            "should_succeed": False
        },
        {
            "name": "超长密码测试（73字节）",
            "data": {
                "username": "longpassworduser",
                "email": "long@example.com",
                "password": "a" * 73,  # 73个字节的密码
                "full_name": "Long Password User"
            },
            "should_succeed": False
        },
        {
            "name": "边界密码测试（72字节）",
            "data": {
                "username": "maxpassworduser",
                "email": "max@example.com",
                "password": "a" * 72,  # 72个字节的密码
                "full_name": "Max Password User"
            },
            "should_succeed": True
        },
        {
            "name": "无效邮箱格式",
            "data": {
                "username": "invalidemail",
                "email": "invalid-email",
                "password": "password123",
                "full_name": "Invalid Email User"
            },
            "should_succeed": False
        }
    ]

    all_passed = True
    for test in test_cases:
        try:
            print(f"\n子测试: {test['name']}")
            response = requests.post(f"{BASE_URL}/auth/register", json=test['data'])
            print(f"  状态码: {response.status_code}")

            if test['should_succeed']:
                assert response.status_code == 200, "应该成功但失败了"
                user_data = response.json()
                print(f"  注册成功 - 用户ID: {user_data.get('id')}, 用户名: {user_data.get('username')}")
                assert 'id' in user_data, "响应缺少用户ID"
                assert user_data['username'] == test['data']['username'], "用户名不匹配"
            else:
                assert response.status_code != 200, "应该失败但成功了"
                error_data = response.json()
                print(f"  预期失败 - 响应: {error_data}")

            print("  ✅ 子测试通过")
        except Exception as e:
            print(f"  ❌ 子测试失败: {e}")
            all_passed = False

    return all_passed

def test_user_login():
    """测试用户登录功能"""
    print_test_header("用户登录测试")

    test_cases = [
        {
            "name": "正确凭据登录",
            "data": {"username": "testuser", "password": "testpassword123"},
            "should_succeed": True
        },
        {
            "name": "错误密码登录",
            "data": {"username": "testuser", "password": "wrongpassword"},
            "should_succeed": False
        },
        {
            "name": "不存在的用户登录",
            "data": {"username": "nonexistent", "password": "password"},
            "should_succeed": False
        }
    ]

    all_passed = True
    tokens = {}

    for test in test_cases:
        try:
            print(f"\n子测试: {test['name']}")
            response = requests.post(f"{BASE_URL}/auth/login", data=test['data'])
            print(f"  状态码: {response.status_code}")

            if test['should_succeed']:
                assert response.status_code == 200, "应该成功但失败了"
                token_data = response.json()
                print(f"  登录成功 - Token类型: {token_data.get('token_type')}")
                assert 'access_token' in token_data, "响应缺少access_token"
                tokens[test['data']['username']] = token_data['access_token']
            else:
                assert response.status_code == 401 or response.status_code == 400, f"应该失败但状态码为 {response.status_code}"
                print(f"  预期失败")

            print("  ✅ 子测试通过")
        except Exception as e:
            print(f"  ❌ 子测试失败: {e}")
            all_passed = False

    return all_passed, tokens

def test_protected_endpoints(tokens):
    """测试受保护的端点"""
    print_test_header("受保护端点测试")

    if 'testuser' not in tokens:
        print("❌ 缺少有效Token，跳过受保护端点测试")
        return False

    token = tokens['testuser']
    all_passed = True

    # 获取用户信息测试
    try:
        print("\n子测试: 获取当前用户信息")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"  状态码: {response.status_code}")

        if response.status_code == 200:
            user_data = response.json()
            print(f"  获取成功 - 用户名: {user_data.get('username')}, ID: {user_data.get('id')}")
            assert 'id' in user_data, "响应缺少用户ID"
        else:
            print(f"  ❌ 获取用户信息失败: {response.json()}")
            all_passed = False

        print("  ✅ 子测试通过")
    except Exception as e:
        print(f"  ❌ 子测试失败: {e}")
        all_passed = False

    # 无Token访问测试
    try:
        print("\n子测试: 无Token访问受保护端点")
        response = requests.get(f"{BASE_URL}/auth/me")
        print(f"  状态码: {response.status_code}")
        assert response.status_code == 401, "应该返回401未授权"
        print("  预期失败（未授权）")
        print("  ✅ 子测试通过")
    except Exception as e:
        print(f"  ❌ 子测试失败: {e}")
        all_passed = False

    return all_passed

def test_admin_endpoints(tokens):
    """测试管理员功能（需要手动设置管理员权限）"""
    print_test_header("管理员端点测试")

    print("📝 注意：管理员功能测试需要手动设置用户为管理员权限")
    print("   可以在数据库中执行: UPDATE user SET is_superuser = 1 WHERE username = 'testuser'")

    # 测试普通用户尝试访问管理员端点
    if 'testuser' in tokens:
        try:
            print("\n子测试: 普通用户访问管理员端点")
            headers = {"Authorization": f"Bearer {tokens['testuser']}"}
            response = requests.get(f"{BASE_URL}/users/", headers=headers)
            print(f"  状态码: {response.status_code}")
            # 普通用户应该无法访问管理员端点
            if response.status_code == 403 or response.status_code == 401:
                print("  预期结果（权限不足）")
                print("  ✅ 子测试通过")
                return True
            else:
                print("  ⚠ 返回了意外状态码")
                return False
        except Exception as e:
            print(f"  ❌ 子测试失败: {e}")
            return False

    return False

def main():
    """主测试函数"""
    print("🚀 开始详细的API功能测试...")

    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(2)

    # 执行测试
    tests = []

    # 基础功能测试
    tests.append(("健康检查", test_health_check()))
    tests.append(("根路径访问", test_root_endpoint()))
    tests.append(("用户注册", test_user_registration()))

    # 登录测试
    login_success, tokens = test_user_login()
    tests.append(("用户登录", login_success))

    # 受保护端点测试
    if login_success and tokens:
        tests.append(("受保护端点", test_protected_endpoints(tokens)))
        tests.append(("管理员端点", test_admin_endpoints(tokens)))
    else:
        tests.append(("受保护端点", False))
        tests.append(("管理员端点", False))

    # 总结结果
    print_test_header("测试总结")
    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    for name, result in tests:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name}: {status}")

    print(f"\n📊 测试结果: {passed}/{total} 通过")

    if passed == total:
        print("🎉 所有测试通过！API功能正常")
        print(f"\n🔗 API文档: {BASE_URL}/docs")
        print(f"🔗 健康检查: {BASE_URL}/health")
    else:
        print("⚠ 部分测试失败，请检查服务器状态和配置")
        sys.exit(1)

if __name__ == "__main__":
    main()