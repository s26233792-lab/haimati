// 肖像照生成服务 - 前端逻辑

// 全局状态
let currentCode = '';
let selectedFile = null;
let remainingCount = 0;

// 更新背景色标签（根据背景类型显示不同文字）
function updateColorLabel() {
    const background = document.querySelector('input[name="background"]:checked').value;
    const colorLabel = document.querySelector('#colorOptions .form-label');
    if (colorLabel) {
        colorLabel.textContent = background === 'solid' ? '选择纯色背景色' : '选择影棚色调';
    }
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
                    generateBtn.disabled = true;
                    step2Error.textContent = '⚠️ 此验证码的使用次数已用完，请更换验证码';
                    step2Error.style.display = 'block';
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

    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        step2Error.textContent = '⚠️ 图片大小不能超过16MB';
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
    const clothing = document.getElementById('clothingSelect').value;
    const angle = document.querySelector('input[name="angle"]:checked').value;
    const background = document.querySelector('input[name="background"]:checked').value;
    const bgColor = document.querySelector('input[name="bgColor"]:checked')?.value || 'white';
    const beautify = 'yes';  // 默认启用轻微美颜

    // 显示进度，隐藏错误
    step2Error.style.display = 'none';
    generateBtn.disabled = true;
    progressArea.style.display = 'block';

    // 准备表单数据
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('code', currentCode);
    formData.append('style', 'portrait');  // 固定使用 portrait 风格
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

        const data = await response.json();

        if (data.success) {
            // 更新剩余次数
            remainingCount = data.remaining;
            remainingCountSpan.textContent = remainingCount;

            // 显示结果
            resultImage.src = data.result_url;

            // 设置下载链接（使用时间戳作为文件名）
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            downloadLink.href = data.result_url;
            downloadLink.download = `portrait-${timestamp}.png`;

            step2.style.display = 'none';
            step3.style.display = 'block';
        } else {
            step2Error.textContent = '⚠️ ' + (data.message || '生成失败，请重试');
            step2Error.style.display = 'block';
            generateBtn.disabled = false;
        }
    } catch (error) {
        step2Error.textContent = '⚠️ 网络错误，请检查连接后重试';
        step2Error.style.display = 'block';
        console.error(error);
        generateBtn.disabled = false;
    } finally {
        progressArea.style.display = 'none';
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
