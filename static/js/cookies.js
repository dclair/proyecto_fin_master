// document.addEventListener("DOMContentLoaded", function() {
//     const banner = document.getElementById('cookie-banner');
//     const acceptBtn = document.getElementById('accept-cookies');
//     const rejectBtn = document.getElementById('reject-cookies'); // <--- Añadimos esta referencia

//     // 1. Verificar si ya se tomó una decisión previa
//     if (localStorage.getItem('hubs-cookies-accepted')) {
//         banner.style.display = 'none';
//     }

//     // 2. Lógica para ACEPTAR TODO
//     if (acceptBtn) {
//         acceptBtn.addEventListener('click', () => {
//             localStorage.setItem('hubs-cookies-accepted', 'all');
//             banner.classList.add('hidden'); // Activa la animación de bajada del CSS
//         });
//     }

//     // 3. Lógica para RECHAZAR / SOLO NECESARIAS
//     if (rejectBtn) {
//         rejectBtn.addEventListener('click', () => {
//             localStorage.setItem('hubs-cookies-accepted', 'essential');
//             banner.classList.add('hidden'); // También lo ocultamos
//         });
//     }
// });

document.addEventListener("DOMContentLoaded", function() {
    const banner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('accept-cookies');
    const rejectBtn = document.getElementById('reject-cookies');
    const resetBtn = document.getElementById('reset-cookies'); // El botón del footer

    // ============================================================
    // 1. LÓGICA PARA MODIFICAR / RESETEAR COOKIES
    // ============================================================
    if (resetBtn) {
        resetBtn.addEventListener('click', function(e) {
            e.preventDefault(); // Evita que la página salte
            localStorage.removeItem('hubs-cookies-accepted'); // Borramos la decisión
            location.reload(); // Recargamos para que el banner vuelva a saltar
        });
    }

    // Si el banner no está en el HTML de esta página, nos detenemos aquí de forma segura
    if (!banner) return; 

    // ============================================================
    // 2. COMPROBACIÓN INICIAL Y BOTONES DEL BANNER
    // ============================================================
    
    // Si ya existe una decisión previa, ocultamos el banner de inmediato
    if (localStorage.getItem('hubs-cookies-accepted')) {
        banner.style.display = 'none'; 
    }

    // Botón: Aceptar todas
    if (acceptBtn) {
        acceptBtn.addEventListener('click', () => {
            localStorage.setItem('hubs-cookies-accepted', 'all');
            banner.classList.add('hidden'); // Añade la clase CSS de subida/ocultación
        });
    }

    // Botón: Solo necesarias
    if (rejectBtn) {
        rejectBtn.addEventListener('click', () => {
            localStorage.setItem('hubs-cookies-accepted', 'essential');
            banner.classList.add('hidden'); // Añade la clase CSS de subida/ocultación
        });
    }

    // Botón: Rechazar todas
    const rejectAllBtn = document.getElementById('reject-all-cookies');
    if (rejectAllBtn) {
        rejectAllBtn.addEventListener('click', () => {
            localStorage.setItem('hubs-cookies-accepted', 'essential');
            banner.classList.add('hidden'); 
        });
    }
});