document.addEventListener('slidesLoaded', () => {
    const slides = document.querySelectorAll('.slide-container');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    
    // 状态变量
    let currentSlideIndex = 0;
    let isPresentationMode = false;
    let isNavigating = false; // 用于滚轮翻页的防抖动锁

    // 初始化
    if (slides.length === 0) return;
    totalPagesSpan.textContent = slides.length;
    currentPageSpan.textContent = 1;
    
    // 标记第一页为 active
    slides[0].classList.add('active');

    // ============================================
    // 核心跳转逻辑 (统一入口)
    // ============================================
    function goToSlide(index) {
        // 边界检查
        if (index < 0 || index >= slides.length) return;
        
        currentSlideIndex = index;
        
        if (isPresentationMode) {
            // 演示模式：更新 active 类，触发 CSS 动画
            updatePresentationView();
        } else {
            // 普通模式：平滑滚动
            slides[currentSlideIndex].scrollIntoView({behavior: 'smooth', block: 'center'});
        }
        updatePageDisplay();
    }

    function nextSlide() { goToSlide(currentSlideIndex + 1); }
    function prevSlide() { goToSlide(currentSlideIndex - 1); }

    // ============================================
    // 逻辑 A: 普通滚动模式监听 (Observer)
    // ============================================
    const observer = new IntersectionObserver((entries) => {
        if (isPresentationMode) return; // 演示模式下禁用观察器，完全由逻辑控制

        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const index = Array.from(slides).indexOf(entry.target);
                if (index !== -1) {
                    currentSlideIndex = index;
                    updatePageDisplay();
                }
            }
        });
    }, { root: null, threshold: 0.55 });

    slides.forEach(slide => observer.observe(slide));

    // ============================================
    // 逻辑 B: 交互控制 (键盘 / 鼠标 / 链接)
    // ============================================
    
    // 1. 键盘控制
    document.addEventListener('keydown', (e) => {
        const isNext = (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown');
        const isPrev = (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp');

        if (isNext || isPrev) {
            e.preventDefault();
            if (isNext) nextSlide();
            else prevSlide();
        }
    });

    // 2. 鼠标点击控制 (演示模式专用)
    document.addEventListener('click', (e) => {
        // --- 处理超链接跳转 (适用于所有模式) ---
        // 查找点击是否发生在指向 #slide 的链接上
        const link = e.target.closest('a[href^="#slide"]');
        if (link) {
            e.preventDefault(); // 阻止默认锚点跳转
            const targetId = link.getAttribute('href').substring(1); // 获取 slideX
            const targetSlide = document.getElementById(targetId);
            if (targetSlide) {
                const index = Array.from(slides).indexOf(targetSlide);
                if (index !== -1) goToSlide(index);
            }
            return; // 处理完链接后直接返回，不触发翻页
        }

        // --- 处理点击翻页 (仅演示模式) ---
        if (!isPresentationMode) return;

        // 如果点击的是按钮或其他交互元素，忽略翻页
        if (e.target.closest('button') || e.target.closest('#control-bar')) return;

        // 点击屏幕右侧 70% -> 下一页，左侧 30% -> 上一页
        const width = window.innerWidth;
        if (e.clientX > width * 0.3) {
            nextSlide();
        } else {
            prevSlide();
        }
    });

    // 3. 鼠标滚轮控制 (演示模式专用) - 带防抖
    document.addEventListener('wheel', (e) => {
        if (!isPresentationMode) return;
        
        // 如果正在冷却中，忽略滚轮事件
        if (isNavigating) return;
        
        // 忽略微小的触控板抖动
        if (Math.abs(e.deltaY) < 20) return;

        // 锁定状态，400ms 后解锁
        isNavigating = true;
        setTimeout(() => { isNavigating = false; }, 400);

        if (e.deltaY > 0) {
            nextSlide();
        } else {
            prevSlide();
        }
    }, { passive: true });

    // ============================================
    // 逻辑 C: 演示模式切换 (Fullscreen)
    // ============================================
    fullscreenBtn.addEventListener('click', togglePresentationMode);

    function togglePresentationMode() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(e => console.error(e));
        } else {
            document.exitFullscreen();
        }
    }

    // 监听全屏状态变化
    document.addEventListener('fullscreenchange', () => {
        if (document.fullscreenElement) {
            // 进入演示模式
            isPresentationMode = true;
            document.body.classList.add('presentation-mode');
            fullscreenBtn.innerHTML = '<i class="fa-solid fa-compress"></i>';
            
            updateScale();
            updatePresentationView();
            
            window.addEventListener('resize', updateScale);
            
        } else {
            // 退出演示模式
            isPresentationMode = false;
            document.body.classList.remove('presentation-mode');
            fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand"></i>';
            
            window.removeEventListener('resize', updateScale);
            
            // 退出时定位回当前页
            slides[currentSlideIndex].scrollIntoView({block: 'center'});
        }
    });

    // 动态缩放：保持 16:9 比例并留白
    function updateScale() {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const cardWidth = 1280;
        const cardHeight = 720;
        const margin = 0.90; // 90% 屏幕占比

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