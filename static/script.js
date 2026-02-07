/**
 * AI肖像馆 - 前端交互逻辑
 * 版本: 2.0 - UI/UX 全面升级
 */

// ==================== 全局状态 ====================
const state = {
    currentCode: '',
    selectedFile: null,
    remainingCount: 0,
    currentStep: 1,
    isGenerating: false
};

// ==================== DOM 元素缓存 ====================
const elements = {
    // 输入
    codeInput: document.getElementById('codeInput'),
    codeError: document.getElementById('codeError'),
    verifyError: document.getElementById('verifyError'),
    
    // 步骤
    step1: document.getElementById('step1'),
    step2: document.getElementById('step2'),
    step3: document.getElementById('step3'),
    stepIndicator: document.getElementById('stepIndicator'),
    
    // 计数和状态
    remainingCount: document.getElementById('remainingCount'),
    step2Error: document.getElementById('step2Error'),
    
    // 文件上传
    fileInput: document.getElementById('fileInput'),
    uploadArea: document.getElementById('uploadArea'),
    uploadPlaceholder: document.getElementById('uploadPlaceholder'),
    previewImage: document.getElementById('previewImage'),
    
    // 按钮
    verifyBtn: document.getElementById('verifyBtn'),
    verifyBtnIcon: document.getElementById('verifyBtnIcon'),
    generateBtn: document.getElementById('generateBtn'),
    generateBtnText: document.getElementById('generateBtnText'),
    generateBtnIcon: document.getElementById('generateBtnIcon'),
    
    // 进度
    progressArea: document.getElementById('progressArea'),
    progressText: document.getElementById('progressText'),
    progressDots: document.getElementById('progressDots'),
    
    // 结果
    resultImage: document.getElementById('resultImage'),
    downloadLink: document.getElementById('downloadLink'),
    
    // Toast
    toastContainer: document.getElementById('toastContainer')
};

// ==================== Toast 通知系统 ====================
const Toast = {
    show(message, type = 'info', duration = 3000) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        const titles = {
            success: '成功',
            error: '错误',
            warning: '警告',
            info: '提示'
        };
        
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <span class="toast-icon">${icons[type]}</span>
            <div class="toast-content">
                <div class="toast-title">${titles[type]}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        elements.toastContainer.appendChild(toast);
        
        // 自动关闭
        if (duration > 0) {
            setTimeout(() => {
                toast.classList.add('hiding');
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        return toast;
    },
    
    success(message, duration) {
        return this.show(message, 'success', duration);
    },
    
    error(message, duration) {
        return this.show(message, 'error', duration);
    },
    
    warning(message, duration) {
        return this.show(message, 'warning', duration);
    },
    
    info(message, duration) {
        return this.show(message, 'info', duration);
    }
};

// ==================== 步骤指示器更新 ====================
function updateStepIndicator(step) {
    state.currentStep = step;
    const dots = elements.stepIndicator.querySelectorAll('.step-dot');
    
    dots.forEach((dot, index) => {
        const dotStep = index + 1;
        dot.classList.remove('active', 'completed');
        
        if (dotStep < step) {
            dot.classList.add('completed');
            dot.innerHTML = '✓';
        } else if (dotStep === step) {
            dot.classList.add('active');
            dot.innerHTML = dotStep;
        } else {
            dot.innerHTML = dotStep;
        }
    });
}

// ==================== 验证码输入处理 ====================
elements.codeInput.addEventListener('input', function() {
    // 自动转大写
    this.value = this.value.toUpperCase();
    // 清除错误信息
    elements.codeError.textContent = '';
    elements.verifyError.style.display = 'none';
    
    // 输入满8位自动验证（可选）
    if (this.value.length === 8) {
        elements.verifyBtn.focus();
    }
});

// 回车键验证
elements.codeInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        verifyCode();
    }
});

// ==================== 验证码验证 ====================
async function verifyCode() {
    const code = elements.codeInput.value.trim();
    
    // 验证输入
    if (!code) {
        elements.codeError.textContent = '请输入验证码';
        elements.codeInput.focus();
        shakeElement(elements.codeInput);
        return;
    }
    
    if (code.length !== 8) {
        elements.codeError.textContent = '验证码应为8位';
        shakeElement(elements.codeInput);
        return;
    }
    
    try {
        // 显示验证中状态
        elements.verifyError.style.display = 'none';
        setButtonLoading(elements.verifyBtn, true, '验证中...');
        
        const response = await fetch('/api/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code })
        });
        
        const data = await response.json();
        
        if (data.success) {
            state.currentCode = code;
            state.remainingCount = data.remaining;
            elements.remainingCount.textContent = state.remainingCount;
            
            Toast.success(`验证成功！剩余 ${data.remaining} 次生成机会`);
            showStep(2);
        } else {
            elements.verifyError.textContent = data.message;
            elements.verifyError.style.display = 'block';
            Toast.error(data.message);
            shakeElement(elements.codeInput);
        }
    } catch (error) {
        console.error('验证错误:', error);
        elements.verifyError.textContent = '网络错误，请检查连接后重试';
        elements.verifyError.style.display = 'block';
        Toast.error('网络错误，请检查连接后重试');
    } finally {
        setButtonLoading(elements.verifyBtn, false, '验证并开始', '→');
    }
}

