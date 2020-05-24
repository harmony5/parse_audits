import dataclasses as dc
import re
from datetime import datetime
from typing import List, Dict, Any, Tuple


AUDIT_ENTRY_PATTERN = re.compile(
    r"(?<=====START====\n)"
    r"(?P<entry>"
    r"(?:Time           :    )(?P<time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]?\d{2}:\d{2})(?:\n)"  # YY-MM-DD HH:mm:SS Timezone
    r"(?:Schema Rev     :    )(?P<schema>\d+?)(?:\n)"
    r"(?:User Name      :    )(?P<user_name>[A-Za-z ]+?)(?:\n)"
    r"(?:User Login     :    )(?P<user_login>[uU]\d+?)(?:\n)"
    r"(?:User Groups    :    )(?P<user_groups>[\w\b ]+?)(?:\n)"
    r"(?:Action         :    )(?P<action>[\w\b ]+?)(?:\n)"
    r"(?:State          :    )(?P<state>[\w\b ]*?)(?:\n)"
    r"(?:==Fields==\n)"
    r"(?P<fields>.+?)"
    r")(?=\n====END====)",
    re.DOTALL,
)

AUDIT_ENTRY_FIELD_PATTERN = re.compile(
    r"(?P<fieldname>\w+?)(?:\s+)(?P<delta>\(\d+(:\d+)?\))(?:\n)"
    r"(?:"
    r"(?:    Old :    )(?P<old>.+?)(?=\n    New :    )"
    r"(?:\n    New :    )(?P<new>.+?)(?=\n\w+\s+\(\d+:\d+\)\n    Old :    |\n====END====|$)"
    r"|(?:        )(?P<value>.+?)(?=\n\w+\s+\(\d+\)\n        |\n====END====|$)"
    r")",
    re.DOTALL,
)


def parse_fields(field_str):
    fields = {
        f.group("fieldname"): {
            "delta": f.group("delta"),
            "old": f.group("old"),
            "new": f.group("new"),
            "value": f.group("value"),
        }
        for f in re.finditer(AUDIT_ENTRY_FIELD_PATTERN, field_str)
    }

    return fields


def parse_fields(field_str):
    fields = []
    for f in re.finditer(AUDIT_ENTRY_FIELD_PATTERN, field_str):
        fields.append(
            {
                "fieldname": f.group("fieldname"),
                "delta": f.group("delta"),
                "old": f.group("old"),
                "new": f.group("new"),
                "value": f.group("value"),
            }
        )

    return fields


@dc.dataclass()
class AuditEntry:
    date: datetime
    schema: int
    user_name: str
    user_login: str
    user_groups: List[str]
    action: str
    state: str
    fields: Dict[str, Dict[str, Any]]

    @staticmethod
    def parse_from_text(cls, text):
        match = re.match(AUDIT_ENTRY_PATTERN, text)
        audit = cls(
            date=datetime.strptime(match.group("time"), "%Y-%m-%d %H:%M:%S %z"),
            schema=match.group("schema"),
            user_name=match.group("user_name"),
            user_login=match.group("user_login"),
            user_groups=match.group("user_groups").split(),
            action=match.group("action"),
            state=match.group("state"),
            fields=parse_fields(match.group("fields")),
        )
        return audit


@dc.dataclass()
class AuditDB:
    users: List[Tuple[int, str, str]]
    groups: List[Tuple[int, str]]
    user_groups: List[Tuple[int, int]]
    entries: List[Tuple[int, int, datetime, int, str, str]]
    fields: List[Tuple[int, int, str, str, Any, Any]]


