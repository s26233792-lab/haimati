// 肖像照生成服务 - 前端逻辑

// 全局状态
let currentCode = '';
let selectedFile = null;
let remainingCount = 0;

// DOM 元素
const codeInput = document.getElementById('codeInput');
const codeError = document.getElementById('codeError');
const step1 = document.getElementById('step1');
const step2 = document.getElementById('step2');
const step3 = document.getElementById('step3');
const remainingCountSpan = document.getElementById('remainingCount');
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
});

// 验证码
async function verifyCode() {
    const code = codeInput.value.trim();

    if (!code) {
        codeError.textContent = '请输入验证码';
        return;
    }

    if (code.length < 6 || code.length > 10) {
        codeError.textContent = '验证码应为6-10位';
        return;
    }

    try {
        codeError.textContent = '验证中...';

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
            codeError.textContent = data.message;
        }
    } catch (error) {
        codeError.textContent = '网络错误，请重试';
        console.error(error);
    }
}

// 显示步骤2
function showStep2() {
    step1.style.display = 'none';
    step2.style.display = 'block';
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

    // 更新剩余次数
    fetch(`/api/status/${currentCode}`)
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                remainingCount = data.remaining;
                remainingCountSpan.textContent = remainingCount;

                if (remainingCount <= 0) {
                    generateBtn.disabled = true;
                    alert('您的使用次数已用完');
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
        alert('只支持 PNG、JPG、WEBP 格式的图片');
        return;
    }

    // 验证文件大小 (16MB)
    if (file.size > 16 * 1024 * 1024) {
        alert('图片大小不能超过16MB');
        return;
    }

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
        alert('请先上传图片');
        return;
    }

    if (remainingCount <= 0) {
        alert('您的使用次数已用完');
        return;
    }

    // 获取选中的配置
    const clothing = document.getElementById('clothingSelect').value;
    const background = document.querySelector('input[name="background"]:checked').value;

    // 显示进度
    generateBtn.disabled = true;
    progressArea.style.display = 'block';

    // 准备表单数据
    const formData = new FormData();
    formData.append('image', selectedFile);
    formData.append('code', currentCode);
    formData.append('style', 'portrait');  // 固定使用 portrait 风格
    formData.append('clothing', clothing);
    formData.append('background', background);

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
            alert(data.message || '生成失败，请重试');
            generateBtn.disabled = false;
        }
    } catch (error) {
        alert('网络错误，请重试');
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
