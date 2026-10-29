/* Comportamientos progresivos de la interfaz ELEAM. */
(function () {
  "use strict";

  function initPasswordToggles(root) {
    root.querySelectorAll("[data-toggle-password]").forEach(function (button) {
      if (button.dataset.passwordReady === "true") return;
      button.dataset.passwordReady = "true";
      button.addEventListener("click", function () {
        var selector = button.getAttribute("data-toggle-password");
        var input = document.querySelector(selector);
        if (!input) return;
        var show = input.type === "password";
        input.type = show ? "text" : "password";
        button.setAttribute("aria-label", show ? "Ocultar contraseña" : "Mostrar contraseña");
        var icon = button.querySelector("i");
        if (icon) {
          icon.classList.toggle("bi-eye", !show);
          icon.classList.toggle("bi-eye-slash", show);
        }
      });
    });
  }

  function initConfirmations(root) {
    root.querySelectorAll("form[data-confirm]").forEach(function (form) {
      if (form.dataset.confirmReady === "true") return;
      form.dataset.confirmReady = "true";
      form.addEventListener("submit", function (event) {
        if (!window.confirm(form.getAttribute("data-confirm"))) {
          event.preventDefault();
        }
      });
    });
  }

  function initTooltips(root) {
    if (!window.bootstrap || !window.bootstrap.Tooltip) return;
    root.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (element) {
      if (element.dataset.tooltipReady === "true") return;
      element.dataset.tooltipReady = "true";
      new window.bootstrap.Tooltip(element);
    });
  }

  function activateTabFromHash() {
    if (!window.location.hash || !window.bootstrap || !window.bootstrap.Tab) return;
    var target =
      window.location.hash === "#cuidados"
        ? "#pane-cuidados"
        : window.location.hash;
    var trigger = document.querySelector(
      '[data-bs-toggle="tab"][data-bs-target="' + target + '"]'
    );
    if (!trigger || trigger.classList.contains("active")) return;
    new window.bootstrap.Tab(trigger).show();
  }

  function initAll(root) {
    initPasswordToggles(root);
    initConfirmations(root);
    initTooltips(root);
  }

  document.addEventListener("DOMContentLoaded", function () {
    initAll(document);
    activateTabFromHash();
  });

  window.addEventListener("hashchange", activateTabFromHash);

  document.addEventListener("htmx:afterSwap", function (event) {
    initAll(event.detail.target || document);
  });

  document.addEventListener("htmx:responseError", function () {
    var container = document.getElementById("htmx-error");
    if (!container) {
      container = document.createElement("div");
      container.id = "htmx-error";
      container.className = "alert alert-danger mt-3";
      container.setAttribute("role", "alert");
      var main = document.querySelector("main .container-xl");
      if (main) main.prepend(container);
    }
    container.textContent = "No se pudo actualizar la información. Recarga la página e inténtalo nuevamente.";
  });
})();
