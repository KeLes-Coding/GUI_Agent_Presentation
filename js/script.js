document.addEventListener('slidesLoaded', () => {
    const slides = document.querySelectorAll('.slide-container');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');
    const fullscreenBtn = document.getElementById('fullscreen-btn');
    
    // 当前索引
    let currentSlideIndex = 0;
    // 是否处于演示模式
    let isPresentationMode = false;

    // 初始化
    if (slides.length === 0) return;
    totalPagesSpan.textContent = slides.length;
    currentPageSpan.textContent = 1;
    
    // 标记第一页为 active (用于演示模式初始状态)
    slides[0].classList.add('active');

    // ============================================
    // 逻辑 A: 普通滚动模式 (Observer)
    // ============================================
    const observer = new IntersectionObserver((entries) => {
        // 如果在演示模式，不通过观察器更新，完全由键盘逻辑控制
        if (isPresentationMode) return; 

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
    // 逻辑 B: 键盘控制 (双模式通用)
    // ============================================
    document.addEventListener('keydown', (e) => {
        const isNext = (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ' || e.key === 'PageDown');
        const isPrev = (e.key === 'ArrowLeft' || e.key === 'ArrowUp' || e.key === 'PageUp');

        if (isNext || isPrev) {
            e.preventDefault();
            
            if (isNext && currentSlideIndex < slides.length - 1) {
                currentSlideIndex++;
            } else if (isPrev && currentSlideIndex > 0) {
                currentSlideIndex--;
            } else {
                return; // 没变
            }

            // 执行跳转
            if (isPresentationMode) {
                updatePresentationView();
            } else {
                slides[currentSlideIndex].scrollIntoView({behavior: 'smooth', block: 'center'});
            }
            updatePageDisplay();
        }
    });

    // ============================================
    // 逻辑 C: 演示模式核心 (Scale & Toggle)
    // ============================================
    fullscreenBtn.addEventListener('click', togglePresentationMode);

    function togglePresentationMode() {
        if (!document.fullscreenElement) {
            // 1. 进入全屏
            document.documentElement.requestFullscreen().catch(e => console.error(e));
        } else {
            // 退出全屏
            document.exitFullscreen();
        }
    }

    // 监听全屏变化事件
    document.addEventListener('fullscreenchange', () => {
        if (document.fullscreenElement) {
            // 进入了演示模式
            isPresentationMode = true;
            document.body.classList.add('presentation-mode');
            fullscreenBtn.innerHTML = '<i class="fa-solid fa-compress"></i>';
            
            // 计算缩放并显示当前页
            updateScale();
            updatePresentationView();
            
            // 监听窗口大小变化以便重新计算缩放
            window.addEventListener('resize', updateScale);
            
        } else {
            // 退出了演示模式
            isPresentationMode = false;
            document.body.classList.remove('presentation-mode');
            fullscreenBtn.innerHTML = '<i class="fa-solid fa-expand"></i>';
            
            window.removeEventListener('resize', updateScale);
            
            // 恢复滚动位置到当前页
            slides[currentSlideIndex].scrollIntoView({block: 'center'});
        }
    });

    // 动态计算缩放比例：让 1280x720 的卡片适应屏幕，保留 5% 的边距
    function updateScale() {
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        const cardWidth = 1280;
        const cardHeight = 720;
        const margin = 0.90; // 占用屏幕 90% 的空间 (即 5% 边距)

        const scaleX = (viewportWidth * margin) / cardWidth;
        const scaleY = (viewportHeight * margin) / cardHeight;
        
        // 取较小值，确保完全放入屏幕
        const scale = Math.min(scaleX, scaleY);
        
        // 设置 CSS 变量
        document.documentElement.style.setProperty('--scale-factor', scale);
    }

    // 切换 Active 类 (演示模式专用)
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