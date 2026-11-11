(() => {
    const root = document.documentElement;
    const themeButton = document.getElementById("theme-toggle");

    function applyTheme(theme) {
        root.dataset.bsTheme = theme;
        localStorage.setItem("alma-theme", theme);
        if (themeButton) {
            const icon = themeButton.querySelector("i");
            icon.className = theme === "dark" ? "bi bi-sun" : "bi bi-moon-stars";
            themeButton.setAttribute(
                "aria-label",
                theme === "dark" ? "Activar tema claro" : "Activar tema oscuro"
            );
        }
        window.dispatchEvent(new CustomEvent("alma:theme", { detail: theme }));
    }

    applyTheme(localStorage.getItem("alma-theme") || "dark");
    themeButton?.addEventListener("click", () => {
        applyTheme(root.dataset.bsTheme === "dark" ? "light" : "dark");
    });

    const sidebar = document.getElementById("sidebar");
    const mobileMenu = document.querySelector(".mobile-menu");
    const mobileViewport = window.matchMedia("(max-width: 991.98px)");

    if (sidebar && mobileMenu && window.bootstrap?.Offcanvas) {
        const offcanvas = window.bootstrap.Offcanvas.getOrCreateInstance(sidebar, {
            backdrop: true,
            keyboard: true,
            scroll: false,
        });
        const closeButton = sidebar.querySelector("[data-sidebar-close]");

        mobileMenu.addEventListener("click", () => {
            if (mobileViewport.matches) {
                offcanvas.toggle();
            }
        });

        closeButton?.addEventListener("click", () => {
            if (mobileViewport.matches) {
                offcanvas.hide();
            }
        });

        sidebar.addEventListener("show.bs.offcanvas", () => {
            mobileMenu.setAttribute("aria-expanded", "true");
        });

        sidebar.addEventListener("hidden.bs.offcanvas", () => {
            mobileMenu.setAttribute("aria-expanded", "false");
        });

        mobileViewport.addEventListener("change", (event) => {
            if (!event.matches && sidebar.classList.contains("show")) {
                offcanvas.hide();
            }
        });
    }

    const dateNode = document.getElementById("current-date");
    const timeNode = document.getElementById("current-time");
    function updateClock() {
        const now = new Date();
        if (dateNode) {
            dateNode.textContent = new Intl.DateTimeFormat("es-CR", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
            }).format(now);
        }
        if (timeNode) {
            timeNode.textContent = new Intl.DateTimeFormat("es-CR", {
                hour: "2-digit",
                minute: "2-digit",
                hour12: false,
            }).format(now);
        }
    }
    updateClock();
    setInterval(updateClock, 30000);

    document.querySelectorAll("[data-client-mode]").forEach((control) => {
        const container = control.closest("form");
        const existing = container?.querySelector("[data-existing-client]");
        const fresh = container?.querySelector("[data-new-client]");
        const update = () => {
            const useNew = container.querySelector("[data-client-mode]:checked")?.value === "new";
            existing?.classList.toggle("d-none", useNew);
            fresh?.classList.toggle("d-none", !useNew);
            existing?.querySelector("select")?.toggleAttribute("required", !useNew);
            fresh?.querySelector("[name='nuevo_cliente_nombre']")?.toggleAttribute("required", useNew);
        };
        control.addEventListener("change", update);
        update();
    });

    document.addEventListener("submit", (evento) => {
        const formulario = evento.target;
        if (!(formulario instanceof HTMLFormElement)) return;
        const mensaje = formulario.dataset.confirmar;
        if (mensaje && !window.confirm(mensaje)) {
            evento.preventDefault();
            return;
        }
        const enviando = formulario.dataset.enviando;
        const boton = enviando ? formulario.querySelector("button") : null;
        if (boton) {
            boton.disabled = true;
            boton.textContent = enviando;
        }
    });

    document.addEventListener("click", (evento) => {
        const control = evento.target.closest("[data-accion]");
        if (!control) return;
        if (control.dataset.accion === "recargar") window.location.reload();
        if (control.dataset.accion === "imprimir") window.print();
    });
})();
