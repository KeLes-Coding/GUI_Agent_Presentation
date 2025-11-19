// 监听 loader.js 发出的 'slidesLoaded' 事件
document.addEventListener('slidesLoaded', () => {
    const slides = document.querySelectorAll('.slide-container');
    let currentSlideIndex = 0;

    if (slides.length === 0) return;

    // 初始化：确保第一页可见，并修正滚动位置
    scrollToSlide(0);

    // 键盘监听
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {
            e.preventDefault();
            if (currentSlideIndex < slides.length - 1) {
                currentSlideIndex++;
                scrollToSlide(currentSlideIndex);
            }
        } else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            e.preventDefault();
            if (currentSlideIndex > 0) {
                currentSlideIndex--;
                scrollToSlide(currentSlideIndex);
            }
        }
    });

    function scrollToSlide(index) {
        slides[index].scrollIntoView({
            behavior: 'smooth',
            block: 'center' // 垂直居中
        });
    }
});