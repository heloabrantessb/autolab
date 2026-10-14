/**
 * AutoLab — JavaScript Principal
 * Scripts auxiliares e melhorias progressivas de interface.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Inicialização de tooltips Bootstrap quando disponíveis
  if (typeof bootstrap !== "undefined" && bootstrap.Tooltip) {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    [...tooltipTriggerList].map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl));
  }

  // Fechamento automático suave de alertas de sucesso após 5 segundos
  const autoDismissAlerts = document.querySelectorAll(".alert-autodismiss");
  autoDismissAlerts.forEach((alertEl) => {
    setTimeout(() => {
      if (typeof bootstrap !== "undefined" && bootstrap.Alert) {
        const alertInstance = bootstrap.Alert.getOrCreateInstance(alertEl);
        alertInstance.close();
      } else {
        alertEl.style.transition = "opacity 0.5s ease";
        alertEl.style.opacity = "0";
        setTimeout(() => alertEl.remove(), 500);
      }
    }, 5000);
  });
});
