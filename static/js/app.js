// Comportamientos pequeños del sistema (sin librerías).
(function () {
  // Cerrar avisos
  document.querySelectorAll("[data-close]").forEach(function (b) {
    b.addEventListener("click", function () { b.parentElement.remove(); });
  });

  // Mostrar u ocultar la contraseña
  document.querySelectorAll("[data-eye]").forEach(function (b) {
    b.addEventListener("click", function () {
      var campo = document.getElementById(b.dataset.eye);
      campo.type = campo.type === "password" ? "text" : "password";
    });
  });

  // Confirmar antes de eliminar
  document.querySelectorAll("form[data-confirm]").forEach(function (f) {
    f.addEventListener("submit", function (e) {
      if (!window.confirm(f.dataset.confirm)) e.preventDefault();
    });
  });

  // Filtros que se aplican solos: al elegir, o 400 ms después de dejar de escribir
  document.querySelectorAll("form[data-autosubmit]").forEach(function (f) {
    var espera;
    f.addEventListener("change", function () { f.submit(); });
    f.querySelectorAll('input[type="text"], input:not([type])').forEach(function (i) {
      i.addEventListener("input", function () {
        clearTimeout(espera);
        espera = setTimeout(function () { f.submit(); }, 400);
      });
      // Deja el cursor al final tras recargar
      if (i.value && i === document.activeElement) i.setSelectionRange(i.value.length, i.value.length);
    });
    // Si se estaba escribiendo en el buscador, vuelve a enfocarlo
    var q = f.querySelector('input[name="q"]');
    if (q && q.value) { q.focus(); q.setSelectionRange(q.value.length, q.value.length); }
  });

  // Formulario de movimientos: Entrada / Salida
  var mov = document.getElementById("movform");
  if (mov) {
    var textos = {
      E: ["Una entrada aumenta las existencias del insumo seleccionado.", "Motivo de entrada *", "Proveedor u origen *"],
      S: ["Una salida reduce las existencias del insumo seleccionado.", "Motivo de salida *", "Cliente o destino *"]
    };
    mov.querySelectorAll('input[name="tipo"]').forEach(function (r) {
      r.addEventListener("change", function () {
        var t = r.value;
        mov.querySelectorAll(".seg label").forEach(function (l) {
          l.classList.toggle("on", l.contains(r));
        });
        document.getElementById("hint-tipo").textContent = textos[t][0];
        document.getElementById("l-motivo").textContent = textos[t][1];
        document.getElementById("l-tercero").textContent = textos[t][2];
        // Cambia las sugerencias: proveedores para entradas, clientes para salidas
        fetch(mov.dataset.terceros + "?tipo=" + t)
          .then(function (x) { return x.json(); })
          .then(function (d) {
            var lista = document.getElementById("terceros");
            lista.innerHTML = "";
            d.terceros.forEach(function (n) {
              var o = document.createElement("option");
              o.value = n;
              lista.appendChild(o);
            });
            mov.querySelector('[name="tercero"]').value = "";
          });
      });
    });
  }
})();
