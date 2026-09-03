const CommunityHub = {
    // 1. Previsualización de Imagen + Validación de Tamaño
    initImagePreview: function() {
        const input = document.getElementById('id_image');
        const container = document.getElementById('imageUploadContainer');
        const preview = document.getElementById('imagePreview');
        const placeholder = document.getElementById('uploadPlaceholder');
        
        const MAX_SIZE_MB = 5;
        const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

        if (container && input) {
            container.addEventListener('click', (e) => {
                if (e.target !== input && !e.target.closest('#btnRemoveImage')) input.click();
            });
            
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    if (file.size > MAX_SIZE_BYTES) {
                        alert(`¡Imagen demasiado pesada! El límite es de ${MAX_SIZE_MB}MB.`);
                        this.value = "";
                        placeholder.classList.remove('d-none');
                        preview.classList.add('d-none');
                        preview.innerHTML = "";
                        return;
                    }

                    const reader = new FileReader();
                    reader.onload = function(e) {
                        placeholder.classList.add('d-none');
                        preview.innerHTML = `
                            <img id="image-preview" src="${e.target.result}" class="img-fluid rounded shadow-sm mb-2" style="max-height: 250px; width: 100%; object-fit: cover;">
                            <div class="d-flex justify-content-center gap-3 mt-1">
                                <span class="extra-small text-hubs fw-bold" style="cursor:pointer;"><i class="bi bi-arrow-repeat me-1"></i>Cambiar</span>
                                <span class="extra-small text-danger fw-bold" id="btnRemoveImage" style="cursor:pointer;"><i class="bi bi-trash3 me-1"></i>Quitar</span>
                            </div>
                        `;
                        preview.classList.remove('d-none');
                        const badge = document.getElementById('badgePhoto');
                        if (badge) badge.classList.remove('d-none');
                    };
                    reader.readAsDataURL(file);
                }
            });

            // Delegar evento de quitar imagen
            preview.addEventListener('click', (e) => {
                if (e.target.closest('#btnRemoveImage')) {
                    e.stopPropagation();
                    input.value = "";
                    placeholder.classList.remove('d-none');
                    preview.classList.add('d-none');
                    preview.innerHTML = "";
                    const badge = document.getElementById('badgePhoto');
                    if (badge) badge.classList.add('d-none');
                }
            });
        }
    },

    // 1.5. Previsualización de Vídeo + Validación de Tamaño
    initVideoPreview: function() {
        const input = document.getElementById('id_video');
        const container = document.getElementById('videoUploadContainer');
        const preview = document.getElementById('videoPreview');
        const placeholder = document.getElementById('videoUploadPlaceholder');
        
        const MAX_SIZE_MB = 20;
        const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

        if (container && input) {
            container.addEventListener('click', (e) => {
                if (e.target !== input && !e.target.closest('#btnRemoveVideo')) input.click();
            });
            
            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    if (file.size > MAX_SIZE_BYTES) {
                        alert(`¡Vídeo demasiado pesado! El límite es de ${MAX_SIZE_MB}MB.`);
                        this.value = "";
                        placeholder.classList.remove('d-none');
                        preview.classList.add('d-none');
                        const videoTag = preview.querySelector('video');
                        if (videoTag) videoTag.src = "";
                        return;
                    }

                    const reader = new FileReader();
                    reader.onload = function(e) {
                        placeholder.classList.add('d-none');
                        const videoTag = preview.querySelector('video');
                        if (videoTag) {
                            videoTag.src = e.target.result;
                        }
                        preview.classList.remove('d-none');
                        const badge = document.getElementById('badgeVideo');
                        if (badge) badge.classList.remove('d-none');
                    };
                    reader.readAsDataURL(file);
                }
            });

            // Delegar evento de quitar vídeo
            preview.addEventListener('click', (e) => {
                if (e.target.closest('#btnRemoveVideo')) {
                    e.stopPropagation();
                    input.value = "";
                    placeholder.classList.remove('d-none');
                    preview.classList.add('d-none');
                    const videoTag = preview.querySelector('video');
                    if (videoTag) videoTag.src = "";
                    const badge = document.getElementById('badgeVideo');
                    if (badge) badge.classList.add('d-none');
                }
            });
        }
    },

    // 1.8. Previsualización y validación de PDF
    initDocumentPreview: function() {
        const input = document.getElementById('id_document');
        const container = document.getElementById('documentUploadContainer');
        const preview = document.getElementById('documentPreview');
        const placeholder = document.getElementById('documentUploadPlaceholder');
        const nameEl = document.getElementById('documentFileName');
        const sizeEl = document.getElementById('documentFileSize');
        
        const MAX_SIZE_MB = 10;
        const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

        if (container && input) {
            container.addEventListener('click', (e) => {
                if (e.target !== input && !e.target.closest('#btnRemoveDocument')) {
                    input.click();
                }
            });

            input.addEventListener('change', function() {
                const file = this.files[0];
                if (file) {
                    if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
                        alert('¡Formato no válido! Solo se permiten documentos en formato PDF.');
                        this.value = "";
                        if (placeholder) placeholder.classList.remove('d-none');
                        if (preview) preview.classList.add('d-none');
                        return;
                    }
                    if (file.size > MAX_SIZE_BYTES) {
                        alert(`¡Documento demasiado pesado! El límite es de ${MAX_SIZE_MB}MB.`);
                        this.value = "";
                        if (placeholder) placeholder.classList.remove('d-none');
                        if (preview) preview.classList.add('d-none');
                        return;
                    }
                    if (nameEl) nameEl.textContent = file.name;
                    if (sizeEl) sizeEl.textContent = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
                    if (placeholder) placeholder.classList.add('d-none');
                    if (preview) preview.classList.remove('d-none');
                    
                    const badge = document.getElementById('badgeDoc');
                    if (badge) badge.classList.remove('d-none');
                }
            });

            const removeBtn = document.getElementById('btnRemoveDocument');
            if (removeBtn) {
                removeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    input.value = "";
                    if (placeholder) placeholder.classList.remove('d-none');
                    if (preview) preview.classList.add('d-none');
                    const badge = document.getElementById('badgeDoc');
                    if (badge) badge.classList.add('d-none');
                });
            }
        }
    },

    // 2. Contador de Caracteres
    initCharCounter: function() {
        const textarea = document.getElementById('id_caption');
        const counter = document.getElementById('charCounter');
        if (textarea && counter) {
            textarea.addEventListener('input', function() {
                counter.textContent = `${this.value.length} / 2000`;
            });
        }
    },

    // 3. Smart Scroll (Solo Móvil)
    initSmartScroll: function() {
        const buttons = document.querySelectorAll('.btn-trending-view');
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                if (window.innerWidth < 992) {
                    const feed = document.querySelector('.col-lg-7');
                    if (feed) feed.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    },

    // 4. Estado de Carga (Spinner) - ¡VERSION MEJORADA Y UNIVERSAL!
    initLoadingState: function() {
        /**
         * Esta función ahora escucha CUALQUIER formulario con la clase .js-form-loading
         * o el botón específico #submit-btn.
         */
        document.addEventListener('submit', function(e) {
            const form = e.target;
            
            // Caso A: Formularios de la lista de eventos (.js-form-loading)
            if (form.classList.contains('js-form-loading')) {
                const button = form.querySelector('button[type="submit"]');
                if (button) {
                    const spinner = button.querySelector('.btn-spinner');
                    const text = button.querySelector('.btn-text');
                    
                    if (spinner) spinner.classList.remove('d-none');
                    if (text) text.classList.add('d-none');
                    
                    button.disabled = true;
                    button.classList.add('disabled');
                }
            }
            
            // Caso B: El botón único de "Crear Post" (#submit-btn)
            const submitBtn = document.getElementById('submit-btn');
            if (submitBtn && form.contains(submitBtn)) {
                const spinner = document.getElementById('btn-spinner');
                const icon = document.getElementById('btn-icon');
                const text = document.getElementById('btn-text');

                submitBtn.disabled = true;
                if (spinner) spinner.classList.remove('d-none');
                if (icon) icon.classList.add('d-none');
                if (text) text.innerText = "Procesando...";
            }
        });
    }
};

