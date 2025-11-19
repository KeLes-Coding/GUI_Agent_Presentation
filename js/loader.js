async function loadSlides() {
    const container = document.getElementById('presentation-deck');
    let slideIndex = 1;
    let keepLoading = true;

    console.log("开始自动加载幻灯片...");

    while (keepLoading) {
        try {
            // 1. 请求文件
            const response = await fetch(`slides/slide${slideIndex}.html`);
            
            if (!response.ok) {
                console.log(`检测到 slide${slideIndex}.html 不存在，加载结束。共加载 ${slideIndex - 1} 页。`);
                keepLoading = false;
                break;
            }
            
            const html = await response.text();
            
            // 2. 插入 Slide HTML
            container.insertAdjacentHTML('beforeend', html);

            // 3. 【关键修改】获取刚才插入的那个 slide 元素
            const currentSlideElement = container.lastElementChild;

            // 4. 【关键修改】在卡片内部插入页码数字
            // 我们创建一个 div，不仅包含数字，还可以包含 "Page x" 这样的前缀，这里只放数字
            const pageNumDiv = `<div class="slide-page-number">${slideIndex}</div>`;
            currentSlideElement.insertAdjacentHTML('beforeend', pageNumDiv);
            
            // 准备下一页
            slideIndex++;
            
        } catch (e) {
            console.error("加载过程中发生异常:", e);
            keepLoading = false;
        }
    }

    // 【新增】通知 MathJax 重新寻找并渲染页面上的公式
    if (window.MathJax) {
        window.MathJax.typesetPromise();
    }

    // 通知 script.js 初始化交互逻辑
    const event = new Event('slidesLoaded');
    document.dispatchEvent(event);
}

// 执行加载
loadSlides();