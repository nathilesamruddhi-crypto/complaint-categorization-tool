// ===== PAGE NAVIGATION =====
function navigateToAnalysis() {
    const landingPage = document.getElementById('landingPage');
    const analysisPage = document.getElementById('analysisPage');
    
    landingPage.classList.remove('active');
    setTimeout(() => {
        landingPage.style.display = 'none';
        analysisPage.classList.add('active');
        analysisPage.style.display = 'flex';
    }, 300);
}

function navigateToLanding() {
    const landingPage = document.getElementById('landingPage');
    const analysisPage = document.getElementById('analysisPage');
    
    analysisPage.classList.remove('active');
    setTimeout(() => {
        analysisPage.style.display = 'none';
        landingPage.style.display = 'flex';
        landingPage.classList.add('active');
    }, 300);
}

// ===== VOICE RECOGNITION =====
let recognition = null;
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
}

// ===== HISTORY MANAGEMENT =====
let predictionHistory = JSON.parse(localStorage.getItem('complaintHistory') || '[]');

function saveHistory() {
    localStorage.setItem('complaintHistory', JSON.stringify(predictionHistory.slice(0, 10)));
}

function addToHistory(complaint, category) {
    predictionHistory.unshift({
        complaint: complaint.substring(0, 80),
        category: category,
        timestamp: new Date().toLocaleTimeString()
    });
    if (predictionHistory.length > 10) predictionHistory.pop();
    saveHistory();
    displayHistory();
    updateHistoryCount();
}

function updateHistoryCount() {
    const countEl = document.getElementById('historyCount');
    if (countEl) {
        countEl.textContent = predictionHistory.length;
    }
}

function displayHistory() {
    const historyList = document.getElementById('historyList');
    if (!historyList) return;
    
    if (predictionHistory.length === 0) {
        historyList.innerHTML = '<p style="color:#94a3b8; text-align:center; padding:20px; font-size:13px;">No predictions yet</p>';
        return;
    }
    
    historyList.innerHTML = predictionHistory.map(item => `
        <div class="history-item" onclick="loadFromHistory('${item.complaint.replace(/'/g, "\\'")}');">
            <div class="history-complaint">${escapeHtml(item.complaint)}</div>
            <div class="history-meta">
                <span class="history-category">${item.category}</span>
                <span class="history-time">${item.timestamp}</span>
            </div>
        </div>
    `).join('');
}