// --- RESTO DEL CODIGO (Masonry, Back to Top, Validation) SE MANTIENE IGUAL ---
document.addEventListener('DOMContentLoaded', () => {
    CommunityHub.initImagePreview();
    CommunityHub.initVideoPreview();
    CommunityHub.initDocumentPreview();
    CommunityHub.initCharCounter();
    CommunityHub.initSmartScroll();
    CommunityHub.initLoadingState();
});

// Botón Back to Top
const mybutton = document.getElementById("btn-back-to-top");
if (mybutton) {
    window.onscroll = function () {
        if (document.documentElement.scrollTop > 50) {
            mybutton.classList.remove("d-none");
        } else {
            mybutton.classList.add("d-none");
        }
    };
    mybutton.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });
}

// Validación de Bootstrap
(function () {
    'use strict'
    document.addEventListener('DOMContentLoaded', function() {
        const forms = document.querySelectorAll('.needs-validation');
        Array.from(forms).forEach(form => {
            form.addEventListener('submit', event => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            }, false);
        });
    });
})();

// Masonry y HTMX
(function() {
    'use strict';
    document.addEventListener('DOMContentLoaded', function() {
        const gridContainer = document.querySelector('.clicks-grid');
        let msnry;

        if (gridContainer) {
            imagesLoaded(gridContainer, function() {
                msnry = new Masonry(gridContainer, {
                    itemSelector: '.grid-item',
                    columnWidth: '.grid-item',
                    percentPosition: true,
                    transitionDuration: '0.4s'
                });
                GLightbox({ selector: '.glightbox', loop: true });
            });
        }

        document.body.addEventListener('htmx:afterOnLoad', function(evt) {
            if (gridContainer && msnry && evt.detail.xhr.responseURL.includes('page=')) {
                imagesLoaded(gridContainer, function() {
                    msnry.reloadItems();
                    msnry.layout();
                    GLightbox({ selector: '.glightbox', loop: true });
                });
            }
        });
    });
})();