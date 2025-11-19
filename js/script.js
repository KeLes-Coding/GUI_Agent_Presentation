document.addEventListener('slidesLoaded', () => {
    const slides = document.querySelectorAll('.slide-container');
    let currentSlideIndex = 0;

    // 获取页码显示元素
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');

    if (slides.length === 0) {
        // 如果没有幻灯片，隐藏页码显示
        document.getElementById('page-indicator').style.display = 'none';
        return;
    }

    // 初始化总页数
    totalPagesSpan.textContent = slides.length;
    // 初始化当前页码
    currentPageSpan.textContent = 1;


    // 1. 核心：使用 IntersectionObserver 自动同步当前页码
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const index = Array.from(slides).indexOf(entry.target);
                if (index !== -1) {
                    currentSlideIndex = index;
                    // 更新页码显示
                    currentPageSpan.textContent = currentSlideIndex + 1;
                    // console.log("用户当前浏览到第:", currentSlideIndex + 1, "页");
                }
            }
        });
    }, {
        root: null, // 视口
        threshold: 0.55 // 只有当页面显示超过 55% 时，才更新索引
    });

    // 开启观察每一页
    slides.forEach(slide => observer.observe(slide));

    // Fix initial view - 确保页面加载时第一页在中间
    // 延迟一点点执行，确保所有 slides 都已插入 DOM 并计算好尺寸
    setTimeout(() => {
        if (slides[0]) {
            slides[0].scrollIntoView({block: 'center'});
        }
    }, 100); // 延迟 100ms


    // 2. 键盘控制逻辑
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
            e.preventDefault();
            if (currentSlideIndex < slides.length - 1) {
                const nextIndex = currentSlideIndex + 1;
                scrollToSlide(nextIndex);
            }
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            if (currentSlideIndex > 0) {
                const prevIndex = currentSlideIndex - 1;
                scrollToSlide(prevIndex);
            }
        }
    });

    function scrollToSlide(index) {
        slides[index].scrollIntoView({
            behavior: 'smooth',
            block: 'center' // 始终把幻灯片放在屏幕正中间
        });
    }
});