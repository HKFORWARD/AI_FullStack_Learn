"""
用户登录模块
包含基本的用户类和登录验证功能
"""

class User:
    """用户类"""
    
    def __init__(self, username, password):
        """
        初始化用户
        
        Args:
            username (str): 用户名
            password (str): 密码
        """
        self.username = username
        self._password = password  # 使用下划线表示私有属性
        self.is_logged_in = False
    
    def authenticate(self, password):
        """
        验证密码
        
        Args:
            password (str): 待验证的密码
            
        Returns:
            bool: 验证是否成功
        """
        return self._password == password
    
    def login(self, password):
        """
        用户登录
        
        Args:
            password (str): 密码
            
        Returns:
            bool: 登录是否成功
        """
        if self.authenticate(password):
            self.is_logged_in = True
            return True
        return False
    
    def logout(self):
        """用户登出"""
        self.is_logged_in = False
    
    def __str__(self):
        return f"User(username='{self.username}', is_logged_in={self.is_logged_in})"


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        """初始化用户管理器"""
        self.users = {}  # 存储用户的字典，key是用户名，value是User对象
    
    def register_user(self, username, password):
        """
        注册新用户
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 注册是否成功
        """
        if username in self.users:
            return False  # 用户已存在
        
        if not username or not password:
            return False  # 用户名或密码为空
        
        self.users[username] = User(username, password)
        return True
    
    def login_user(self, username, password):
        """
        用户登录
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 登录是否成功
        """
        if username not in self.users:
            return False  # 用户不存在
        
        user = self.users[username]
        return user.login(password)
    
    def logout_user(self, username):
        """
        用户登出
        
        Args:
            username (str): 用户名
            
        Returns:
            bool: 登出是否成功
        """
        if username not in self.users:
            return False  # 用户不存在
        
        self.users[username].logout()
        return True
    
    def is_user_logged_in(self, username):
        """
        检查用户是否已登录
        
        Args:
            username (str): 用户名
            
        Returns:
            bool: 用户是否已登录
        """
        if username not in self.users:
            return False
        
        return self.users[username].is_logged_in
    
    def get_user(self, username):
        """
        获取用户对象
        
        Args:
            username (str): 用户名
            
        Returns:
            User or None: 用户对象，如果不存在则返回None
        """
        return self.users.get(username)


# 简单的使用示例
if __name__ == "__main__":
    # 创建用户管理器
    user_manager = UserManager()
    
    # 注册用户
    print("注册用户 'alice':", user_manager.register_user("alice", "password123"))
    print("注册用户 'bob':", user_manager.register_user("bob", "secret456"))
    
    # 尝试重复注册
    print("重复注册 'alice':", user_manager.register_user("alice", "newpassword"))
    
    # 用户登录
    print("alice 登录:", user_manager.login_user("alice", "password123"))
    print("bob 错误密码登录:", user_manager.login_user("bob", "wrongpassword"))
    print("bob 正确密码登录:", user_manager.login_user("bob", "secret456"))
    
    # 检查登录状态
    print("alice 是否已登录:", user_manager.is_user_logged_in("alice"))
    print("bob 是否已登录:", user_manager.is_user_logged_in("bob"))
    
    # 用户登出
    print("alice 登出:", user_manager.logout_user("alice"))
    print("alice 是否已登录:", user_manager.is_user_logged_in("alice")) 