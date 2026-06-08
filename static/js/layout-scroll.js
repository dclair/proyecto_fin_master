document.addEventListener('DOMContentLoaded', function() {
    const scrollContainer = document.querySelector('.mobile-hobby-scroll');
    const arrowLeft = document.querySelector('.scroll-arrow-left');
    const arrowRight = document.querySelector('.scroll-arrow-right');

    if (scrollContainer && arrowRight) {
        const handleScroll = () => {
            // Tolerancia de 5px para detectar los bordes
            const maxScrollLeft = scrollContainer.scrollWidth - scrollContainer.clientWidth;
            
            // Mostrar/Ocultar flecha izquierda
            if (arrowLeft) {
                if (scrollContainer.scrollLeft > 5) {
                    arrowLeft.classList.remove('scroll-arrow-hidden');
                } else {
                    arrowLeft.classList.add('scroll-arrow-hidden');
                }
            }

            // Mostrar/Ocultar flecha derecha y difuminado
            if (scrollContainer.scrollLeft >= maxScrollLeft - 5) {
                arrowRight.classList.add('scroll-arrow-hidden');
                scrollContainer.parentElement.classList.add('hide-fade');
            } else {
                arrowRight.classList.remove('scroll-arrow-hidden');
                scrollContainer.parentElement.classList.remove('hide-fade');
            }
        };

        // Ejecutar al cargar para configurar estado inicial
        handleScroll();

        // Escuchar eventos
        scrollContainer.addEventListener('scroll', handleScroll);
        window.addEventListener('resize', handleScroll);
    }
});
