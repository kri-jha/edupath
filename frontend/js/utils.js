const utils = {
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('en-IN', {
            style: 'currency',
            currency: 'INR',
            maximumFractionDigits: 0
        }).format(amount);
    },
    showToast: (message, type = 'success') => {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerText = message;
        
        Object.assign(toast.style, {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            padding: '12px 24px',
            borderRadius: '8px',
            color: '#fff',
            background: type === 'success' ? 'var(--success)' : (type === 'error' ? 'var(--danger)' : 'var(--primary)'),
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
            zIndex: '9999',
            opacity: '0',
            transition: 'opacity 0.3s'
        });

        document.body.appendChild(toast);
        setTimeout(() => toast.style.opacity = '1', 10);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
};
