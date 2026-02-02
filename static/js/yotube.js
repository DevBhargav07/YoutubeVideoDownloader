// Progress Bar Controller
class ProgressBar {
    constructor() {
        this.container = $('#progress-container');
        this.bar = $('#progress-bar');
        this.percentage = $('#progress-percentage');
        this.status = $('#progress-status');
        this.currentProgress = 0;
        this.interval = null;
    }

    show() {
        this.container.addClass('active');
        this.reset();
    }

    hide() {
        this.container.removeClass('active');
    }

    reset() {
        this.currentProgress = 0;
        this.updateDisplay();
    }

    updateDisplay() {
        this.bar.css('width', this.currentProgress + '%');
        this.percentage.text(Math.floor(this.currentProgress) + '%');
    }

    setStatus(text) {
        this.status.text(text);
    }

    // Simulate realistic download progress
    start(type) {
        this.show();
        this.currentProgress = 0;
        
        const stages = [
            { end: 15, speed: 100, status: 'Connecting to server...' },
            { end: 30, speed: 150, status: 'Fetching video information...' },
            { end: 50, speed: 120, status: `Downloading ${type}...` },
            { end: 75, speed: 100, status: `Processing ${type}...` },
            { end: 90, speed: 80, status: 'Almost done...' },
            { end: 100, speed: 60, status: 'Finalizing download...' }
        ];

        let currentStage = 0;

        const animate = () => {
            if (currentStage >= stages.length) {
                clearInterval(this.interval);
                return;
            }

            const stage = stages[currentStage];
            this.setStatus(stage.status);

            this.interval = setInterval(() => {
                if (this.currentProgress >= stage.end) {
                    clearInterval(this.interval);
                    currentStage++;
                    animate();
                } else {
                    // Randomize progress increment for realism
                    const increment = Math.random() * 2 + 0.5;
                    this.currentProgress = Math.min(this.currentProgress + increment, stage.end);
                    this.updateDisplay();
                }
            }, stage.speed);
        };

        animate();
    }

    complete() {
        clearInterval(this.interval);
        this.currentProgress = 100;
        this.updateDisplay();
        this.setStatus('Download complete! ✓');
        
        setTimeout(() => {
            this.hide();
        }, 1500);
    }

    error() {
        clearInterval(this.interval);
        this.setStatus('Download failed ✗');
        setTimeout(() => {
            this.hide();
        }, 2000);
    }
}

const progressBar = new ProgressBar();

// Notification System
function showNotification(type, title, message) {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());

    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    
    const icon = type === 'success' ? '✓' : '✕';
    
    notification.innerHTML = `
        <div class="notification-icon">${icon}</div>
        <div class="notification-content">
            <div class="notification-title">${title}</div>
            <div class="notification-message">${message}</div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.classList.add('hide');
        setTimeout(() => notification.remove(), 500);
    }, 5000);
}

// Handle Video Form with proper error handling
$('#video-form').on('submit', function(e) {
    e.preventDefault();
    
    const url = $('#yturl').val();
    const btn = $('#video-btn');
    const btnText = btn.find('span');
    
    // Validate URL
    if (!url.trim()) {
        showNotification('error', 'Invalid Input', 'Please enter a YouTube URL');
        return;
    }
    
    // Disable button
    btn.prop('disabled', true);
    btnText.html('Downloading...');
    
    // Start progress bar
    progressBar.start('video');
    
    // First, check if URL is valid using AJAX
    $.ajax({
        url: '/download-video/',
        type: 'POST',
        data: { yturl: url },
        xhrFields: {
            responseType: 'blob' // Important for file download
        },
        success: function(blob, status, xhr) {
            // Check if response is JSON (error) or blob (file)
            const contentType = xhr.getResponseHeader('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                // It's an error response
                const reader = new FileReader();
                reader.onload = function() {
                    const errorData = JSON.parse(reader.result);
                    progressBar.error();
                    showNotification('error', 'Download Failed', errorData.message || 'An error occurred');
                };
                reader.readAsText(blob);
            } else {
                // It's a file - trigger download
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                
                // Get filename from Content-Disposition header
                const disposition = xhr.getResponseHeader('Content-Disposition');
                let filename = 'video.mp4';
                if (disposition && disposition.indexOf('filename=') !== -1) {
                    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                    const matches = filenameRegex.exec(disposition);
                    if (matches != null && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '');
                    }
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                a.remove();
                
                progressBar.complete();
                showNotification('success', 'Success!', 'Video downloaded successfully!');
                $('#yturl').val('');
            }
        },
        error: function(xhr, status, error) {
            progressBar.error();
            
            let errorMessage = 'Failed to download video. Please try again.';
            
            try {
                const errorData = JSON.parse(xhr.responseText);
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                // If response is not JSON, use default message
                if (xhr.status === 400) {
                    errorMessage = 'Invalid YouTube URL. Please check and try again.';
                } else if (xhr.status === 404) {
                    errorMessage = 'Video not found or unavailable.';
                }
            }
            
            showNotification('error', 'Download Failed', errorMessage);
        },
        complete: function() {
            btn.prop('disabled', false);
            btnText.html('Download Video');
        }
    });
});

// Handle Audio Form with proper error handling
$('#audio-form').on('submit', function(e) {
    e.preventDefault();
    
    const url = $('#ytaurl').val();
    const btn = $('#audio-btn');
    const btnText = btn.find('span');
    
    // Validate URL
    if (!url.trim()) {
        showNotification('error', 'Invalid Input', 'Please enter a YouTube URL');
        return;
    }
    
    // Disable button
    btn.prop('disabled', true);
    btnText.html('Downloading...');
    
    // Start progress bar
    progressBar.start('audio');
    
    // Check if URL is valid using AJAX
    $.ajax({
        url: '/download-audio/',
        type: 'POST',
        data: { ytaurl: url },
        xhrFields: {
            responseType: 'blob' // Important for file download
        },
        success: function(blob, status, xhr) {
            // Check if response is JSON (error) or blob (file)
            const contentType = xhr.getResponseHeader('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                // It's an error response
                const reader = new FileReader();
                reader.onload = function() {
                    const errorData = JSON.parse(reader.result);
                    progressBar.error();
                    showNotification('error', 'Download Failed', errorData.message || 'An error occurred');
                };
                reader.readAsText(blob);
            } else {
                // It's a file - trigger download
                const downloadUrl = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = downloadUrl;
                
                // Get filename from Content-Disposition header
                const disposition = xhr.getResponseHeader('Content-Disposition');
                let filename = 'audio.mp3';
                if (disposition && disposition.indexOf('filename=') !== -1) {
                    const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                    const matches = filenameRegex.exec(disposition);
                    if (matches != null && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '');
                    }
                }
                
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(downloadUrl);
                a.remove();
                
                progressBar.complete();
                showNotification('success', 'Success!', 'Audio downloaded successfully!');
                $('#ytaurl').val('');
            }
        },
        error: function(xhr, status, error) {
            progressBar.error();
            
            let errorMessage = 'Failed to download audio. Please try again.';
            
            try {
                const errorData = JSON.parse(xhr.responseText);
                errorMessage = errorData.message || errorMessage;
            } catch (e) {
                // If response is not JSON, use default message
                if (xhr.status === 400) {
                    errorMessage = 'Invalid YouTube URL. Please check and try again.';
                } else if (xhr.status === 404) {
                    errorMessage = 'Audio not found or unavailable.';
                }
            }
            
            showNotification('error', 'Download Failed', errorMessage);
        },
        complete: function() {
            btn.prop('disabled', false);
            btnText.html('Download Audio');
        }
    });
});