def parse_audits(audit_str: str) -> AuditDB:
    entries = re.finditer(AUDIT_ENTRY_PATTERN, audit_str)

    # USERS: (user_id, user_name, user_login)
    users = {}

    # GROUPS: (group_id, group_name)
    groups = {}

    # USER_GROUPS: (user_id, group_id)
    user_group = []

    # MODIFICATIONS: (entry_id, user_id, time, schema, action, state)
    mods = []

    # FIELD_MOD: (field_mod_id, entry_id, fieldname, delta, old_value, new_value)
    field_mod = []

    ucounter, gcounter = 1, 1

    for e_id, e in enumerate(entries):

        if not users.get(ulog := e.group("user_login")):
            # Updates the users 'table'
            users[ulog] = (ucounter, e.group("user_name"))
            ucounter += 1

            # TODO: convertir de listas de tuplas a listas de dict?
            # Cuales serian los beneficios. Talvez sea mas entendible asi?
            # TODO: users.append({ 'id': ucounter, 'user_name':e.group('user_name'), 'user_login':ulog })?
            # TODO: groups.append({ 'id': gcounter, 'group_name': e.group(g) })?

            # This is not the best way to do this:
            # some users share almost all groups,
            # so this iterates multiple times over
            # the same groups
            u_id = users.get(ulog)[0]
            for g in e.group("user_groups").split():
                if not groups.get(g):
                    # Updates the groups 'table'
                    groups[g] = gcounter
                    gcounter += 1

                g_id = groups.get(g)
                if (u_id, g_id) not in user_group:
                    # Relates the users 'table' with the groups 'table'
                    user_group.append((u_id, g_id))

        mods.append(
            (
                e_id,
                users.get(e.group("user_login"))[0],
                datetime.strptime(e.group("time"), "%Y-%m-%d %H:%M:%S %z"),
                e.group("schema"),
                e.group("action"),
                e.group("state"),
            )
        )

        for f_id, field in enumerate(
            re.finditer(AUDIT_ENTRY_FIELD_PATTERN, e.group("fields"))
        ):
            field_mod.append(
                (
                    f_id,
                    e_id,
                    field.group("fieldname"),
                    field.group("delta"),
                    field.group("old"),
                    field.group("new"),
                )
            )

    # Converting users and groups from dicts to lists.
    # Used dicts just for better performance

    users_list = [(uid, uname, ulogin) for ulogin, (uid, uname) in users.items()]
    groups_list = [(gid, gname) for gname, gid in groups.items()]

    audit_db = AuditDB(
        users=users_list,
        groups=groups_list,
        user_groups=user_group,
        entries=mods,
        fields=field_mod,
    )

    return audit_db


def parse_audits(audit_str: str) -> List[Dict[str, Any]]:
    audits = []

    for e in re.finditer(AUDIT_ENTRY_PATTERN, audit_str):
        audits.append(
            {
                "time": datetime.strptime(e.group("time"), "%Y-%m-%d %H:%M:%S %z"),
                "schema": e.group("schema"),
                "user": {
                    "name": e.group("user_name"),
                    "login": e.group("user_login"),
                    "groups": e.group("user_groups").split(),
                },
                "action": e.group("action"),
                "state": e.group("state"),
                "fields": parse_fields(e.group("fields")),
            }
        )

    return audits


