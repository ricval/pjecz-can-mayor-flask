"""
Archivo - Documentos Bitacoras, vistas
"""

import json
from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from lib.datatables import get_datatable_parameters, output_datatable_json
from lib.safe_string import safe_string, safe_message

from can_mayor.blueprints.bitacoras.models import Bitacora
from can_mayor.blueprints.modulos.models import Modulo
from can_mayor.blueprints.permisos.models import Permiso
from can_mayor.blueprints.usuarios.decorators import permission_required
from can_mayor.blueprints.arc_documentos_bitacoras.models import ArcDocumentoBitacora

MODULO = "ARC DOCUMENTOS"

arc_documentos_bitacoras = Blueprint("arc_documentos_bitacoras", __name__, template_folder="templates")


@arc_documentos_bitacoras.before_request
@login_required
@permission_required(MODULO, Permiso.VER)
def before_request():
    """Permiso por defecto"""


@arc_documentos_bitacoras.route("/arc_documentos_bitacoras/datatable_json", methods=["GET", "POST"])
def datatable_json():
    """DataTable JSON para listado de Archivo - Documentos Bitácoras"""
    # Tomar parámetros de Datatables
    draw, start, rows_per_page = get_datatable_parameters()
    # Consultar
    consulta = ArcDocumentoBitacora.query
    # Primero filtrar por columnas propias
    if "estatus" in request.form:
        consulta = consulta.filter_by(estatus=request.form["estatus"])
    else:
        consulta = consulta.filter_by(estatus="A")
    if "arc_documento_id" in request.form:
        consulta = consulta.filter_by(arc_documento_id=int(request.form["arc_documento_id"]))
    if "fecha_desde" in request.form:
        consulta = consulta.filter(ArcDocumentoBitacora.modificado >= request.form["fecha_desde"])
    if "fecha_hasta" in request.form:
        consulta = consulta.filter(ArcDocumentoBitacora.modificado <= request.form["fecha_hasta"] + " 23:59:59")
    if "accion" in request.form:
        consulta = consulta.filter_by(accion=request.form["accion"])
    if "usuario_id" in request.form:
        consulta = consulta.filter_by(usuario_id=int(request.form["usuario_id"]))
    # Luego filtrar por columnas de otras tablas
    # if "persona_rfc" in request.form:
    #     consulta = consulta.join(Persona)
    #     consulta = consulta.filter(Persona.rfc.contains(safe_rfc(request.form["persona_rfc"], search_fragment=True)))
    # Ordenar y paginar
    registros = consulta.order_by(ArcDocumentoBitacora.id.desc()).offset(start).limit(rows_per_page).all()
    total = consulta.count()
    # Elaborar datos para DataTable
    data = []
    for resultado in registros:
        data.append(
            {
                "id": resultado.id,
                "usuario": {
                    "nombre": resultado.usuario.nombre,
                    "url": url_for("usuarios.detail", usuario_id=resultado.usuario.id),
                },
                "accion": resultado.accion,
                "fojas": resultado.fojas,
                "observaciones": "" if resultado.observaciones is None else resultado.observaciones,
                "modificado": resultado.modificado.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )
    # Entregar JSON
    return output_datatable_json(draw, total, data)
