#!/usr/bin/env python3
"""
用户登录系统 - Gradio Web界面
提供用户注册、登录、状态查看和登出功能
"""

import gradio as gr
from user import UserManager

# 全局用户管理器实例
user_manager = UserManager()

# 用于在界面之间传递当前登录用户信息
current_user = {"username": None, "logged_in": False}


def register_user(username, password, confirm_password):
    """
    用户注册功能
    
    Args:
        username (str): 用户名
        password (str): 密码
        confirm_password (str): 确认密码
        
    Returns:
        tuple: (消息, 成功状态样式)
    """
    if not username or not password:
        return "❌ 用户名和密码不能为空！", "color: red;"
    
    if password != confirm_password:
        return "❌ 两次输入的密码不一致！", "color: red;"
    
    if len(password) < 6:
        return "❌ 密码长度至少需要6位！", "color: red;"
    
    success = user_manager.register_user(username, password)
    if success:
        return f"✅ 用户 '{username}' 注册成功！", "color: green;"
    else:
        return f"❌ 用户 '{username}' 已存在！", "color: red;"


def login_user(username, password):
    """
    用户登录功能
    
    Args:
        username (str): 用户名
        password (str): 密码
        
    Returns:
        tuple: (消息, 成功状态样式, 当前用户信息)
    """
    if not username or not password:
        return "❌ 用户名和密码不能为空！", "color: red;", "当前未登录"
    
    success = user_manager.login_user(username, password)
    if success:
        current_user["username"] = username
        current_user["logged_in"] = True
        return f"✅ 用户 '{username}' 登录成功！", "color: green;", f"当前用户: {username} (已登录)"
    else:
        return "❌ 用户名或密码错误！", "color: red;", "当前未登录"


def logout_user():
    """
    用户登出功能
    
    Returns:
        tuple: (消息, 成功状态样式, 当前用户信息)
    """
    if not current_user["logged_in"]:
        return "❌ 当前没有用户登录！", "color: red;", "当前未登录"
    
    username = current_user["username"]
    user_manager.logout_user(username)
    current_user["username"] = None
    current_user["logged_in"] = False
    
    return f"✅ 用户 '{username}' 已成功登出！", "color: green;", "当前未登录"


def get_user_status():
    """
    获取当前用户状态
    
    Returns:
        str: 当前用户状态信息
    """
    if current_user["logged_in"]:
        username = current_user["username"]
        user = user_manager.get_user(username)
        if user:
            return f"👤 当前用户: {username}\n📊 状态: 已登录\n🔐 用户信息: {user}"
        else:
            return "❌ 用户信息异常"
    else:
        return "🚫 当前没有用户登录"


def get_all_users():
    """
    获取所有注册用户列表
    
    Returns:
        str: 所有用户信息
    """
    if not user_manager.users:
        return "📋 暂无注册用户"
    
    user_list = []
    for username, user in user_manager.users.items():
        status = "🟢 已登录" if user.is_logged_in else "🔴 未登录"
        user_list.append(f"👤 {username} - {status}")
    
    return "📋 所有注册用户:\n" + "\n".join(user_list)


def clear_inputs():
    """
    清空输入框
    
    Returns:
        tuple: 空字符串元组
    """
    return "", "", ""


