// JavaScript para manejar los menús desplegables
document.addEventListener("DOMContentLoaded", function () {
  // Obtener todos los botones de categoría
  const categoryButtons = document.querySelectorAll(".category-button");

  // Añadir evento de clic a cada botón
  categoryButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const targetId = this.id.replace("btn-", "menu-");
      const targetMenu = document.getElementById(targetId);

      // Si el menú actual está cerrado, cerrar todos los demás primero
      if (!this.classList.contains("active")) {
        // Cerrar todos los menús
        document.querySelectorAll(".category-menu").forEach((menu) => {
          menu.classList.remove("show");
        });

        // Desactivar todos los botones
        document.querySelectorAll(".category-button").forEach((btn) => {
          btn.classList.remove("active");
        });
      }

      // Alternar el estado del menú actual
      this.classList.toggle("active");
      targetMenu.classList.toggle("show");
    });
  });

  // Marcar como activo el elemento del menú correspondiente a la página actual
  const currentPath = window.location.pathname;
  document.querySelectorAll(".menu-item a").forEach((link) => {
    if (link.getAttribute("href") === currentPath) {
      link.classList.add("active");

      // Expandir la categoría correspondiente
      const parentMenu = link.closest(".category-menu");
      if (parentMenu) {
        parentMenu.classList.add("show");
        const buttonId = parentMenu.id.replace("menu-", "btn-");
        document.getElementById(buttonId).classList.add("active");
      }
    }
  });
});
