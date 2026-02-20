// 肖像照生成服务 - 前端逻辑

// 全局状态
let currentCode = '';
let selectedFile = null;
let remainingCount = 0;
let isGenerating = false;  // 标记是否正在生成

// 页面关闭前警告（生成中）
window.addEventListener('beforeunload', function(e) {
    if (isGenerating) {
        e.preventDefault();
        e.returnValue = '图片正在生成中，确定要离开吗？生成将中断。';
        return e.returnValue;
    }
});

// 更新背景色标签（根据背景类型显示不同文字）
function updateColorLabel() {
    const background = document.querySelector('input[name="background"]:checked').value;
    const colorLabel = document.querySelector('#colorOptions .form-label');
    if (colorLabel) {
        colorLabel.textContent = background === 'solid' ? '选择纯色背景色' : '选择影棚色调';
    }
}

// 根据性别更新服装选项
function updateClothingOptions() {
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const clothingSelect = document.getElementById('clothingSelect');

    // 定义男女服装选项
    const clothingOptions = {
        male: [
            { value: 'business_suit', text: '商务西装' },
            { value: 'casual_blazer', text: '休闲西装' },
            { value: 'casual_pants', text: '休闲装' },
            { value: 'casual_shirt', text: '休闲衬衫' },
            { value: 'turtleneck', text: '高领毛衣' },
            { value: 'tshirt', text: '简约T恤' },
            { value: 'doctoral_gown', text: '博士学位服' },
            { value: 'keep_original', text: '和原图保持一致' }
        ],
        female: [
            { value: 'business_suit', text: '商务西装套装' },
            { value: 'casual_blazer', text: '休闲西装外套' },
            { value: 'casual_pants', text: '休闲装' },
            { value: 'casual_shirt', text: '休闲衬衫' },
            { value: 'turtleneck', text: '高领毛衣' },
            { value: 'tshirt', text: '简约T恤' },
            { value: 'doctoral_gown', text: '博士学位服' },
            { value: 'keep_original', text: '和原图保持一致' }
        ]
    };

    // 保存当前选中的值
    const currentValue = clothingSelect.value;

    // 清空选项
    clothingSelect.innerHTML = '';

    // 添加新选项
    const options = clothingOptions[gender] || clothingOptions.male;
    options.forEach(option => {
        const optElement = document.createElement('option');
        optElement.value = option.value;
        optElement.textContent = option.text;
        clothingSelect.appendChild(optElement);
    });

    // 尝试恢复之前选中的值，如果不存在则选择第一个
    const optionExists = Array.from(clothingSelect.options).some(opt => opt.value === currentValue);
    clothingSelect.value = optionExists ? currentValue : 'business_suit';
}

// DOM 元素
const codeInput = document.getElementById('codeInput');
const codeError = document.getElementById('codeError');
const verifyError = document.getElementById('verifyError');
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const remainingCountSpan = document.getElementById('remainingCount');
const step2Error = document.getElementById('step2Error');
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadPlaceholder = document.getElementById('uploadPlaceholder');
const previewImage = document.getElementById('previewImage');
const generateBtn = document.getElementById('generateBtn');
const progressArea = document.getElementById('progressArea');
const resultImage = document.getElementById('resultImage');
const downloadLink = document.getElementById('downloadLink');

// 验证码输入自动转大写
codeInput.addEventListener('input', function() {
    this.value = this.value.toUpperCase();
    codeError.textContent = '';
    verifyError.style.display = 'none';
});

// 验证码
async function verifyCode() {
    const code = codeInput.value.trim();

    if (!code) {
        codeError.textContent = '请输入验证码';
        return;
    }

    if (code.length !== 8) {
        codeError.textContent = '验证码应为8位';
        return;
    }

    try {
        // 显示验证中状态
        verifyError.style.display = 'none';
        const verifyBtn = document.getElementById('verifyBtn');
        verifyBtn.disabled = true;
        verifyBtn.textContent = '验证中...';

        const response = await fetch('/api/verify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (data.success) {
            currentCode = code;
            remainingCount = data.remaining;
            remainingCountSpan.textContent = remainingCount;
            showStep2();
        } else {
            verifyError.textContent = data.message;
            verifyError.style.display = 'block';
        }
    } catch (error) {
        verifyError.textContent = '网络错误，请检查连接后重试';
        verifyError.style.display = 'block';
        console.error(error);
    } finally {
        const verifyBtn = document.getElementById('verifyBtn');
        verifyBtn.disabled = false;
        verifyBtn.textContent = '验证并开始';
    }
}

