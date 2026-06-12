# SDD Explore: Marketplace

## Contexto del Proyecto
El proyecto `aficionados_network` es una red social y gestor de eventos para profesionales de terapias naturales (osteopatía, quiromasaje, acupuntura, etc.).
Las apps principales actuales son:
- `profiles`: Gestión de usuarios, perfiles y las terapias (`Hobby`).
- `posts`: Manejo del feed, "clicks" (imágenes) y eventos ("quedadas").
- `chat`: Mensajería directa entre usuarios.

## Requisito
Crear un "Mercadillo" (Marketplace) para que los profesionales puedan vender, comprar o alquilar material clínico (camillas, aceites, material) o servicios profesionales (alquiler de boxes o gabinetes).

## Impacto Arquitectónico
- **Nueva App Django**: Se requiere correr `python manage.py startapp marketplace`.
- **Modelos**: Se necesita un modelo de Producto (`Item` o `Listing`), ligado a un Usuario (`User`) y a una Terapia (`Hobby` de la app `profiles`).
- **Estados**: El producto puede estar Disponible, Reservado o Vendido.
- **Tipos**: Venta, Alquiler, Intercambio.
- **Integración con Chat**: La comunicación no debería requerir un sistema de mensajería nuevo, sino reutilizar la app `chat` existente mediante un botón "Contactar Vendedor" que abra o redirija al chat privado.
- **URLs**: El namespace será `marketplace:`. Se incluirá en las urls globales.
- **Vistas**: Lista de productos, Detalles, Crear, Editar, Eliminar.

## Riesgos y Consideraciones
- **Filtros**: Es vital que se pueda filtrar por Terapia (`Hobby`) para que un quiromasajista no vea agujas de acupuntura si no le interesan.
- **Imágenes**: Deberán reutilizar la función de compresión y validación (hasta 5MB) que ya se utiliza en `posts.models.validate_image_size`.