function loadFromHistory(complaint) {
    document.getElementById('complaint').value = complaint;
    document.getElementById('complaint').focus();
    document.getElementById('charCount').textContent = complaint.length;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ===== COMPLAINT ANALYSIS =====
async function predictComplaint() {
    const complaint = document.getElementById("complaint").value;
    const loading = document.getElementById("loading");
    const resultBox = document.getElementById("resultBox");
    const resultContent = document.getElementById("resultContent");

    if (complaint.trim() === "") {
        showNotification("Please enter a complaint", "warning");
        return;
    }

    loading.style.display = "flex";
    resultBox.style.display = "none";
    resultBox.classList.remove('show');

    try {
        const apiBase = window.location.protocol === "file:" ? "http://127.0.0.1:5000" : "";
        const response = await fetch(`${apiBase}/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ complaint: complaint })
        });

        const data = await response.json();
        loading.style.display = "none";

        if (data.success) {
            displayResult(data, complaint);
            addToHistory(complaint, data.category);
            showNotification("Prediction complete!", "success");
        } else {
            resultContent.innerHTML = `<div style="color:#ef4444; text-align:center; padding:20px;">❌ Prediction Failed: ${data.error}</div>`;
            resultBox.classList.add('show');
            resultBox.style.display = "block";
            showNotification("Prediction failed", "error");
        }
    } catch (error) {
        loading.style.display = "none";
        resultContent.innerHTML = `<div style="color:#ef4444; text-align:center; padding:20px;">⚠️ Cannot connect to backend. Make sure Flask server is running on port 5000.</div>`;
        resultBox.classList.add('show');
        resultBox.style.display = "block";
        showNotification("Connection Error", "error");
        console.error(error);
    }
}

function displayResult(data, complaint) {
    const resultBox = document.getElementById("resultBox");
    const resultContent = document.getElementById("resultContent");
    const category = data.category;

    // Category color mapping
    const categoryGradients = {
        'Account': 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
        'Billing': 'linear-gradient(135deg, #f97316 0%, #ec4899 100%)',
        'Delivery': 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)',
        'Product': 'linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)',
        'Service': 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)',
        'Technical': 'linear-gradient(135deg, #06b6d4 0%, #10b981 100%)'
    };
    
    const gradient = categoryGradients[category] || 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)';

    resultContent.innerHTML = `
        <div class="result-box prediction-only">
            <div style="text-align: center;">
                <div class="result-label">Prediction</div>
                <div class="category-badge" style="background: ${gradient};">
                    <i class="fas fa-tag"></i> ${category}
                </div>
            </div>
        </div>
    `;

    resultBox.classList.add('show');
    resultBox.style.display = "block";
    resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    return;
    
    let probHtml = '<div class="probabilities-section"><div class="prob-header">📊 Probability Distribution</div>';
    for (const [cat, prob] of Object.entries(probabilities)) {
        probHtml += `
            <div class="prob-item">
                <div class="prob-category">
                    <span>${cat}</span>
                    <span>${prob.toFixed(1)}%</span>
                </div>
                <div class="prob-bar-bg">
                    <div class="prob-bar-fill" style="width: 0%; --target-width: ${prob}%;"></div>
                </div>
            </div>
        `;
    }
    probHtml += '</div>';
    
    resultContent.innerHTML = `
        <div class="result-box">
            <div style="text-align: center;">
                <div class="category-badge" style="background: ${gradient};">
                    <i class="fas fa-tag"></i> ${category}
                </div>
                <div class="confidence-section">
                    <div class="confidence-label">🤖 AI Confidence Score</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: 0%;"></div>
                    </div>
                    <div class="confidence-value">${confidence}% Accurate</div>
                </div>
                ${probHtml}
                <div style="margin-top: 20px; font-size: 12px; color: #64748b;">
                    <i class="fas fa-info-circle"></i> Based on Logistic Regression model with TF-IDF features
                </div>
            </div>
        </div>
    `;
    
    resultBox.classList.add('show');
    resultBox.style.display = "block";
    
    // Animate bars
    setTimeout(() => {
        const confFill = resultContent.querySelector('.confidence-fill');
        const probBars = resultContent.querySelectorAll('.prob-bar-fill');
        
        if (confFill) {
            confFill.style.width = confidence + '%';
        }
        
        probBars.forEach((bar, index) => {
            setTimeout(() => {
                const targetWidth = parseFloat(bar.parentElement.querySelector('span:last-child').textContent);
                bar.style.width = targetWidth + '%';
            }, 100 * (index + 1));
        });
    }, 50);
    
    resultBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    
    notification.className = `notification ${type}`;
    notification.innerHTML = `<i class="fas ${icons[type]}"></i> ${message}`;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideInRight 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// ===== EVENT LISTENERS =====

// Voice input
if (recognition && document.getElementById('voiceBtn')) {
    document.getElementById('voiceBtn').addEventListener('click', () => {
        recognition.start();
        document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone-slash"></i>';
        showNotification("Listening... Speak now", "info");
    });
    
    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById('complaint').value = transcript;
        document.getElementById('charCount').textContent = transcript.length;
        document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone"></i>';
        showNotification("Voice input added!", "success");
    };
    
    recognition.onerror = () => {
        document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone"></i>';
        showNotification("Voice recognition failed", "error");
    };
    
    recognition.onend = () => {
        document.getElementById('voiceBtn').innerHTML = '<i class="fas fa-microphone"></i>';
    };
}

// Example chips
document.querySelectorAll('.example-chip').forEach(chip => {
    chip.addEventListener('click', () => {
        const text = chip.getAttribute('data-text');
        document.getElementById('complaint').value = text;
        document.getElementById('charCount').textContent = text.length;
        document.getElementById('complaint').focus();
    });
});

// Textarea character count
const complaintsTextarea = document.getElementById('complaint');
if (complaintsTextarea) {
    complaintsTextarea.addEventListener('input', () => {
        const count = complaintsTextarea.value.length;
        const charCount = document.getElementById('charCount');
        if (charCount) {
            charCount.textContent = count;
        }
    });
}

// Clear button
document.getElementById('clearBtn')?.addEventListener('click', () => {
    document.getElementById('complaint').value = '';
    document.getElementById('charCount').textContent = '0';
    document.getElementById('resultBox').style.display = 'none';
    showNotification("Cleared", "info");
});

// Clear history
document.getElementById('clearHistoryBtn')?.addEventListener('click', () => {
    predictionHistory = [];
    saveHistory();
    displayHistory();
    updateHistoryCount();
    showNotification("History cleared", "info");
});

// Predict button
document.getElementById('predictBtn')?.addEventListener('click', predictComplaint);

// Allow Enter+Ctrl to submit
document.getElementById('complaint')?.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'Enter') {
        predictComplaint();
    }
});

// Initialize
displayHistory();
updateHistoryCount();

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