// 返回步骤1
function backToStep1() {
    step2.style.display = 'none';
    step1.style.display = 'block';
    codeInput.value = '';
    codeError.textContent = '';
    verifyError.style.display = 'none';
    currentCode = '';
    selectedFile = null;
    remainingCount = 0;
}

// 显示步骤2
function showStep2() {
    step1.style.display = 'none';
    step2.style.display = 'block';
    step2Error.style.display = 'none';

    // 检查剩余次数
    if (remainingCount <= 0) {
        step2Error.textContent = '⚠️ 此验证码的使用次数已用完，请更换验证码';
        step2Error.style.display = 'block';
        generateBtn.disabled = true;
    }
}

// 返回步骤2
function resetToStep2() {
    // 检查剩余次数
    if (remainingCount <= 0) {
        alert('⚠️ 额度已用完！\\n\\n此验证码的使用次数已全部用完，如需继续使用，请更换新的验证码。');
        // 返回步骤1让用户输入新验证码
        backToStep1();
        return;
    }

    step3.style.display = 'none';
    step2.style.display = 'block';
    resultImage.src = '';
    selectedFile = null;
    previewImage.style.display = 'none';
    uploadPlaceholder.style.display = 'block';
    generateBtn.disabled = true;
    step2Error.style.display = 'none';

    // 更新剩余次数
    fetch(`/api/status/${currentCode}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                remainingCount = data.remaining;
                remainingCountSpan.textContent = remainingCount;

                if (remainingCount <= 0) {
                    alert('⚠️ 额度已用完！\\n\\n此验证码的使用次数已全部用完，如需继续使用，请更换新的验证码。');
                    backToStep1();
                }
            }
        });
}

// 文件上传处理
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
});

function handleFile(file) {
    // 验证文件类型
    const allowedTypes = ['image/png', 'image/jpeg', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        step2Error.textContent = '⚠️ 只支持 PNG、JPG、WEBP 格式的图片';
        step2Error.style.display = 'block';
        return;
    }

    // 验证��件大小 (5MB)
    const maxSize = 5 * 1024 * 1024; // 5MB
    if (file.size > maxSize) {
        const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
        step2Error.textContent = `⚠️ 图片大小不能超过5MB，当前文件为 ${sizeMB}MB`;
        step2Error.style.display = 'block';
        return;
    }

    // 清除之前的错误信息
    step2Error.style.display = 'none';

    selectedFile = file;

    // 显示预览
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        previewImage.style.display = 'block';
        uploadPlaceholder.style.display = 'none';
        generateBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

// 生成肖像
async function generatePortrait() {
    if (!selectedFile) {
        step2Error.textContent = '⚠️ 请先上传照片';
        step2Error.style.display = 'block';
        return;
    }

    if (remainingCount <= 0) {
        step2Error.textContent = '⚠️ 此验证码的使用次数已用完，请更换验证码';
        step2Error.style.display = 'block';
        return;
    }

    // 获取选中的配置
    const gender = document.querySelector('input[name="gender"]:checked').value;
    const clothing = document.getElementById('clothingSelect').value;
    const angle = document.querySelector('input[name="angle"]:checked').value;
    const background = document.querySelector('input[name="background"]:checked').value;
    const bgColor = document.querySelector('input[name="bgColor"]:checked')?.value || 'white';
    const beautify = 'yes';  // 默认启用轻微美颜

    // 显示进度，隐藏错误
    step2Error.style.display = 'none';
    generateBtn.disabled = true;
    progressArea.style.display = 'block';
    isGenerating = true;  // 标记开始生成

    // 更新进度提示文字 - 警告不要关闭窗口
    const progressMessage = progressArea.querySelector('p');
    if (progressMessage) {
        progressMessage.innerHTML = '⏳ <strong>AI 正在生成图片，请勿关闭窗口！</strong><br><small>这可能需要 1-2 分钟，请耐心等待...</small>';
    }

    // 准备表单数据
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('code', currentCode);
    formData.append('style', 'portrait');  // 固定使用 portrait 风格
    formData.append('gender', gender);
    formData.append('clothing', clothing);
    formData.append('angle', angle);
    formData.append('background', background);
    formData.append('bgColor', bgColor);
    formData.append('beautify', beautify);

    // 创建超时 Promise (150秒超时)
    const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => {
            reject(new Error('timeout: 生成超时，图片处理需要较长时间，请稍后重试或联系客服'));
        }, 150000);
    });

    try {
        // 使用 Promise.race 实现超时控制
        const response = await Promise.race([
            fetch('/api/upload', {
                method: 'POST',
                body: formData
            }),
            timeoutPromise
        ]);

        console.log('[API] 响应状态:', response.status);
        console.log('[API] 响应类型:', response.headers.get('content-type'));

        // 检查响应是否是 JSON
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            // 服务器返回了 HTML 错误页面
            const text = await response.text();
            console.error('[API] 服务器返回非 JSON 响应:', text.substring(0, 500));
            step2Error.textContent = '⚠️ 服务器错误，请联系管理员';
            step2Error.style.display = 'block';
            generateBtn.disabled = false;
            return;
        }

        const data = await response.json();

        console.log('[API] 响应数据:', data);

        if (data.success) {
            // 更新剩余次数
            remainingCount = data.remaining;
            remainingCountSpan.textContent = remainingCount;

            // 显示结果
            resultImage.src = data.result_url;

            // 添加加载错误处理
            resultImage.onerror = function() {
                console.error('[Result] 图片加载失败:', data.result_url);
                step2Error.textContent = '⚠️ 图片加载失败，请联系客服或重试';
                step2Error.style.display = 'block';
                generateBtn.disabled = false;
                step3.style.display = 'none';
                step2.style.display = 'block';
            };

            // 加载成功后移除错误处理
            resultImage.onload = function() {
                console.log('[Result] 图片加载成功');
            };

            // 设置下载链接（使用时间戳作为文件名）
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            downloadLink.href = data.result_url;
            downloadLink.download = `portrait-${timestamp}.png`;

            // 根据剩余次数显示不同提示
            const stepHeader = step3.querySelector('.step-header');
            if (stepHeader) {
                if (remainingCount > 0) {
                    stepHeader.querySelector('.text-success').innerHTML = `✓ 生成成功 (剩余 ${remainingCount} 次)`;
                } else {
                    stepHeader.querySelector('.text-success').innerHTML = `✓ 生成完成 <small class="text-warning">(额度已用完)</small>`;
                }
            }

            step2.style.display = 'none';
            step3.style.display = 'block';
        } else {
            step2Error.textContent = '⚠️ ' + (data.message || '生成失败，请重试');
            step2Error.style.display = 'block';
            generateBtn.disabled = false;
        }
    } catch (error) {
        console.error('[API] 请求异常:', error);
        let errorMsg = '⚠️ 网络错误，请检查连接后重试';
        let isTimeout = false;
        let isConnectionError = false;

        // 详细的错误分类
        if (error.name === 'TypeError' && error.message === 'Failed to fetch') {
            errorMsg = '⚠️ 无法连接到服务器，请检查网络或稍后重试';
            isConnectionError = true;
        } else if (error.message) {
            // 检查是否是超时错误
            if (error.message.includes('超时') || error.message.includes('timeout')) {
                errorMsg = '⚠️ 请求超时，服务器响应时间过长，请稍后重试';
                isTimeout = true;
            }
            // 检查是否是连接错误
            else if (error.message.includes('连接') || error.message.includes('Connection')) {
                errorMsg = '⚠️ 连接失败，请检查网络设置或代理配置';
                isConnectionError = true;
            }
            // 检查是否是断路器错误
            else if (error.message.includes('断路器') || error.message.includes('暂时不可用')) {
                errorMsg = '⚠️ 服务暂时不可用（断路器保护），请稍后重试';
            }
            // 检查是否是代理错误
            else if (error.message.includes('代理') || error.message.includes('Proxy')) {
                errorMsg = '⚠️ 代理连接失败，请检查代理配置';
            }
            // 其他错误
            else {
                errorMsg = `⚠️ 请求失败: ${error.message}`;
            }
        }

        step2Error.textContent = errorMsg;
        step2Error.style.display = 'block';
        generateBtn.disabled = false;

        // 根据错误类型添加不同的样式
        if (isTimeout) {
            step2Error.style.color = '#f59e0b'; // 橙色 - 警告
        } else if (isConnectionError) {
            step2Error.style.color = '#ef4444'; // 红色 - 错误
        } else {
            step2Error.style.color = '#3b82f6'; // 蓝色 - 信息
        }
    } finally {
        progressArea.style.display = 'none';
        isGenerating = false;  // 生成完成或出错
    }
}

// 回车键验证
codeInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        verifyCode();
    }
});

// 页面加载完成
document.addEventListener('DOMContentLoaded', () => {
    console.log('肖像照生成服务已加载');
});
