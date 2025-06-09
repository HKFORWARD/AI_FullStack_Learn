"""
用户登录模块的单元测试
"""

import unittest
from user import User, UserManager


class TestUser(unittest.TestCase):
    """测试User类"""
    
    def setUp(self):
        """每个测试方法运行前的准备工作"""
        self.user = User("testuser", "testpassword")
    
    def test_user_initialization(self):
        """测试用户初始化"""
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user._password, "testpassword")
        self.assertFalse(self.user.is_logged_in)
    
    def test_authenticate_correct_password(self):
        """测试正确密码认证"""
        self.assertTrue(self.user.authenticate("testpassword"))
    
    def test_authenticate_wrong_password(self):
        """测试错误密码认证"""
        self.assertFalse(self.user.authenticate("wrongpassword"))
    
    def test_login_success(self):
        """测试成功登录"""
        result = self.user.login("testpassword")
        self.assertTrue(result)
        self.assertTrue(self.user.is_logged_in)
    
    def test_login_failure(self):
        """测试登录失败"""
        result = self.user.login("wrongpassword")
        self.assertFalse(result)
        self.assertFalse(self.user.is_logged_in)
    
    def test_logout(self):
        """测试登出功能"""
        # 先登录
        self.user.login("testpassword")
        self.assertTrue(self.user.is_logged_in)
        
        # 然后登出
        self.user.logout()
        self.assertFalse(self.user.is_logged_in)
    
    def test_str_representation(self):
        """测试字符串表示"""
        expected = "User(username='testuser', is_logged_in=False)"
        self.assertEqual(str(self.user), expected)


class TestUserManager(unittest.TestCase):
    """测试UserManager类"""
    
    def setUp(self):
        """每个测试方法运行前的准备工作"""
        self.user_manager = UserManager()
    
    def test_register_user_success(self):
        """测试成功注册用户"""
        result = self.user_manager.register_user("alice", "password123")
        self.assertTrue(result)
        self.assertIn("alice", self.user_manager.users)
    
    def test_register_user_duplicate(self):
        """测试重复注册用户"""
        # 第一次注册
        self.user_manager.register_user("alice", "password123")
        
        # 第二次注册相同用户名
        result = self.user_manager.register_user("alice", "newpassword")
        self.assertFalse(result)
    
    def test_register_user_empty_username(self):
        """测试空用户名注册"""
        result = self.user_manager.register_user("", "password123")
        self.assertFalse(result)
    
    def test_register_user_empty_password(self):
        """测试空密码注册"""
        result = self.user_manager.register_user("alice", "")
        self.assertFalse(result)
    
    def test_login_user_success(self):
        """测试成功登录"""
        # 先注册用户
        self.user_manager.register_user("alice", "password123")
        
        # 然后登录
        result = self.user_manager.login_user("alice", "password123")
        self.assertTrue(result)
        self.assertTrue(self.user_manager.is_user_logged_in("alice"))
    
    def test_login_user_wrong_password(self):
        """测试错误密码登录"""
        # 先注册用户
        self.user_manager.register_user("alice", "password123")
        
        # 使用错误密码登录
        result = self.user_manager.login_user("alice", "wrongpassword")
        self.assertFalse(result)
        self.assertFalse(self.user_manager.is_user_logged_in("alice"))
    
    def test_login_user_not_exist(self):
        """测试不存在的用户登录"""
        result = self.user_manager.login_user("nonexistent", "password")
        self.assertFalse(result)
    
    def test_logout_user_success(self):
        """测试成功登出"""
        # 注册并登录用户
        self.user_manager.register_user("alice", "password123")
        self.user_manager.login_user("alice", "password123")
        
        # 登出
        result = self.user_manager.logout_user("alice")
        self.assertTrue(result)
        self.assertFalse(self.user_manager.is_user_logged_in("alice"))
    
    def test_logout_user_not_exist(self):
        """测试不存在的用户登出"""
        result = self.user_manager.logout_user("nonexistent")
        self.assertFalse(result)
    
    def test_is_user_logged_in_not_exist(self):
        """测试检查不存在用户的登录状态"""
        result = self.user_manager.is_user_logged_in("nonexistent")
        self.assertFalse(result)
    
    def test_get_user_exist(self):
        """测试获取存在的用户"""
        self.user_manager.register_user("alice", "password123")
        user = self.user_manager.get_user("alice")
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "alice")
    
    def test_get_user_not_exist(self):
        """测试获取不存在的用户"""
        user = self.user_manager.get_user("nonexistent")
        self.assertIsNone(user)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_user_workflow(self):
        """测试完整的用户工作流程"""
        user_manager = UserManager()
        
        # 1. 注册用户
        self.assertTrue(user_manager.register_user("alice", "secret123"))
        self.assertTrue(user_manager.register_user("bob", "password456"))
        
        # 2. 登录用户
        self.assertTrue(user_manager.login_user("alice", "secret123"))
        self.assertTrue(user_manager.login_user("bob", "password456"))
        
        # 3. 检查登录状态
        self.assertTrue(user_manager.is_user_logged_in("alice"))
        self.assertTrue(user_manager.is_user_logged_in("bob"))
        
        # 4. 登出一个用户
        self.assertTrue(user_manager.logout_user("alice"))
        self.assertFalse(user_manager.is_user_logged_in("alice"))
        self.assertTrue(user_manager.is_user_logged_in("bob"))  # bob 仍然登录
        
        # 5. 尝试重新登录
        self.assertTrue(user_manager.login_user("alice", "secret123"))
        self.assertTrue(user_manager.is_user_logged_in("alice"))


if __name__ == "__main__":
    # 运行所有测试
    unittest.main(verbosity=2) 