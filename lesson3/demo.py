#!/usr/bin/env python3
"""
用户登录模块演示脚本
展示如何使用User和UserManager类
"""

from user import User, UserManager


def main():
    """主演示函数"""
    print("=" * 50)
    print("用户登录模块演示")
    print("=" * 50)
    
    # 创建用户管理器
    user_manager = UserManager()
    
    print("\n1. 注册用户演示")
    print("-" * 30)
    
    # 注册几个用户
    users_to_register = [
        ("alice", "password123"),
        ("bob", "secret456"),
        ("charlie", "mypass789")
    ]
    
    for username, password in users_to_register:
        success = user_manager.register_user(username, password)
        print(f"注册用户 '{username}': {'成功' if success else '失败'}")
    
    # 尝试重复注册
    print(f"重复注册 'alice': {'成功' if user_manager.register_user('alice', 'newpass') else '失败'}")
    
    # 尝试无效注册
    print(f"空用户名注册: {'成功' if user_manager.register_user('', 'pass') else '失败'}")
    print(f"空密码注册: {'成功' if user_manager.register_user('test', '') else '失败'}")
    
    print("\n2. 用户登录演示")
    print("-" * 30)
    
    # 正确登录
    print(f"alice 正确登录: {'成功' if user_manager.login_user('alice', 'password123') else '失败'}")
    print(f"bob 正确登录: {'成功' if user_manager.login_user('bob', 'secret456') else '失败'}")
    
    # 错误登录
    print(f"charlie 错误密码登录: {'成功' if user_manager.login_user('charlie', 'wrongpass') else '失败'}")
    print(f"不存在用户登录: {'成功' if user_manager.login_user('nonexistent', 'pass') else '失败'}")
    
    print("\n3. 登录状态检查")
    print("-" * 30)
    
    all_users = ["alice", "bob", "charlie", "nonexistent"]
    for username in all_users:
        status = user_manager.is_user_logged_in(username)
        print(f"用户 '{username}' 登录状态: {'已登录' if status else '未登录'}")
    
    print("\n4. 获取用户信息")
    print("-" * 30)
    
    for username in ["alice", "bob", "nonexistent"]:
        user = user_manager.get_user(username)
        if user:
            print(f"用户信息: {user}")
        else:
            print(f"用户 '{username}' 不存在")
    
    print("\n5. 用户登出演示")
    print("-" * 30)
    
    print(f"alice 登出: {'成功' if user_manager.logout_user('alice') else '失败'}")
    print(f"alice 登录状态: {'已登录' if user_manager.is_user_logged_in('alice') else '未登录'}")
    
    print("\n6. 完整工作流程演示")
    print("-" * 30)
    
    # 创建一个新的用户管理器演示完整流程
    demo_manager = UserManager()
    
    # 注册 -> 登录 -> 检查状态 -> 登出 -> 再次登录
    steps = [
        ("注册用户 'demo'", lambda: demo_manager.register_user("demo", "demopass")),
        ("登录用户 'demo'", lambda: demo_manager.login_user("demo", "demopass")),
        ("检查登录状态", lambda: demo_manager.is_user_logged_in("demo")),
        ("登出用户 'demo'", lambda: demo_manager.logout_user("demo")),
        ("再次检查状态", lambda: demo_manager.is_user_logged_in("demo")),
        ("重新登录", lambda: demo_manager.login_user("demo", "demopass")),
        ("最终状态", lambda: demo_manager.is_user_logged_in("demo"))
    ]
    
    for step_name, step_func in steps:
        result = step_func()
        if isinstance(result, bool):
            status = "成功" if result else "失败"
        else:
            status = str(result)
        print(f"{step_name}: {status}")
    
    print("\n" + "=" * 50)
    print("演示结束")
    print("=" * 50)


if __name__ == "__main__":
    main() 