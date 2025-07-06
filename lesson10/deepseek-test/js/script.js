/*******************************************************************************
* 项目名称: DeepSeek 官网前端测试版
* 文件: script.js
* 目的: 此文件为DeepSeek官网的前端视觉测试和学习项目提供交互功能。
*       请注意：此网站并非DeepSeek官方网站，仅供测试使用。
*******************************************************************************/

document.addEventListener('DOMContentLoaded', () => {
    // 平滑滚动功能
    const navLinks = document.querySelectorAll('a[data-scroll-to]');
    navLinks.forEach(link => {
        link.addEventListener('click', function (event) {
            event.preventDefault(); // 阻止默认的锚点跳转行为

            const targetId = this.getAttribute('data-scroll-to');
            const targetSection = document.getElementById(targetId);

            if (targetSection) {
                // 使用 scrollIntoView 实现平滑滚动
                targetSection.scrollIntoView({
                    behavior: 'smooth'
                });

                // 如果是移动端菜单，滚动后关闭菜单
                const navList = document.querySelector('.nav-list');
                if (navList.classList.contains('active')) {
                    navList.classList.remove('active');
                }
            }
        });
    });

    // 移动端汉堡菜单切换功能
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navList = document.querySelector('.nav-list');

    hamburgerMenu.addEventListener('click', () => {
        navList.classList.toggle('active');
    });

    // 点击菜单外部区域关闭菜单 (可选，提升用户体验)
    document.addEventListener('click', (event) => {
        const isClickInsideNav = navList.contains(event.target) || hamburgerMenu.contains(event.target);
        if (!isClickInsideNav && navList.classList.contains('active')) {
            navList.classList.remove('active');
        }
    });

    // 监听窗口大小变化，如果从移动端变到桌面端，确保菜单是关闭的
    window.addEventListener('resize', () => {
        if (window.innerWidth > 768 && navList.classList.contains('active')) {
            navList.classList.remove('active');
        }
    });
});