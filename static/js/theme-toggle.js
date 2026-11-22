(function () {
    const updateIcon = (theme) => {
        const themeIcon = document.getElementById('themeIcon');
        if (!themeIcon) return;
        themeIcon.className = theme === 'dark'
            ? 'bi bi-sun-fill text-warning fs-5'
            : 'bi bi-moon-stars-fill text-dark fs-5';
    };

    window.setAppTheme = function (theme, emit = true) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        updateIcon(theme);
        if (emit) {
            window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme } }));
        }
    };

    document.addEventListener('DOMContentLoaded', () => {
        const themeToggleBtn = document.getElementById('themeToggleBtn');
        const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'light';
        updateIcon(currentTheme);

        if (themeToggleBtn) {
            themeToggleBtn.addEventListener('click', () => {
                const active = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
                const next = active === 'dark' ? 'light' : 'dark';
                window.setAppTheme(next, true);
            });
        }
    });

    window.addEventListener('themeChanged', (e) => {
        if (e.detail && e.detail.theme) {
            updateIcon(e.detail.theme);
        }
    });
})();