// ==================== 步骤切换 ====================
function showStep(step) {
    // 隐藏所有步骤
    elements.step1.style.display = 'none';
    elements.step2.style.display = 'none';
    elements.step3.style.display = 'none';
    
    // 显示目标步骤
    switch(step) {
        case 1:
            elements.step1.style.display = 'block';
            elements.codeInput.focus();
            break;
        case 2:
            elements.step2.style.display = 'block';
            elements.step2Error.style.display = 'none';
            
            // 检查剩余次数
            if (state.remainingCount <= 0) {
                elements.step2Error.textContent = '⚠️ 此验证码的使用次数已用完，请更换验证码';
                elements.step2Error.style.display = 'block';
                elements.generateBtn.disabled = true;
            }
            break;
        case 3:
            elements.step3.style.display = 'block';
            // 滚动到结果区域
            setTimeout(() => {
                elements.resultImage.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
            break;
    }
    
    updateStepIndicator(step);
}

// 返回步骤1
function backToStep1() {
    showStep(1);
    elements.codeInput.value = '';
    elements.codeError.textContent = '';
    elements.verifyError.style.display = 'none';
    state.currentCode = '';
    state.selectedFile = null;
    state.remainingCount = 0;
}

// 返回步骤2
function resetToStep2() {
    showStep(2);
    elements.resultImage.src = '';
    state.selectedFile = null;
    elements.previewImage.style.display = 'none';
    elements.uploadPlaceholder.style.display = 'block';
    elements.generateBtn.disabled = true;
    elements.step2Error.style.display = 'none';
    
    // 更新剩余次数
    fetch(`/api/status/${state.currentCode}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                state.remainingCount = data.remaining;
                elements.remainingCount.textContent = state.remainingCount;
                
                if (state.remainingCount <= 0) {
                    elements.generateBtn.disabled = true;
                    elements.step2Error.textContent = '⚠️ 此验证码的使用次数已用完，请更换验证码';
                    elements.step2Error.style.display = 'block';
                } else {
                    Toast.info(`剩余 ${data.remaining} 次生成机会`);
                }
            }
        })
        .catch(err => console.error('获取状态失败:', err));
}

// ==================== 文件上传处理 ====================
// 点击上传
elements.uploadArea.addEventListener('click', () => {
    if (!state.isGenerating) {
        elements.fileInput.click();
    }
});

// 拖拽上传
elements.uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    if (!state.isGenerating) {
        elements.uploadArea.classList.add('dragover');
    }
});

elements.uploadArea.addEventListener('dragleave', () => {
    elements.uploadArea.classList.remove('dragover');
});

elements.uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    elements.uploadArea.classList.remove('dragover');
    
    if (state.isGenerating) return;
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

elements.fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

// 处理文件
function handleFile(file) {
    // 验证文件类型
    const allowedTypes = ['image/png', 'image/jpeg', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showError('只支持 PNG、JPG、WEBP 格式的图片');
        return;
    }
    
    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        showError('图片大小不能超过16MB');
        return;
    }
    
    // 清除错误
    elements.step2Error.style.display = 'none';
    
    state.selectedFile = file;
    
    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => {
        elements.previewImage.src = e.target.result;
        elements.previewImage.style.display = 'block';
        elements.uploadPlaceholder.style.display = 'none';
        elements.generateBtn.disabled = false;
        
        Toast.success('图片上传成功！');
    };
    reader.onerror = () => {
        Toast.error('图片读取失败，请重试');
    };
    reader.readAsDataURL(file);
}

// ==================== 背景色标签更新 ====================
function updateColorLabel() {
    const background = document.querySelector('input[name="background"]:checked').value;
    const colorLabel = document.querySelector('#colorOptions .form-label');
    if (colorLabel) {
        colorLabel.textContent = background === 'solid' ? '选择纯色背景色' : '选择影棚色调';
    }
}

// ==================== 生成肖像 ====================
async function generatePortrait() {
    if (!state.selectedFile) {
        showError('请先上传照片');
        return;
    }
    
    if (state.remainingCount <= 0) {
        showError('此验证码的使用次数已用完，请更换验证码');
        return;
    }
    
    // 获取配置
    const clothing = document.getElementById('clothingSelect').value;
    const angle = document.querySelector('input[name="angle"]:checked').value;
    const background = document.querySelector('input[name="background"]:checked').value;
    const bgColor = document.querySelector('input[name="bgColor"]:checked')?.value || 'white';
    const beautifyCheckbox = document.getElementById('beautifyCheckbox');
    const beautify = beautifyCheckbox.checked ? 'yes' : 'no';
    
    console.log('[配置] 服装:', clothing, '角度:', angle, '背景:', background, '颜色:', bgColor, '美颜:', beautify);
    
    // 设置生成状态
    state.isGenerating = true;
    elements.step2Error.style.display = 'none';
    elements.generateBtn.disabled = true;
    elements.progressArea.style.display = 'block';
    
    // 进度文字动画
    startProgressAnimation();
    
    // 准备表单数据
    const formData = new FormData();
    formData.append('image', state.selectedFile);
    formData.append('code', state.currentCode);
    formData.append('style', 'portrait');
    formData.append('clothing', clothing);
    formData.append('angle', angle);
    formData.append('background', background);
    formData.append('bgColor', bgColor);
    formData.append('beautify', beautify);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        console.log('[API] 响应状态:', response.status);
        
        // 检查响应类型
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('[API] 服务器返回非 JSON 响应:', text.substring(0, 500));
            throw new Error('服务器返回格式错误，请联系管理员');
        }
        
        const data = await response.json();
        console.log('[API] 响应数据:', data);
        
        if (data.success) {
            // 更新状态
            state.remainingCount = data.remaining;
            elements.remainingCount.textContent = state.remainingCount;
            state.isGenerating = false;
            
            // 显示结果
            elements.resultImage.src = data.result_url;
            
            // 设置下载链接
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            elements.downloadLink.href = data.result_url;
            elements.downloadLink.download = `AI肖像-${timestamp}.png`;
            
            Toast.success('肖像生成成功！请下载保存');
            showStep(3);
        } else {
            throw new Error(data.message || '生成失败，请重试');
        }
    } catch (error) {
        console.error('[API] 请求异常:', error);
        state.isGenerating = false;
        
        let errorMsg = error.message || '网络错误，请检查连接后重试';
        
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            errorMsg = '无法连接到服务器，请检查网络或稍后重试';
        }
        
        showError(errorMsg);
        Toast.error(errorMsg);
        elements.generateBtn.disabled = false;
    } finally {
        elements.progressArea.style.display = 'none';
        stopProgressAnimation();
    }
}

// ==================== 进度动画 ====================
let progressInterval;
const progressMessages = [
    '正在分析照片特征',
    '正在调整光线和色彩',
    '正在生成专业肖像',
    '正在进行最终渲染',
    '即将完成...'
];

function startProgressAnimation() {
    let messageIndex = 0;
    elements.progressText.textContent = progressMessages[0];
    
    progressInterval = setInterval(() => {
        messageIndex = (messageIndex + 1) % progressMessages.length;
        elements.progressText.textContent = progressMessages[messageIndex];
        
        // 动态省略号
        let dots = '';
        const dotsInterval = setInterval(() => {
            dots = dots.length >= 3 ? '' : dots + '.';
            elements.progressDots.textContent = dots;
        }, 500);
        
        // 清理旧定时器
        if (messageIndex === 0) {
            clearInterval(dotsInterval);
        }
    }, 4000);
}

function stopProgressAnimation() {
    clearInterval(progressInterval);
}

// ==================== 工具函数 ====================

// 显示错误
function showError(message) {
    elements.step2Error.textContent = '⚠️ ' + message;
    elements.step2Error.style.display = 'block';
    elements.step2Error.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// 设置按钮加载状态
function setButtonLoading(btn, loading, text, icon = '') {
    btn.disabled = loading;
    
    const textSpan = btn.querySelector('span:first-child');
    const iconSpan = btn.querySelector('span:last-child');
    
    if (textSpan) textSpan.textContent = text;
    if (iconSpan && icon) iconSpan.textContent = icon;
    
    if (loading) {
        btn.classList.add('loading');
        btn.style.opacity = '0.8';
    } else {
        btn.classList.remove('loading');
        btn.style.opacity = '1';
    }
}

// 元素抖动动画（错误提示）
function shakeElement(element) {
    element.style.animation = 'shake 0.5s ease-in-out';
    setTimeout(() => {
        element.style.animation = '';
    }, 500);
}

// 添加抖动动画样式
const shakeStyle = document.createElement('style');
shakeStyle.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
`;
document.head.appendChild(shakeStyle);

// ==================== 页面加载完成 ====================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎨 AI肖像馆已加载');
    
    // 初始化步骤指示器
    updateStepIndicator(1);
    
    // 聚焦验证码输入框
    elements.codeInput.focus();
    
    // 页面可见性变化处理（防止后台运行时的问题）
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible' && state.isGenerating) {
            // 页面重新可见时检查状态
            console.log('页面重新可见，检查生成状态...');
        }
    });
    
    // 防止意外刷新导致数据丢失
    window.addEventListener('beforeunload', (e) => {
        if (state.isGenerating) {
            e.preventDefault();
            e.returnValue = '正在生成中，确定要离开吗？';
        }
    });
});

// ==================== 键盘快捷键 ====================
document.addEventListener('keydown', (e) => {
    // ESC 返回上一步（在步骤2和3时）
    if (e.key === 'Escape') {
        if (state.currentStep === 2 && !state.isGenerating) {
            backToStep1();
        } else if (state.currentStep === 3) {
            resetToStep2();
        }
    }
});