par = """====START====
Time           :    2020-02-21 07:57:50 -04:00
Schema Rev     :    139
User Name      :    ELIZABETH NICOLE PEÑA CASTILLO
User Login     :    U40691
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    OFICIAL_ENC_SOP_ADMIN    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    Vendor_Management    Administracion_Presupuesto    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    VM_Adm_Suplidores    ANALISTA_I_ASEG_METODO    VM_Adm_Contratos    Analista_I_Admin_De_Versiones    Responsable_Ctro_Costo    Usuarios_Presupuestos    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    Service_Level_Management    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Modificar
State          :    
==Fields==
Acumulado_Credito  (12:12)
    Old :    3,868,862.46
    New :    5,010,336.72
Acumulado_Credito_Debito  (12:12)
    Old :    3,868,862.46
    New :    5,010,336.72
Creditos_Febrero  (12:12)
    Old :    3,868,862.46
    New :    5,010,336.72
Disponible_Total  (4:12)
    Old :    0.00
    New :    1,141,474.26
Notas_Credito_Debito  (17:26)
    Old :    45654288
45659208
    New :    45654288
45659208
45663740
Pres_Disponible_Febrero  (4:12)
    Old :    0.00
    New :    1,141,474.26

====END====

====START====
Time           :    2020-04-22 12:58:00 -04:00
Schema Rev     :    139
User Name      :    Gregorio Mota
User Login     :    U31500
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    OFICIAL_ENC_SOP_ADMIN    Responsables_Compras    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    Vendor_Management    Administracion_Presupuesto    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    VM_Adm_Suplidores    ANALISTA_I_ASEG_METODO    Analista_I_Admin_De_Versiones    Responsable_Ctro_Costo    Usuarios_Presupuestos    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Modificar
State          :    
==Fields==
Porc_Disponible_Abril  (6:1)
    Old :    100.00
    New :    0
Pres_Disponible_Abril  (4:12)
    Old :    0.00
    New :    2,686,357.37

====END====

====START====
Time           :    2020-04-22 12:57:58 -04:00
Schema Rev     :    139
User Name      :    Gregorio Mota
User Login     :    U31500
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    OFICIAL_ENC_SOP_ADMIN    Responsables_Compras    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    Vendor_Management    Administracion_Presupuesto    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    VM_Adm_Suplidores    ANALISTA_I_ASEG_METODO    Analista_I_Admin_De_Versiones    Responsable_Ctro_Costo    Usuarios_Presupuestos    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Modificar
State          :    
==Fields==
Ejecutado_Total  (13:13)
    Old :    19,790,779.38
    New :    17,104,422.01
Porc_Ejecucion   (5:5)
    Old :    69.54
    New :    60.10
Porc_Ejecucion_Abril  (14:14)
    Old :    478,503,167.00
    New :    209,867,430.00
Pres_Ejecutado_Abril  (12:12)
    Old :    4,785,031.67
    New :    2,098,674.30

====END====

====START====
Time           :    2020-04-22 12:57:56 -04:00
Schema Rev     :    139
User Name      :    Gregorio Mota
User Login     :    U31500
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    OFICIAL_ENC_SOP_ADMIN    Responsables_Compras    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    Vendor_Management    Administracion_Presupuesto    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    VM_Adm_Suplidores    ANALISTA_I_ASEG_METODO    Analista_I_Admin_De_Versiones    Responsable_Ctro_Costo    Usuarios_Presupuestos    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Modificar
State          :    
==Fields==
Reservas_Total   (12:12)
    Old :    4,470,604.54
    New :    7,156,961.91

====END====

====START====
Time           :    2020-04-22 12:44:48 -04:00
Schema Rev     :    139
User Name      :    Sony Torres Veras
User Login     :    U34041
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    Usuarios_Presupuestos_RP    OFICIAL_ENC_SOP_ADMIN    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    ANALISTA_I_ASEG_METODO    Analista_I_Admin_De_Versiones    Digitadores    Usuarios_Presupuestos    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Modificar
State          :    
==Fields==
Reservas_Total   (12:12)
    Old :    4,470,604.56
    New :    4,470,604.54

====END====

====START====
Time           :    2020-04-22 12:44:47 -04:00
Schema Rev     :    139
User Name      :    Sony Torres Veras
User Login     :    U34041
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    Usuarios_Presupuestos_RP    OFICIAL_ENC_SOP_ADMIN    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    ANALISTA_I_ASEG_METODO    Analista_I_Admin_De_Versiones    Digitadores    Usuarios_Presupuestos    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Modificar
State          :    
==Fields==
Ejecutado_Total  (13:13)
    Old :    19,790,779.36
    New :    19,790,779.38
Porc_Ejecucion_Abril  (14:14)
    Old :    478,503,165.00
    New :    478,503,167.00
Pres_Ejecutado_Abril  (12:12)
    Old :    4,785,031.65
    New :    4,785,031.67

====END====

====START====
Time           :    2020-01-08 16:49:59 -04:00
Schema Rev     :    139
User Name      :    Usuario Automatizador
User Login     :    automatizador
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    Oficial_Cumpl_Regulatorio    Release_Managers    OFICIAL_ENC_SOP_ADMIN    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    Administrators    EmailPlusAdmins    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    Administracion_Organigrama    ANALISTA_I_ASEG_METODO    Analista_I_Admin_De_Versiones    Responsable_Ctro_Costo    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    Automatizadores    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Import
State          :    
==Fields==
Detalle_Dist_Partida  (0:8)
    Old :    
    New :    45585262
Temp_Porc        (0:3)
    Old :    
    New :    100
TempDbid         (8:8)
    Old :    45574396
    New :    45585262

====END====

====START====
Time           :    2020-01-13 09:58:38 -04:00
Schema Rev     :    139
User Name      :    MASSIEL CABRERA CASTRO
User Login     :    U35409
User Groups    :    OFICIAL_I_CONTROL_CTAxPAGAR    Usuarios_Presupuestos_RP    OFICIAL_ENC_SOP_ADMIN    GERENTE_GESTION_RIESGO_CAPITAL    Subgerente_Integridad_Datos    GTE_Parametros_Tarjeta_Credito    GTE_RECLAM_BANC_Y_DEMAN    GTE_Integridad_Datos    GTE_Parametros_Tarjeta_Debito    ANALISTA_I_ASEG_METODO    Analista_I_Admin_De_Versiones    Digitadores    Usuarios_Presupuestos    Usuarios    Subgerente_Parametros_TD    Subgerente_Parametros_TC    SUBGERENTE_ANALISIS_GP_FIL    Analista_I_Auto_De_Pruebas
Action         :    Ingresar
State          :    Ingresado
==Fields==
Chk_Centro_Ajustado  (1)
        0
Chk_Incluir      (1)
        1
Descripcion      (119)
        Pago correspondiente al Arrendamiento Solución de Notificación de Mensajes VOCOM. Correspondiente al mes de Enero 2020.
Destinatario     (14)
        DEST0000000007
Destinatario_Area  (16)
        Div. Contraloría
Destinatario_FullName  (10)
        Sonia Ruiz

====END====
"""

for i, e in enumerate(parse_audits(par)):
    print(
        f"""\nEntry #{i}
    {e['time']=}
    {e['schema']=}
    {e['user']['name']=}
    {e['user']['groups'][0]=}
    {e['action']=}
    {e['state']=}
    {e['fields']=}
    """
    )