# 创建Gradio界面
def create_interface():
    """创建主界面"""
    
    # 自定义CSS样式
    css = """
    .main-container {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    .status-info {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .success {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
    }
    .error {
        background-color: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        padding: 10px;
    }
    """
    
    with gr.Blocks(css=css, title="用户登录系统", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 🔐 用户登录系统
            
            欢迎使用基于Gradio的用户登录管理系统！
            
            ## 功能特性
            - 👥 用户注册
            - 🔑 用户登录
            - 📊 状态查看
            - 🚪 用户登出
            """, 
            elem_classes="main-container"
        )
        
        with gr.Tabs():
            # 用户注册标签页
            with gr.Tab("👥 用户注册"):
                gr.Markdown("### 注册新用户")
                
                with gr.Row():
                    with gr.Column():
                        reg_username = gr.Textbox(
                            label="用户名", 
                            placeholder="请输入用户名",
                            max_lines=1
                        )
                        reg_password = gr.Textbox(
                            label="密码", 
                            placeholder="请输入密码（至少6位）",
                            type="password",
                            max_lines=1
                        )
                        reg_confirm = gr.Textbox(
                            label="确认密码", 
                            placeholder="请再次输入密码",
                            type="password",
                            max_lines=1
                        )
                        
                        with gr.Row():
                            reg_btn = gr.Button("📝 注册", variant="primary", size="lg")
                            reg_clear_btn = gr.Button("🗑️ 清空", variant="secondary")
                        
                        reg_result = gr.HTML(label="注册结果")
                
                # 注册按钮事件
                reg_btn.click(
                    fn=register_user,
                    inputs=[reg_username, reg_password, reg_confirm],
                    outputs=[reg_result]
                )
                
                # 清空按钮事件
                reg_clear_btn.click(
                    fn=lambda: ("", "", "", ""),
                    outputs=[reg_username, reg_password, reg_confirm, reg_result]
                )
            
            # 用户登录标签页
            with gr.Tab("🔑 用户登录"):
                gr.Markdown("### 用户登录")
                
                with gr.Row():
                    with gr.Column():
                        login_username = gr.Textbox(
                            label="用户名", 
                            placeholder="请输入用户名",
                            max_lines=1
                        )
                        login_password = gr.Textbox(
                            label="密码", 
                            placeholder="请输入密码",
                            type="password",
                            max_lines=1
                        )
                        
                        with gr.Row():
                            login_btn = gr.Button("🔐 登录", variant="primary", size="lg")
                            logout_btn = gr.Button("🚪 登出", variant="secondary", size="lg")
                        
                        login_result = gr.HTML(label="登录结果")
                        current_user_display = gr.Textbox(
                            label="当前状态", 
                            value="当前未登录",
                            interactive=False,
                            max_lines=1
                        )
                
                # 登录按钮事件
                login_btn.click(
                    fn=login_user,
                    inputs=[login_username, login_password],
                    outputs=[login_result, current_user_display]
                )
                
                # 登出按钮事件
                logout_btn.click(
                    fn=logout_user,
                    outputs=[login_result, current_user_display]
                )
            
            # 状态查看标签页
            with gr.Tab("📊 状态查看"):
                gr.Markdown("### 用户状态信息")
                
                with gr.Row():
                    with gr.Column():
                        status_btn = gr.Button("🔍 查看当前用户状态", variant="primary", size="lg")
                        user_status = gr.Textbox(
                            label="当前用户状态",
                            lines=4,
                            interactive=False
                        )
                        
                        all_users_btn = gr.Button("📋 查看所有用户", variant="secondary", size="lg")
                        all_users_status = gr.Textbox(
                            label="所有用户状态",
                            lines=6,
                            interactive=False
                        )
                
                # 状态查看按钮事件
                status_btn.click(
                    fn=get_user_status,
                    outputs=user_status
                )
                
                # 查看所有用户按钮事件
                all_users_btn.click(
                    fn=get_all_users,
                    outputs=all_users_status
                )
        
        # 页脚信息
        gr.Markdown(
            """
            ---
            💡 **使用提示:**
            1. 首先在"用户注册"页面注册一个新账户
            2. 然后在"用户登录"页面使用注册的账户登录
            3. 在"状态查看"页面可以查看当前登录状态和所有用户信息
            4. 登录后可以在"用户登录"页面点击"登出"按钮
            
            🔧 **技术栈:** Python + Gradio + 自定义用户管理模块
            """,
            elem_classes="main-container"
        )
    
    return app


if __name__ == "__main__":
    # 预先注册一些示例用户用于测试
    user_manager.register_user("admin", "admin123")
    user_manager.register_user("demo", "demo123")
    user_manager.register_user("test", "test123")
    
    print("🚀 启动用户登录系统...")
    print("📝 已预注册测试用户:")
    print("   - admin / admin123")
    print("   - demo / demo123") 
    print("   - test / test123")
    print("\n🌐 访问地址: http://localhost:7860")
    
    # 创建并启动应用
    app = create_interface()
    app.launch(
        server_name="0.0.0.0",  # 允许外部访问
        server_port=7860,       # 设置端口
        share=False,            # 不创建公共链接
        debug=True,             # 启用调试模式
        show_error=True         # 显示错误信息
    ) 