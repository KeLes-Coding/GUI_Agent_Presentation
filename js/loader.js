async function loadSlides() {
    const container = document.getElementById('presentation-deck');
    // 定义你要加载的文件数量
    const totalSlides = 15; 

    for (let i = 1; i <= totalSlides; i++) {
        try {
            // 动态获取文件
            const response = await fetch(`slides/slide${i}.html`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const html = await response.text();
            
            // 将读取到的 HTML 字符串追加到容器中
            // 使用 insertAdjacentHTML 比 innerHTML += 更快，且不会破坏已有的事件绑定
            container.insertAdjacentHTML('beforeend', html);
            
        } catch (e) {
            console.error(`无法加载 slide${i}.html:`, e);
            container.insertAdjacentHTML('beforeend', `<div class="slide-container"><h1>加载失败: Slide ${i}</h1><p>${e.message}</p></div>`);
        }
    }

    // Slide 全部加载完毕后，我们需要通知 script.js 初始化翻页逻辑
    // 因为 script.js 之前运行的时候，页面里可能还是空的
    console.log("所有 Slides 加载完毕，初始化翻页控制...");
    
    // 触发一个自定义事件，通知 script.js
    const event = new Event('slidesLoaded');
    document.dispatchEvent(event);
}

// 页面加载时立即执行
loadSlides();