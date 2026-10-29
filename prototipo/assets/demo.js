/* Prototipo ELEAM — interacciones de demostración.
   No contiene datos reales ni lógica clínica. */

(function () {
  "use strict";

  var ROLE_KEY = "eleam-demo-role";
  var DEFAULT_ROLE = "ENFERMERIA";

  var ROLES = {
    ENFERMERIA: { label: "Enfermería", name: "Carolina Demo", initials: "CD" },
    ADMINISTRACION: { label: "Administración", name: "Andrés Demo", initials: "AD" },
    TECNICO: { label: "Técnico/a", name: "Tamara Demo", initials: "TD" },
    CUIDADOR: { label: "Cuidador/a", name: "Camila Demo", initials: "CD" },
    DIRECCION: { label: "Dirección", name: "Daniela Demo", initials: "DD" }
  };

  function normalize(value) {
    return (value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .trim();
  }

  function getRole() {
    var saved = localStorage.getItem(ROLE_KEY);
    return ROLES[saved] ? saved : DEFAULT_ROLE;
  }

  function applyRole() {
    var role = getRole();
    var data = ROLES[role];
    document.body.dataset.role = role;

    var select = document.getElementById("role-select");
    if (select) select.value = role;

    document.querySelectorAll("[data-roles]").forEach(function (el) {
      var allowed = (el.dataset.roles || "").split(/\s+/);
      el.hidden = allowed.indexOf(role) === -1;
    });

    document.querySelectorAll("[data-not-roles]").forEach(function (el) {
      var denied = (el.dataset.notRoles || "").split(/\s+/);
      el.hidden = denied.indexOf(role) !== -1;
    });

    document.querySelectorAll("[data-role-label]").forEach(function (el) {
      el.textContent = data.label;
    });
    document.querySelectorAll("[data-role-name]").forEach(function (el) {
      el.textContent = data.name;
    });
    document.querySelectorAll("[data-role-initials]").forEach(function (el) {
      el.textContent = data.initials;
    });

    var auditContent = document.querySelector("[data-audit-content]");
    if (auditContent) {
      var canAudit = role === "DIRECCION" || role === "ADMINISTRACION";
      auditContent.hidden = !canAudit;
      var auditDenied = document.querySelector("[data-audit-denied]");
      if (auditDenied) auditDenied.hidden = canAudit;
    }
  }

  function showToast(message, title) {
    var container = document.getElementById("toast-container");
    if (!container) {
      window.alert(message);
      return;
    }
    var toastEl = document.createElement("div");
    toastEl.className = "toast";
    toastEl.setAttribute("role", "status");
    toastEl.setAttribute("aria-live", "polite");

    var header = document.createElement("div");
    header.className = "toast-header";
    header.innerHTML = '<i class="bi bi-info-circle me-2"></i>';
    var strong = document.createElement("strong");
    strong.className = "me-auto";
    strong.textContent = title || "Prototipo";
    header.appendChild(strong);
    var close = document.createElement("button");
    close.type = "button";
    close.className = "btn-close";
    close.setAttribute("data-bs-dismiss", "toast");
    close.setAttribute("aria-label", "Cerrar");
    header.appendChild(close);

    var body = document.createElement("div");
    body.className = "toast-body";
    body.textContent = message;

    toastEl.appendChild(header);
    toastEl.appendChild(body);
    container.appendChild(toastEl);

    var toast = new bootstrap.Toast(toastEl, { delay: 4000 });
    toastEl.addEventListener("hidden.bs.toast", function () { toastEl.remove(); });
    toast.show();
  }

  function initRoleSwitch() {
    var select = document.getElementById("role-select");
    if (!select) return;
    select.addEventListener("change", function () {
      localStorage.setItem(ROLE_KEY, select.value);
      applyRole();
    });
  }

  function initDemoActions() {
    document.addEventListener("click", function (event) {
      var actionEl = event.target.closest("[data-demo-action]");
      if (!actionEl) return;
      event.preventDefault();
      showToast(
        actionEl.dataset.demoAction || "Acción simulada en el prototipo.",
        actionEl.dataset.demoTitle || "Prototipo"
      );
    });

    document.querySelectorAll("[data-prototype-form]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        showToast(
          form.dataset.successMessage || "Acción simulada. En la aplicación real se guardaría y quedaría en auditoría.",
          "Acción simulada"
        );
      });
    });
  }

  function initResidentFilter() {
    var table = document.getElementById("tabla-residentes");
    if (!table) return;

    var input = document.getElementById("filtro-texto");
    var status = document.getElementById("filtro-estado");
    var archived = document.getElementById("filtro-archivados");
    var counter = document.getElementById("resultado-conteo");
    var empty = document.getElementById("sin-resultados");
    var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr[data-search]"));

    function applyFilters() {
      var query = normalize(input ? input.value : "");
      var selectedStatus = status ? status.value : "";
      var showArchived = archived ? archived.checked : false;
      var visible = 0;

      rows.forEach(function (row) {
        var matchesText = !query || normalize(row.dataset.search).indexOf(query) !== -1;
        var matchesStatus = !selectedStatus || row.dataset.status === selectedStatus;
        var matchesArchived = showArchived || row.dataset.archived !== "true";
        var show = matchesText && matchesStatus && matchesArchived;
        row.hidden = !show;
        if (show) visible += 1;
      });

      if (counter) {
        counter.textContent = visible === 1 ? "1 residente" : visible + " residentes";
      }
      if (empty) empty.hidden = visible !== 0;
    }

    [input, status, archived].forEach(function (el) {
      if (!el) return;
      el.addEventListener(el.tagName === "SELECT" || el.type === "checkbox" ? "change" : "input", applyFilters);
    });

    var form = document.getElementById("form-busqueda");
    if (form) {
      form.addEventListener("submit", function (event) {
        event.preventDefault();
        applyFilters();
      });
    }

    applyFilters();
  }

  function initLoginDemo() {
    var form = document.getElementById("form-login-demo");
    if (!form) return;
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      window.location.href = "panel.html";
    });
  }

  function initDates() {
    var formatter = new Intl.DateTimeFormat("es-CL", {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric"
    });
    var text = formatter.format(new Date());
    text = text.charAt(0).toUpperCase() + text.slice(1);
    document.querySelectorAll("[data-today]").forEach(function (el) {
      el.textContent = text;
    });

    var hour = new Date().getHours();
    var greeting = hour < 12 ? "Buenos días" : hour < 19 ? "Buenas tardes" : "Buenas noches";
    document.querySelectorAll("[data-greeting]").forEach(function (el) {
      el.textContent = greeting;
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initDates();
    initLoginDemo();
    initRoleSwitch();
    initDemoActions();
    initResidentFilter();
    applyRole();

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
      new bootstrap.Tooltip(el);
    });
  });
})();
