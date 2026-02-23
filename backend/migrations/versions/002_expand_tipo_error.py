"""Ampliar ck_tipo_error para incluir todos los tipos usados en el procesador.

Revision ID: 002
Revises: 001
Create Date: 2026-02-17

"""
from typing import Sequence, Union

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TIPOS_PERMITIDOS = (
    "archivo_no_encontrado", "error_xml", "estructura_invalida", "error_lectura", "error_global",
    "formato_cups_invalido", "cliente_inexistente", "tipo_vacio", "tipo_no_soportado", "formato_invalido",
    "fecha_vacia", "rango_fechas_invalido", "fecha_formato_invalido", "formato_numerico_invalido",
    "periodos_insuficientes", "registro_duplicado", "inconsistencia",
    "archivo_duplicado", "inconsistencia_numerica", "array_longitud_invalida", "fecha_invalida",
)


def upgrade() -> None:
    op.drop_constraint("ck_tipo_error", "registro_errores", type_="check")
    in_clause = ", ".join(f"'{t}'" for t in TIPOS_PERMITIDOS)
    op.create_check_constraint(
        "ck_tipo_error",
        "registro_errores",
        f"tipo_error IN ({in_clause})",
    )


def downgrade() -> None:
    op.drop_constraint("ck_tipo_error", "registro_errores", type_="check")
    op.create_check_constraint(
        "ck_tipo_error",
        "registro_errores",
        "tipo_error IN ("
        "'cliente_inexistente', 'tipo_no_soportado', 'formato_invalido', "
        "'archivo_duplicado', 'inconsistencia_numerica', "
        "'array_longitud_invalida', 'fecha_invalida')",
    )
