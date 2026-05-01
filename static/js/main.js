document.addEventListener("DOMContentLoaded", function () {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    setTimeout(function () {
        document.querySelectorAll(".alert").forEach(function (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    document.querySelectorAll(".fila-link").forEach(function (fila) {
        fila.addEventListener("click", function (event) {
            if (event.target.closest("a, button, input, select, textarea")) {
                return;
            }
            window.location = this.dataset.href;
        });
    });
});
