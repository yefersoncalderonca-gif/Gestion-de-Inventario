from datetime import date, timedelta
from io import BytesIO
from urllib.parse import urlencode

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from aula.utils import paginar
from movimientos.models import Movimiento
from productos.models import Producto
from usuarios.auth import requiere_sesion

from .models import Reporte

TIPOS = [("movimientos", "Movimientos del periodo"), ("stock", "Stock actual"),
         ("vencimientos", "Vencimientos y recargas"), ("bajo", "Bajo stock mínimo")]


def _fecha(texto, defecto):
    try:
        return date.fromisoformat(texto)
    except (TypeError, ValueError):
        return defecto


def _datos(tipo, desde, hasta):
    """Devuelve (título, cabecera, filas, tarjetas) del reporte pedido."""
    prods = list(Producto.objects.select_related("categoria"))
    if tipo == "movimientos":
        movs = list(Movimiento.objects.filter(fecha__gte=desde, fecha__lte=hasta)
                    .select_related("producto", "cliente", "proveedor"))
        ent = sum(m.cantidad for m in movs if m.tipo == "E")
        sal = sum(m.cantidad for m in movs if m.tipo == "S")
        cab = ["Fecha", "Tipo", "Producto", "Cantidad", "Cliente o proveedor", "Motivo", "Factura"]
        filas = [[m.fecha.strftime("%d/%m/%Y"), m.get_tipo_display(), m.producto.nombre,
                  m.firmada, m.tercero, m.motivo, m.factura] for m in movs]
        return "Movimientos del periodo", cab, filas, [
            ("in", "Entradas", ent, "unidades"), ("out", "Salidas", sal, "unidades"),
            ("swap", "Movimientos", len(movs), "registros")]
    if tipo == "vencimientos":
        con_fecha = sorted((p for p in prods if p.fecha_clave), key=lambda p: p.fecha_clave)
        cab = ["Código", "Producto", "Lote", "Fecha clave", "Días restantes", "Estado"]
        filas = [[p.codigo, p.nombre, p.lote or "—", p.fecha_clave.strftime("%d/%m/%Y"),
                  p.dias_restantes, p.estado] for p in con_fecha]
        vencidos = sum(1 for p in con_fecha if p.dias_restantes < 0)
        prox = sum(1 for p in con_fecha if 0 <= p.dias_restantes <= 30)
        return "Vencimientos y recargas", cab, filas, [
            ("alert", "Vencidos", vencidos, "productos"), ("calendar", "Próximos 30 días", prox, "productos"),
            ("box", "Con fecha", len(con_fecha), "productos")]
    if tipo == "bajo":
        bajos = [p for p in prods if p.bajo_minimo]
        cab = ["Código", "Producto", "Cantidad", "Mínimo", "Faltante"]
        filas = [[p.codigo, p.nombre, p.stock, p.stock_minimo, max(p.stock_minimo - p.stock, 0)]
                 for p in bajos]
        return "Productos bajo el stock mínimo", cab, filas, [
            ("alert", "Productos en alerta", len(bajos), "productos"),
            ("layers", "Unidades faltantes", sum(f[4] for f in filas), "unidades"),
            ("box", "Catálogo", len(prods), "productos")]
    cab = ["Código", "Producto", "Categoría", "Cantidad", "Mínimo", "Estado"]
    filas = [[p.codigo, p.nombre, str(p.categoria or "—"), p.stock, p.stock_minimo, p.estado] for p in prods]
    return "Stock actual", cab, filas, [
        ("box", "Productos", len(prods), "productos"),
        ("layers", "Unidades", sum(p.stock for p in prods), "unidades"),
        ("chart", "Valor a precio de compra", f"${int(sum(p.valor_compra for p in prods)):,}".replace(",", "."), "COP")]


def _xlsx(titulo, cab, filas, desde, hasta):
    from openpyxl import Workbook
    from openpyxl.styles import Font
    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"
    ws.append([f"{titulo} · {desde:%d/%m/%Y} – {hasta:%d/%m/%Y}"])
    ws["A1"].font = Font(bold=True, size=13)
    ws.append(cab)
    for c in ws[2]:
        c.font = Font(bold=True)
    for f in filas:
        ws.append(list(f))
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = min(40, max(len(str(c.value or "")) for c in col) + 2)
    out = BytesIO()
    wb.save(out)
    r = HttpResponse(out.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    r["Content-Disposition"] = 'attachment; filename="reporte_magnussig.xlsx"'
    return r


def _pdf(titulo, cab, filas, desde, hasta):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    out = BytesIO()
    doc = SimpleDocTemplate(out, pagesize=landscape(A4), title=titulo,
                            leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    est = getSampleStyleSheet()
    data = [cab] + [["—" if v is None else str(v) for v in f] for f in filas]
    t = Table(data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f2a4d")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white), ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f3f6fb")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#c9d3e3")),
    ]))
    doc.build([
        Paragraph(f"MagnusSIG SAS · {titulo}", est["Title"]),
        Paragraph(f"Periodo: {desde:%d/%m/%Y} – {hasta:%d/%m/%Y}. Informe de apoyo al SG-SST; "
                  "no implica certificación ni afirmación de cumplimiento legal.", est["Normal"]),
        Spacer(1, 10), t])
    r = HttpResponse(out.getvalue(), content_type="application/pdf")
    r["Content-Disposition"] = 'attachment; filename="reporte_magnussig.pdf"'
    return r


@requiere_sesion
def reportes(request):
    hoy = timezone.localdate()
    tipo = request.GET.get("tipo", "movimientos")
    if tipo not in dict(TIPOS):
        tipo = "movimientos"
    desde = _fecha(request.GET.get("desde"), hoy - timedelta(days=30))
    hasta = _fecha(request.GET.get("hasta"), hoy)
    if desde > hasta:
        messages.error(request, "La fecha «Desde» no puede ser posterior a «Hasta»: se intercambiaron.")
        desde, hasta = hasta, desde

    titulo, cab, filas, tarjetas = _datos(tipo, desde, hasta)
    formato = request.GET.get("export")
    if formato in ("pdf", "xlsx"):
        Reporte.objects.create(tipo=f"{tipo} ({formato})", fecha_desde=desde, fecha_hasta=hasta,
                               usuario=request.usuario)
        return (_pdf if formato == "pdf" else _xlsx)(titulo, cab, filas, desde, hasta)

    prods = list(Producto.objects.all())
    bajo = [p for p in prods if p.bajo_minimo]
    return render(request, "reportes.html", {
        "activo": "reportes", "tipos": TIPOS, "tipo": tipo, "desde": desde, "hasta": hasta,
        "qs": urlencode({"tipo": tipo, "desde": desde.isoformat(), "hasta": hasta.isoformat()}),
        "tarjetas": tarjetas, "titulo": titulo, "cab": cab, "n": len(filas),
        "page": paginar(request, filas, 10),
        "n_prods": len(prods), "n_bajo": len(bajo), "bajo_txt": ", ".join(p.nombre for p in bajo),
        "n_fecha": sum(1 for p in prods if p.estado in ("Vencido", "Urgente", "Por vencer")),
    })
