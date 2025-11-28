#!/usr/bin/env python3
"""
API功能测试脚本
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_health_check():
    """测试健康检查"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"健康检查: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"健康检查失败: {e}")
        return False

def test_user_registration():
    """测试用户注册"""
    try:
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"用户注册: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"用户注册失败: {e}")
        return False

def test_user_login():
    """测试用户登录"""
    try:
        login_data = {
            "username": "testuser",
            "password": "testpassword123"
        }
        response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
        print(f"用户登录: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            print(f"Token类型: {token_data.get('token_type')}")
            print(f"Access Token: {token_data.get('access_token')[:50]}...")
            return token_data.get("access_token")
        return None
    except Exception as e:
        print(f"用户登录失败: {e}")
        return None

def test_protected_endpoint(token):
    """测试受保护的端点"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"获取用户信息: {response.status_code} - {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"获取用户信息失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始API测试...")

    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)

    # 测试健康检查
    if not test_health_check():
        print("❌ 健康检查失败")
        return

    # 测试用户注册
    if not test_user_registration():
        print("❌ 用户注册失败")
        return

    # 测试用户登录
    token = test_user_login()
    if not token:
        print("❌ 用户登录失败")
        return

    # 测试受保护的端点
    if not test_protected_endpoint(token):
        print("❌ 受保护端点测试失败")
        return

    print("✅ 所有测试通过！API功能正常")

if __name__ == "__main__":
    main()