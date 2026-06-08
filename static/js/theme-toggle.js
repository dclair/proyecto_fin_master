document.addEventListener('DOMContentLoaded', () => {
    const themeToggleBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeIcon');
    
    if (themeToggleBtn && themeIcon) {
        // Setea el ícono inicial basado en el tema actual
        const currentTheme = document.documentElement.getAttribute('data-bs-theme');
        themeIcon.className = currentTheme === 'dark' ? 'bi bi-sun-fill text-warning fs-5' : 'bi bi-moon-stars-fill text-dark fs-5';

        themeToggleBtn.addEventListener('click', () => {
            const theme = document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-bs-theme', theme);
            localStorage.setItem('theme', theme);
            
            // Actualiza el ícono
            themeIcon.className = theme === 'dark' ? 'bi bi-sun-fill text-warning fs-5' : 'bi bi-moon-stars-fill text-dark fs-5';
        });
    }
});
