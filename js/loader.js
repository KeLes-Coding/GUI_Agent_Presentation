async function loadSlides() {
    const container = document.getElementById('presentation-deck');
    let slideIndex = 1;
    let keepLoading = true;

    console.log("开始自动加载幻灯片...");

    while (keepLoading) {
        try {
            // 1. 请求幻灯片文件
            const response = await fetch(`slides/slide${slideIndex}.html`);
            
            if (!response.ok) {
                console.log(`检测到 slide${slideIndex}.html 不存在，加载结束。共加载 ${slideIndex - 1} 页。`);
                keepLoading = false;
                break;
            }
            
            const html = await response.text();
            
            // 2. 插入 HTML
            container.insertAdjacentHTML('beforeend', html);
            
            // 3. 获取当前插入的 slide DOM 对象
            const currentSlideElement = container.lastElementChild;
            
            // --- 注入 1: 校徽 (右上角) ---
            // 请确保 assets/scnu_logo.png 存在
            const logoImg = `<img src="assets/scnu_logo.png" class="scnu-logo" alt="SCNU Logo">`;
            currentSlideElement.insertAdjacentHTML('beforeend', logoImg);

            // --- 注入 2: 页码 (右下角) ---
            const pageNumDiv = `<div class="slide-page-number">${slideIndex}</div>`;
            currentSlideElement.insertAdjacentHTML('beforeend', pageNumDiv);
            
            // --- [新增] 注入 3: 返回目录按钮 (左下角) ---
            // 逻辑：只有 Slide 3 及以后的页面才显示
            if (slideIndex > 2) {
                const backBtn = `
                    <a href="#slide2" class="back-to-dir-btn" title="Back to Directory">
                        <i class="fa-solid fa-list-ul"></i>
                    </a>
                `;
                currentSlideElement.insertAdjacentHTML('beforeend', backBtn);
            }
            
            slideIndex++;
            
        } catch (e) {
            console.error("加载异常:", e);
            keepLoading = false;
        }
    }

    // 4. 重新渲染公式
    if (window.MathJax) {
        window.MathJax.typesetPromise();
    }

    // 5. 通知脚本初始化
    const event = new Event('slidesLoaded');
    document.dispatchEvent(event);
}

loadSlides();