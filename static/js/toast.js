class Toast {
    constructor() {
        this.container = document.createElement('div');
        this.container.className = 'toast-container';
        document.body.appendChild(this.container);
    }

    show({ type = 'info', title = '', message = '', duration = 3000 }) {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icon = this.getIcon(type);
        
        toast.innerHTML = `
            <span class="toast-icon">${icon}</span>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
            </div>
            <button class="toast-close">&times;</button>
        `;

        this.container.appendChild(toast);

        // Add close button functionality
        const closeButton = toast.querySelector('.toast-close');
        closeButton.addEventListener('click', () => {
            this.removeToast(toast);
        });

        // Auto remove after duration
        if (duration > 0) {
            setTimeout(() => {
                this.removeToast(toast);
            }, duration);
        }
    }

    removeToast(toast) {
        toast.style.animation = 'slideOut 0.3s ease-in-out forwards';
        setTimeout(() => {
            toast.remove();
        }, 300);
    }

    getIcon(type) {
        const icons = {
            success: '<i class="ri-checkbox-circle-fill"></i>',
            error: '<i class="ri-close-circle-fill"></i>',
            warning: '<i class="ri-alert-fill"></i>',
            info: '<i class="ri-information-fill"></i>'
        };
        return icons[type] || icons.info;
    }
}

// Create global toast instance
window.toast = new Toast(); 