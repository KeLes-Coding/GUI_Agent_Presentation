document.addEventListener('slidesLoaded', () => {
    const slides = document.querySelectorAll('.slide-container');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    
    // 状态变量
    let currentSlideIndex = 0;
    let isPresentationMode = false;
    let isNavigating = false;

    // --- 1. 初始化检查 ---
    if (slides.length === 0) {
        console.error("未检测到幻灯片，脚本停止。");
        return;
    }

    // 更新总页数
    totalPagesSpan.textContent = slides.length;
    currentPageSpan.textContent = 1;
    slides[0].classList.add('active');

    // ============================================
    // 核心功能：切换模式 (解耦版)
    // ============================================
    function setPresentationMode(enable) {
        isPresentationMode = enable;

        if (enable) {
            // 进入演示模式
            document.body.classList.add('presentation-mode');
            fullscreenBtn.innerHTML = '<i class="fa-solid fa-compress"></i>'; // 图标变"退出"
            
            // 立即计算缩放并显示当前页
            updateScale();
            updatePresentationView();
            window.addEventListener('resize', updateScale);

            // 尝试申请全屏 (如果浏览器允许)
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {
                    console.log("全屏请求被拦截或不支持 (不影响正常演示):", err);
                });
            }

        } else {
            // 退出演示模式
            document.body.classList.remove('presentation-mode');
            fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand"></i>'; // 图标变"全屏"
            
            window.removeEventListener('resize', updateScale);

            // 退出全屏
            if (document.fullscreenElement) {
                document.exitFullscreen().catch(() => {});
            }

            // 滚动回当前页的位置
            setTimeout(() => {
                slides[currentSlideIndex].scrollIntoView({behavior: 'smooth', block: 'center'});
            }, 100);
        }
    }

    // ============================================
    // 交互绑定
    // ============================================

    // 1. 按钮点击 (直接调用切换逻辑)
    fullscreenBtn.addEventListener('click', () => {
        setPresentationMode(!isPresentationMode);
    });

    // 2. 监听 ESC 键退出 (双重保险)
    document.addEventListener('fullscreenchange', () => {
        // 只有当用户通过 ESC 键强制退出全屏时，我们要同步状态
        if (!document.fullscreenElement && isPresentationMode) {
            setPresentationMode(false);
        }
    });

    // 3. 翻页逻辑
    function goToSlide(index) {
        if (index < 0 || index >= slides.length) return;
        currentSlideIndex = index;
        
        if (isPresentationMode) {
            updatePresentationView();
        } else {
            slides[currentSlideIndex].scrollIntoView({behavior: 'smooth', block: 'center'});
        }
        updatePageDisplay();
    }

    function nextSlide() { goToSlide(currentSlideIndex + 1); }
    function prevSlide() { goToSlide(currentSlideIndex - 1); }

    // 4. 键盘监听
    document.addEventListener('keydown', (e) => {
        const isNext = (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown');
        const isPrev = (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp');

        if (isNext || isPrev) {
            e.preventDefault();
            isNext ? nextSlide() : prevSlide();
        }
    });

    // 5. 鼠标点击翻页 (仅演示模式)
    document.addEventListener('click', (e) => {
        // 处理目录跳转链接
        const link = e.target.closest('a[href^="#slide"]');
        if (link) {
            e.preventDefault();
            const targetId = link.getAttribute('href').substring(1);
            const targetSlide = document.getElementById(targetId);
            if (targetSlide) {
                const index = Array.from(slides).indexOf(targetSlide);
                if (index !== -1) goToSlide(index);
            }
            return;
        }

        if (!isPresentationMode) return;
        if (e.target.closest('button') || e.target.closest('#control-bar')) return;

        // 简单的左右分屏点击
        if (e.clientX > window.innerWidth * 0.3) {
            nextSlide();
        } else {
            prevSlide();
        }
    });

    // 6. 滚轮翻页
    document.addEventListener('wheel', (e) => {
        if (!isPresentationMode || isNavigating) return;
        if (Math.abs(e.deltaY) < 20) return;

        isNavigating = true;
        setTimeout(() => { isNavigating = false; }, 400);

        e.deltaY > 0 ? nextSlide() : prevSlide();
    }, { passive: true });


    // ============================================
    // 视图更新辅助函数
    // ============================================
    function updateScale() {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const cardWidth = 1280;
        const cardHeight = 720;
        const margin = 0.90;

        const scaleX = (viewportWidth * margin) / cardWidth;
        const scaleY = (viewportHeight * margin) / cardHeight;
        const scale = Math.min(scaleX, scaleY);
        
        document.documentElement.style.setProperty('--scale-factor', scale);
    }

    function updatePresentationView() {
        slides.forEach((slide, index) => {
            if (index === currentSlideIndex) {
                slide.classList.add('active');
            } else {
                slide.classList.remove('active');
            }
        });
    }

    function updatePageDisplay() {
        currentPageSpan.textContent = currentSlideIndex + 1;
    }
});