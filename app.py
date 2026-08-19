import json
import os
from datetime import datetime

from flask import Flask, Response, jsonify, render_template, request
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
ASISTENCIA_FILE = os.path.join(DATA_DIR, "asistencia.json")
TICKETS_FILE = os.path.join(DATA_DIR, "tickets.json")


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/asistencia", methods=["GET"])
def get_asistencia():
    records = load_json(ASISTENCIA_FILE, [])
    records.reverse()
    return jsonify(records)


@app.route("/api/marcar", methods=["POST"])
def marcar():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    tipo = data.get("tipo")
    if not nombre:
        return jsonify({"error": "El nombre es obligatorio"}), 400
    if tipo not in ("entrada", "salida", "salida_refrigerio", "retorno_refrigerio"):
        return jsonify({"error": "Tipo no válido"}), 400

    now = datetime.now()
    record = {
        "nombre": nombre,
        "tipo": tipo,
        "fecha": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M:%S"),
    }
    records = load_json(ASISTENCIA_FILE, [])
    records.append(record)
    save_json(ASISTENCIA_FILE, records)
    return jsonify({"ok": True, "record": record})


@app.route("/api/ticket", methods=["POST"])
def crear_ticket():
    data = request.get_json(silent=True) or {}
    nombre = (data.get("nombre") or "").strip()
    titulo = (data.get("titulo") or "").strip()
    mensaje = (data.get("mensaje") or "").strip()
    if not nombre or not titulo or not mensaje:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    tickets = load_json(TICKETS_FILE, [])
    ticket = {
        "id": len(tickets) + 1,
        "nombre": nombre,
        "titulo": titulo,
        "mensaje": mensaje,
        "estado": "abierto",
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    tickets.append(ticket)
    save_json(TICKETS_FILE, tickets)
    return jsonify({"ok": True, "ticket": ticket})


@app.route("/api/tickets", methods=["GET"])
def get_tickets():
    tickets = load_json(TICKETS_FILE, [])
    tickets.reverse()
    return jsonify(tickets)


@app.route("/api/ticket/<int:ticket_id>/cerrar", methods=["POST"])
def cerrar_ticket(ticket_id):
    tickets = load_json(TICKETS_FILE, [])
    for t in tickets:
        if t["id"] == ticket_id:
            t["estado"] = "cerrado"
            save_json(TICKETS_FILE, tickets)
            return jsonify({"ok": True})
    return jsonify({"error": "Ticket no encontrado"}), 404


@app.route("/api/exportar", methods=["GET"])
def exportar():
    wb = Workbook()

    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="2D2D56", end_color="2D2D56", fill_type="solid")
    header_align = Alignment(horizontal="center")
    border = Border(
        bottom=Side(style="thin", color="CCCCCC"),
    )

    # Hoja Asistencia
    ws1 = wb.active
    ws1.title = "Asistencia"
    ws1.append(["Nombre", "Tipo", "Fecha", "Hora"])
    for cell in ws1[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    records = load_json(ASISTENCIA_FILE, [])
    for r in records:
        ws1.append([r["nombre"], r["tipo"], r["fecha"], r["hora"]])

    for row in ws1.iter_rows(min_row=2, max_row=ws1.max_row):
        for cell in row:
            cell.border = border

    ws1.column_dimensions["A"].width = 20
    ws1.column_dimensions["B"].width = 12
    ws1.column_dimensions["C"].width = 15
    ws1.column_dimensions["D"].width = 12

    # Hoja Tickets
    ws2 = wb.create_sheet("Tickets")
    ws2.append(["ID", "Nombre", "Asunto", "Mensaje", "Estado", "Fecha"])
    for cell in ws2[1]:
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    tickets = load_json(TICKETS_FILE, [])
    for t in tickets:
        ws2.append([t["id"], t["nombre"], t["titulo"], t["mensaje"], t["estado"], t["fecha"]])

    for row in ws2.iter_rows(min_row=2, max_row=ws2.max_row):
        for cell in row:
            cell.border = border

    ws2.column_dimensions["A"].width = 8
    ws2.column_dimensions["B"].width = 20
    ws2.column_dimensions["C"].width = 30
    ws2.column_dimensions["D"].width = 40
    ws2.column_dimensions["E"].width = 12
    ws2.column_dimensions["F"].width = 20

    buf = Workbook.__call__  # dummy, we just need BytesIO
    from io import BytesIO
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
    return Response(
        buf.getvalue(),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment;filename=reporte_{fecha}.xlsx"},
    )


if __name__ == "__main__":
    import sys
    port = int(os.environ.get("PORT", 5000))
    debug = "--debug" in sys.argv
    app.run(debug=debug, host="0.0.0.0", port=port)