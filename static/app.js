/**
 * Hybrid Quiz Solver - Client Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const quizForm = document.getElementById('quizForm');
  const urlInput = document.getElementById('quizUrl');
  const secretInput = document.getElementById('quizSecret');
  const emailInput = document.getElementById('quizEmail');
  const submitBtn = document.getElementById('submitBtn');
  const btnText = document.getElementById('btnText');
  const btnSpinner = document.getElementById('btnSpinner');

  const codeDisplay = document.getElementById('codeDisplay');
  const copyBtn = document.getElementById('copyBtn');
  const codeTabs = document.querySelectorAll('.code-tab');

  const serverStatus = document.getElementById('serverStatus');
  const statusDot = document.getElementById('statusDot');
  const uptimeDisplay = document.getElementById('uptimeDisplay');
  const activeModelDisplay = document.getElementById('activeModelDisplay');

  let currentLanguage = 'curl';

  // Real-time cURL / Code generator
  function updateCodeSnippet() {
    const url = urlInput.value.trim() || 'https://quiz-url.com/q1.html';
    const secret = secretInput.value.trim() || 'your_secret_key';
    const email = emailInput.value.trim() || 'your_email@example.com';
    const origin = window.location.origin || 'http://localhost:8000';

    const payload = {
      email: email,
      secret: secret,
      url: url
    };

    let snippet = '';

    if (currentLanguage === 'curl') {
      snippet = `curl -X POST "${origin}/quiz" \\
  -H "Content-Type: application/json" \\
  -d '${JSON.stringify(payload, null, 2)}'`;
    } else if (currentLanguage === 'python') {
      snippet = `import requests

url = "${origin}/quiz"
payload = {
    "email": "${email}",
    "secret": "${secret}",
    "url": "${url}"
}

response = requests.post(url, json=payload)
print(response.status_code, response.json())`;
    } else if (currentLanguage === 'javascript') {
      snippet = `const response = await fetch('${origin}/quiz', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(${JSON.stringify(payload, null, 4)})
});

const data = await response.json();
console.log(data);`;
    }

    if (codeDisplay) {
      codeDisplay.textContent = snippet;
    }
  }

  // Event listeners for real-time snippet updates
  [urlInput, secretInput, emailInput].forEach(input => {
    if (input) {
      input.addEventListener('input', updateCodeSnippet);
    }
  });

  // Code Tab Switching
  codeTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      codeTabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      currentLanguage = tab.dataset.lang;
      updateCodeSnippet();
    });
  });

  // Copy to Clipboard
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      if (!codeDisplay) return;
      try {
        await navigator.clipboard.writeText(codeDisplay.textContent);
        const originalText = copyBtn.innerHTML;
        copyBtn.innerHTML = '<span>✓ Copied!</span>';
        setTimeout(() => {
          copyBtn.innerHTML = originalText;
        }, 2000);
      } catch (err) {
        showToast('Failed to copy to clipboard', 'error');
      }
    });
  }

  // Toast Notification System
  function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icon = type === 'success' ? '✓' : '⚠️';
    toast.innerHTML = `<span style="font-size: 1.1rem;">${icon}</span> <span>${message}</span>`;
    
    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
  }

  // Live Server Health & Uptime Poller
  async function checkServerHealth() {
    try {
      const response = await fetch('/healthz');
      if (response.ok) {
        const data = await response.json();
        if (serverStatus) serverStatus.textContent = 'Server Online';
        if (statusDot) {
          statusDot.style.backgroundColor = '#10b981';
          statusDot.style.boxShadow = '0 0 8px #10b981';
        }
        if (uptimeDisplay) {
          const uptimeSec = data.uptime_seconds || 0;
          const mins = Math.floor(uptimeSec / 60);
          const secs = uptimeSec % 60;
          uptimeDisplay.textContent = `${mins}m ${secs}s`;
        }
      } else {
        throw new Error('Unhealthy status');
      }
    } catch (err) {
      if (serverStatus) serverStatus.textContent = 'Disconnected';
      if (statusDot) {
        statusDot.style.backgroundColor = '#f43f5e';
        statusDot.style.boxShadow = '0 0 8px #f43f5e';
      }
      if (uptimeDisplay) uptimeDisplay.textContent = 'Offline';
    }
  }

  // Initial health check & recurring poll
  checkServerHealth();
  setInterval(checkServerHealth, 5000);

  // Form Submission
  if (quizForm) {
    quizForm.addEventListener('submit', async (e) => {
      e.preventDefault();

      const url = urlInput.value.trim();
      const secret = secretInput.value.trim();
      const email = emailInput.value.trim();

      if (!url) {
        showToast('Please enter a valid Quiz URL', 'error');
        urlInput.focus();
        return;
      }

      if (!secret) {
        showToast('Please enter your TDS Secret key', 'error');
        secretInput.focus();
        return;
      }

      // Set Loading State
      if (submitBtn) submitBtn.disabled = true;
      if (btnText) btnText.textContent = 'Starting Task...';

      try {
        const response = await fetch('/quiz', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            url: url,
            secret: secret,
            email: email || undefined
          })
        });

        const data = await response.json();

        if (response.ok) {
          showToast('✓ Quiz Task Dispatched! Agent is solving in the background.', 'success');
        } else {
          const errorMsg = data.detail || 'Failed to dispatch quiz task';
          showToast(`Error (${response.status}): ${errorMsg}`, 'error');
        }
      } catch (err) {
        showToast(`Network Error: ${err.message}`, 'error');
      } finally {
        if (submitBtn) submitBtn.disabled = false;
        if (btnText) btnText.textContent = 'Dispatch Quiz Task';
      }
    });
  }

  // Initialize snippet on page load
  updateCodeSnippet();
});
