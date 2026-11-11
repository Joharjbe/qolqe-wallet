"""Pasos de pytest-bdd del G4: casos funcionales y técnicos adicionales (contactos y solicitudes)."""
import json
import re
import threading
from datetime import datetime, timedelta

import conftest  # Helpers compartidos: URL, USUARIOS, Sesiones.
import httpx
import jsonschema_rs
from pytest_bdd import given, parsers, then, when

# Los pasos nombran al usuario de forma explícita para no capturar frases de otros módulos.
_NOMBRE = r"(?P<nombre>Ana|Bruno|Carla|Diego)"
_PIN_CARGA = "2580"  # Usuarios de carga de la semilla: celulares 900000001 a 900000200.
_SIN_CUERPO = "(sin cuerpo)"
_CONTRATO = {}


# ---------- Helpers ----------

def _cabeceras(s, nombre):
    """Token del usuario sin cambiar el usuario actual del escenario."""
    if nombre not in s.tokens:
        celular, pin = conftest.USUARIOS.get(nombre, (nombre, _PIN_CARGA))
        r = s.cliente.post("/api/auth/login", json={"celular": celular, "pin": pin})
        assert r.status_code == 200, r.text
        s.tokens[nombre] = {"Authorization": f"Bearer {r.json()['access_token']}"}
    return s.tokens[nombre]


def _pedir(s, metodo, ruta, nombre, **opciones):
    s.respuesta = s.cliente.request(metodo, ruta, headers=_cabeceras(s, nombre), **opciones)
    return s.respuesta


def _nombre_de(celular):
    return next(nombre for nombre, (cel, _) in conftest.USUARIOS.items() if cel == celular)


def _contactos(s, nombre):
    _cabeceras(s, nombre)
    return s.contactos(nombre)


def _contacto_id(s, alias, nombre):
    return next(c["id"] for c in _contactos(s, nombre) if c["alias"] == alias)


def _solicitudes(s, nombre):
    r = s.cliente.get("/api/solicitudes", headers=_cabeceras(s, nombre))
    assert r.status_code == 200, r.text
    return r.json()


def _solicitar(s, solicitante, alias, monto, motivo):
    cuerpo = {"contacto_id": _contacto_id(s, alias, solicitante), "monto": monto, "motivo": motivo}
    r = s.cliente.post("/api/solicitudes", headers=_cabeceras(s, solicitante), json=cuerpo)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _resolver(s, nombre, accion, solicitud_id):
    r = s.cliente.post(f"/api/solicitudes/{solicitud_id}/{accion}", headers=_cabeceras(s, nombre))
    assert r.status_code == 200, r.text


def _recientes(s, nombre):
    r = s.cliente.get("/api/movimientos/recientes", headers=_cabeceras(s, nombre), params={"limite": 20})
    assert r.status_code == 200, r.text
    return r.json()


def _sms(s, celular):
    return [m["mensaje"] for m in s.cliente.get("/api/pruebas/notificaciones", params={"celular": celular}).json()]


def _lista(texto):
    return [parte.strip() for parte in texto.split(",")] if texto.strip() else []


def _avanzar_reloj(s, minutos):
    r = s.cliente.put("/api/pruebas/reloj", json={"avanzar_minutos": minutos})
    assert r.status_code == 200, r.text


def _codigo_operacion(s):
    """Código de la respuesta actual o, si no lo trae (por ejemplo un 204), el de la transferencia previa."""
    try:
        cuerpo = s.respuesta.json()
    except ValueError:
        cuerpo = None
    if isinstance(cuerpo, dict) and cuerpo.get("codigo_operacion"):
        return cuerpo["codigo_operacion"]
    return s.codigo_operacion


def _foto(s):
    """Saldo, contactos y solicitudes de los cuatro usuarios, con tokens propios para no tocar los del escenario."""
    tokens = vars(s).setdefault("tokens_foto", {})
    foto = {}
    for nombre, (celular, pin) in conftest.USUARIOS.items():
        datos = []
        for ruta in ("/api/cuentas/me/saldo", "/api/contactos", "/api/solicitudes"):
            r = s.cliente.get(ruta, headers=tokens.get(nombre))
            if r.status_code == 401:  # Primera vez, o el reloj avanzó y el token venció.
                login = s.cliente.post("/api/auth/login", json={"celular": celular, "pin": pin})
                tokens[nombre] = {"Authorization": f"Bearer {login.json()['access_token']}"}
                r = s.cliente.get(ruta, headers=tokens[nombre])
            datos.append(r.json())
        foto[nombre] = datos
    return foto


def _a_la_vez(peticiones):
    """Envía las peticiones a la vez: un cliente por hilo, con la conexión abierta antes de soltar la barrera."""
    barrera = threading.Barrier(len(peticiones))
    respuestas = [None] * len(peticiones)

    def enviar(i, metodo, ruta, cabeceras, cuerpo):
        with httpx.Client(base_url=conftest.URL, timeout=30) as cliente:
            cliente.get("/api/salud")
            barrera.wait(timeout=30)
            respuestas[i] = cliente.request(metodo, ruta, headers=cabeceras, json=cuerpo)

    hilos = [threading.Thread(target=enviar, args=(i, *peticion)) for i, peticion in enumerate(peticiones)]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    assert None not in respuestas, "Algún hilo no recibió respuesta"
    return respuestas


def _cuerpo_valido(metodo, ruta):
    """Cuerpo que la operación aceptaría con un token válido: así un 401 prueba solo la autenticación."""
    if metodo == "POST" and ruta == "/api/contactos":
        return {"celular": "998877665", "alias": "Diego"}
    if metodo == "PUT" and ruta.startswith("/api/contactos/"):
        return {"favorito": False}
    if metodo == "POST" and ruta == "/api/solicitudes":
        return {"contacto_id": 1, "monto": "10.00", "motivo": "Motivo valido"}
    if metodo == "POST" and ruta.endswith("/rechazar"):
        return {"motivo": "No corresponde"}
    return None


def _credencial(s, credencial):
    if credencial == "ninguna":
        return {}
    if credencial == "token basura":
        return {"Authorization": "Bearer abc.def.ghi"}
    m = re.fullmatch(r"token de (Ana|Bruno|Carla|Diego)( sin el prefijo Bearer| con el esquema Basic)?", credencial)
    assert m, f"Credencial desconocida: {credencial}"
    token = _cabeceras(s, m[1])["Authorization"].removeprefix("Bearer ")
    if m[2] == " sin el prefijo Bearer":
        return {"Authorization": token}
    if m[2] == " con el esquema Basic":
        return {"Authorization": f"Basic {token}"}
    return {"Authorization": f"Bearer {token}"}


def _contrato(s):
    if not _CONTRATO:
        _CONTRATO.update(s.cliente.get("/openapi.json").json())
    return _CONTRATO


# ---------- Dado ----------

@given(parsers.parse('que el usuario de carga "{celular}" ingresó a Qolqe'))
def usuario_de_carga_ingreso(s, celular):
    _cabeceras(s, celular)
    s.actual = celular


@given(parsers.re(rf'{_NOMBRE} agregó el contacto "(?P<celular>\d+)" con alias "(?P<alias>[^"]+)"'))
def agrego_contacto_g4(s, nombre, celular, alias):
    r = s.cliente.post("/api/contactos", headers=_cabeceras(s, nombre), json={"celular": celular, "alias": alias})
    assert r.status_code == 201, r.text


@given(parsers.re(rf'{_NOMBRE} eliminó su contacto "(?P<alias>[^"]+)"'))
def elimino_contacto_g4(s, nombre, alias):
    r = s.cliente.delete(f"/api/contactos/{_contacto_id(s, alias, nombre)}", headers=_cabeceras(s, nombre))
    assert r.status_code == 204, r.text


@given(parsers.re(rf'{_NOMBRE} desmarcó como favorito su contacto "(?P<alias>[^"]+)"'))
def desmarco_favorito_g4(s, nombre, alias):
    r = s.cliente.put(f"/api/contactos/{_contacto_id(s, alias, nombre)}", headers=_cabeceras(s, nombre),
                      json={"favorito": False})
    assert r.status_code == 200, r.text


@given(parsers.re(rf"{_NOMBRE} (?P<accion>rechazó|canceló) la solicitud"))
def resolvio_solicitud_g4(s, nombre, accion):
    _resolver(s, nombre, {"rechazó": "rechazar", "canceló": "cancelar"}[accion], s.solicitud_id)


@given(parsers.re(rf'{_NOMBRE} envió (?P<total>\d+) solicitudes a su contacto "(?P<alias>[^"]+)"'))
def envio_solicitudes_a_contacto(s, nombre, total, alias):
    for i in range(int(total)):
        s.solicitud_id = _solicitar(s, nombre, alias, "1.00", f"Solicitud {i}")


@given(parsers.re(rf'{_NOMBRE} tiene una solicitud enviada a su contacto "(?P<alias>[^"]+)" en cada estado final'))
def solicitud_en_cada_estado(s, nombre, alias):
    destinatario = _nombre_de(next(c["celular"] for c in _contactos(s, nombre) if c["alias"] == alias))
    _resolver(s, destinatario, "aceptar", _solicitar(s, nombre, alias, "5.00", "Para aceptar"))
    _resolver(s, destinatario, "rechazar", _solicitar(s, nombre, alias, "5.00", "Para rechazar"))
    _resolver(s, nombre, "cancelar", _solicitar(s, nombre, alias, "5.00", "Para cancelar"))


@given(parsers.re(rf"(?:que )?{_NOMBRE} recibió solicitudes de (?P<monto>\d+\.\d\d) de (?P<uno>Ana|Bruno|Carla|Diego) "
                  r"y de (?P<otro>Ana|Bruno|Carla|Diego)"))
def recibio_solicitudes(s, nombre, monto, uno, otro):
    s.solicitudes_simultaneas = []
    for solicitante in (uno, otro):
        s.solicitar_entre(solicitante, nombre, monto)
        s.solicitudes_simultaneas.append(s.solicitud_id)


@given(parsers.re(rf"pasaron (?P<horas>\d+) horas desde la última solicitud de {_NOMBRE}"))
def pasaron_horas_desde_solicitud(s, horas, nombre):
    # Se fija la hora exacta para que los segundos transcurridos no cambien el valor límite.
    ultima = max(e["creada_en"] for e in _solicitudes(s, nombre)["enviadas"])
    momento = datetime.fromisoformat(ultima) + timedelta(hours=int(horas))
    assert s.cliente.put("/api/pruebas/reloj", json={"ahora": momento.isoformat()}).status_code == 200
    s.tokens.clear()  # Los tokens vencieron con el salto: los pasos siguientes vuelven a ingresar.


@given(parsers.re(r"pasaron (?P<horas>\d+) horas en el reloj de Qolqe"))
def pasaron_horas(s, horas):
    _avanzar_reloj(s, int(horas) * 60)
    s.tokens.clear()


@given(parsers.re(r"pasaron (?P<minutos>\d+) minutos en el reloj de Qolqe desde el ingreso"))
def pasaron_minutos_sin_reingresar(s, minutos):
    _avanzar_reloj(s, int(minutos))


@given(parsers.re(rf"{_NOMBRE} cerró sesión"))
def cerro_sesion_g4(s, nombre):
    r = s.cliente.post("/api/auth/logout", headers=_cabeceras(s, nombre))
    assert r.status_code == 204, r.text


@given("se registran los saldos, contactos y solicitudes de los cuatro usuarios")
def registra_foto(s):
    s.foto = _foto(s)


# ---------- Cuando ----------

@when(parsers.re(rf"{_NOMBRE} envía el alta de contacto con celular (?P<celular>.+?) y alias (?P<alias>.+)"))
def envia_alta_literal(s, nombre, celular, alias):
    _pedir(s, "POST", "/api/contactos", nombre, json={"celular": json.loads(celular), "alias": json.loads(alias)})


@when(parsers.re(rf"{_NOMBRE} consulta la página (?P<pagina>\d+) de sus contactos"))
def consulta_pagina(s, nombre, pagina):
    _pedir(s, "GET", "/api/contactos", nombre, params={"pagina": pagina})


@when(parsers.re(rf'{_NOMBRE} busca entre sus contactos el texto (?P<texto>"[^"]*")(?: en la página (?P<pagina>\d+))?'))
def busca_texto_literal(s, nombre, texto, pagina):
    parametros = {"buscar": json.loads(texto)}
    if pagina:
        parametros["pagina"] = pagina
    _pedir(s, "GET", "/api/contactos", nombre, params=parametros)


@when(parsers.re(rf'{_NOMBRE} (?P<accion>marca|desmarca) como favorito su contacto "(?P<alias>[^"]+)"'))
def cambia_favorito(s, nombre, accion, alias):
    s.duenio_contacto = nombre
    _pedir(s, "PUT", f"/api/contactos/{_contacto_id(s, alias, nombre)}", nombre, json={"favorito": accion == "marca"})


@when(parsers.re(rf'{_NOMBRE} modifica su contacto "(?P<alias>[^"]+)" con el cuerpo (?P<cuerpo>\{{.*\}})'))
def modifica_contacto(s, nombre, alias, cuerpo):
    s.duenio_contacto = nombre
    _pedir(s, "PUT", f"/api/contactos/{_contacto_id(s, alias, nombre)}", nombre, json=json.loads(cuerpo))


@when(parsers.re(rf'{_NOMBRE} elimina su contacto "(?P<alias>[^"]+)"'))
def elimina_su_contacto(s, nombre, alias):
    _pedir(s, "DELETE", f"/api/contactos/{_contacto_id(s, alias, nombre)}", nombre)


@when(parsers.re(rf'{_NOMBRE} solicita (?P<monto>\d+(?:\.\d+)?) a su contacto "(?P<alias>[^"]+)" por "(?P<motivo>[^"]+)"'))
def solicita_a_contacto(s, nombre, monto, alias, motivo):
    r = _pedir(s, "POST", "/api/solicitudes", nombre,
               json={"contacto_id": _contacto_id(s, alias, nombre), "monto": monto, "motivo": motivo})
    if r.status_code == 201:
        s.solicitud_id = r.json()["id"]


@when(parsers.re(rf'{_NOMBRE} envía a su contacto "(?P<alias>[^"]+)" una solicitud con monto (?P<monto>.+?) '
                 r'y motivo (?P<motivo>".*")'))
def envia_solicitud_literal(s, nombre, alias, monto, motivo):
    cuerpo = {"contacto_id": _contacto_id(s, alias, nombre), "monto": json.loads(monto), "motivo": json.loads(motivo)}
    r = _pedir(s, "POST", "/api/solicitudes", nombre, json=cuerpo)
    if r.status_code == 201:
        s.solicitud_id = r.json()["id"]


@when(parsers.re(rf"{_NOMBRE} consulta todas sus solicitudes"))
def consulta_todas_las_solicitudes(s, nombre):
    _pedir(s, "GET", "/api/solicitudes", nombre)


@when(parsers.re(rf'{_NOMBRE} filtra sus solicitudes por el estado (?P<estado>"[^"]*")'))
def filtra_solicitudes(s, nombre, estado):
    _pedir(s, "GET", "/api/solicitudes", nombre, params={"estado": json.loads(estado)})


@when(parsers.re(rf"{_NOMBRE} rechaza la solicitud con el cuerpo (?P<cuerpo>.+)"))
def rechaza_con_cuerpo(s, nombre, cuerpo):
    ruta = f"/api/solicitudes/{s.solicitud_id}/rechazar"
    if cuerpo == _SIN_CUERPO:
        _pedir(s, "POST", ruta, nombre)
    else:
        _pedir(s, "POST", ruta, nombre, json=json.loads(cuerpo))


@when(parsers.re(rf"{_NOMBRE} acepta la misma solicitud (?P<veces>\d+) veces a la vez"))
def acepta_a_la_vez(s, nombre, veces):
    peticion = ("POST", f"/api/solicitudes/{s.solicitud_id}/aceptar", _cabeceras(s, nombre), None)
    s.respuestas = _a_la_vez([peticion] * int(veces))


@when(parsers.re(rf"{_NOMBRE} acepta a la vez las solicitudes que recibió"))
def acepta_varias_a_la_vez(s, nombre):
    cabeceras = _cabeceras(s, nombre)
    s.respuestas = _a_la_vez([("POST", f"/api/solicitudes/{i}/aceptar", cabeceras, None)
                              for i in s.solicitudes_simultaneas])


@when(parsers.re(rf'{_NOMBRE} agrega (?P<veces>\d+) veces a la vez el celular "(?P<celular>\d+)"'))
def agrega_a_la_vez(s, nombre, veces, celular):
    cabeceras = _cabeceras(s, nombre)
    s.respuestas = _a_la_vez([("POST", "/api/contactos", cabeceras, {"celular": celular, "alias": f"Alias {i}"})
                              for i in range(1, int(veces) + 1)])


@when(parsers.re(rf"{_NOMBRE} envía (?P<metodo>GET|POST|PUT|DELETE|PATCH|OPTIONS) (?P<ruta>/\S*)"
                 r'(?: con el cuerpo (?P<cuerpo>.+?))?(?: y el tipo "(?P<tipo>[^"]+)")?'))
def envia_peticion(s, nombre, metodo, ruta, cuerpo, tipo):
    """El cuerpo va tal cual (puede ser un JSON mal formado); "(sin cuerpo)" no envía nada."""
    if cuerpo is None or cuerpo == _SIN_CUERPO:
        _pedir(s, metodo, ruta, nombre)
        return
    cabeceras = {**_cabeceras(s, nombre), "Content-Type": tipo or "application/json"}
    s.respuesta = s.cliente.request(metodo, ruta, headers=cabeceras, content=cuerpo.encode())


@when(parsers.re(r'se envía (?P<metodo>GET|POST|PUT|DELETE) (?P<ruta>/\S*) con la credencial "(?P<credencial>[^"]+)"'))
def envia_con_credencial(s, metodo, ruta, credencial):
    s.respuesta = s.cliente.request(metodo, ruta, headers=_credencial(s, credencial),
                                    json=_cuerpo_valido(metodo, ruta))


# ---------- Entonces ----------

@then(parsers.re(r'el contacto (?:"(?P<alias>[^"]+)" de la respuesta|devuelto) tiene nombre "(?P<nombre>[^"]+)", '
                 r'celular "(?P<celular>\d+)" y (?P<marca>es favorito|no es favorito)'))
def contacto_informado(s, alias, nombre, celular, marca):
    cuerpo = s.respuesta.json()
    contacto = next(c for c in cuerpo["contactos"] if c["alias"] == alias) if alias else cuerpo
    assert (contacto["nombre"], contacto["celular"], contacto["favorito"]) == (nombre, celular, marca == "es favorito")


@then(parsers.re(rf'la lista de contactos de {_NOMBRE} queda "(?P<lista>[^"]*)"'))
def lista_de_contactos(s, nombre, lista):
    assert [c["alias"] for c in _contactos(s, nombre)] == _lista(lista)


@then(parsers.re(r'los contactos de la página están en el orden "(?P<lista>[^"]*)"'))
def orden_de_la_pagina(s, lista):
    assert [c["alias"] for c in s.respuesta.json()["contactos"]] == _lista(lista)


@then(parsers.re(r"la página (?P<pagina>\d+) trae (?P<cantidad>\d+) contactos con total (?P<total>\d+) "
                 r"y total_paginas (?P<paginas>\d+)"))
def pagina_informada(s, pagina, cantidad, total, paginas):
    c = s.respuesta.json()
    assert (c["pagina"], len(c["contactos"]), c["total"], c["total_paginas"], c["por_pagina"]) == (
        int(pagina), int(cantidad), int(total), int(paginas), 10)


@then(parsers.re(rf"{_NOMBRE} queda con (?P<total>\d+) (?P<que>contactos|favoritos)"))
def queda_con(s, nombre, total, que):
    contactos = _contactos(s, nombre)
    cantidad = len(contactos) if que == "contactos" else sum(c["favorito"] for c in contactos)
    assert cantidad == int(total)


@then(parsers.re(r'el contacto queda con alias "(?P<alias>[^"]*)" y (?P<marca>es favorito|no es favorito)'))
def contacto_queda(s, alias, marca):
    esperado = (alias, marca == "es favorito")
    cuerpo = s.respuesta.json()
    assert (cuerpo["alias"], cuerpo["favorito"]) == esperado
    guardado = next(c for c in _contactos(s, s.duenio_contacto) if c["id"] == cuerpo["id"])
    assert (guardado["alias"], guardado["favorito"]) == esperado


@then(parsers.re(rf'{_NOMBRE} tiene el celular "(?P<celular>\d+)" una sola vez entre sus contactos'))
def celular_una_vez(s, nombre, celular):
    celulares = [c["celular"] for c in _contactos(s, nombre)]
    assert celulares.count(celular) == 1, celulares


@then(parsers.re(rf'{_NOMBRE} todavía ve la solicitud "(?P<motivo>[^"]+)" en estado "(?P<estado>[A-Z]+)"'))
def todavia_ve_solicitud(s, nombre, motivo, estado):
    datos = _solicitudes(s, nombre)
    assert [x["estado"] for x in datos["enviadas"] + datos["recibidas"] if x["motivo"] == motivo] == [estado]


@then(parsers.re(rf'{_NOMBRE} tiene el movimiento reciente "(?P<tipo>TRANSFERENCIA_ENVIADA|TRANSFERENCIA_RECIBIDA)" '
                 r'por "(?P<importe>-?\d+\.\d\d)" con el código de la operación(?: y la descripción "(?P<descripcion>[^"]+)")?'))
def movimiento_reciente(s, nombre, tipo, importe, descripcion):
    # /api/movimientos/recientes filtra por usuario e incluye el día de hoy (RN-10).
    codigo = _codigo_operacion(s)
    movimientos = [m for m in _recientes(s, nombre) if m["codigo_operacion"] == codigo and m["tipo"] == tipo]
    assert len(movimientos) == 1, movimientos
    assert movimientos[0]["importe"] == importe
    if descripcion:
        assert movimientos[0]["descripcion"] == descripcion


@then(parsers.re(r'ningún movimiento reciente de (?P<uno>Ana|Bruno|Carla|Diego) ni de (?P<otro>Ana|Bruno|Carla|Diego) '
                 r'dice "(?P<texto>[^"]+)"'))
def sin_movimientos(s, uno, otro, texto):
    for nombre in (uno, otro):
        assert all(m["descripcion"] != texto for m in _recientes(s, nombre)), nombre


@then(parsers.re(rf"{_NOMBRE} no tiene solicitudes enviadas"))
def sin_solicitudes_enviadas(s, nombre):
    assert _solicitudes(s, nombre)["enviadas"] == []


@then(parsers.re(r'la solicitud creada tiene monto "(?P<monto>[^"]+)" y motivo "(?P<motivo>[^"]+)"'))
def solicitud_creada_con(s, monto, motivo):
    cuerpo = s.respuesta.json()
    assert (cuerpo["monto"], cuerpo["motivo"]) == (monto, motivo)


@then(parsers.re(r'la solicitud creada tiene solicitante "(?P<solicitante>[^"]+)" \((?P<cel_solicitante>\d+)\), '
                 r'destinatario "(?P<destinatario>[^"]+)" \((?P<cel_destinatario>\d+)\) y aún no tiene resolución'))
def solicitud_creada_participantes(s, solicitante, cel_solicitante, destinatario, cel_destinatario):
    c = s.respuesta.json()
    assert c["solicitante"] == {"nombre": solicitante, "celular": cel_solicitante}
    assert c["destinatario"] == {"nombre": destinatario, "celular": cel_destinatario}
    assert (c["resuelta_en"], c["motivo_rechazo"], c["codigo_operacion"]) == (None, None, None)


@then(parsers.re(r'el SMS a "(?P<celular>\d+)" indica el monto, el motivo y la fecha de vencimiento de la solicitud'))
def sms_de_solicitud(s, celular):
    c = s.respuesta.json()
    partes = (f"S/ {c['monto']}", f'"{c["motivo"]}"', f"Vence el {datetime.fromisoformat(c['vence_en']):%d/%m a las %H:%M}")
    mensajes = _sms(s, celular)
    assert any(all(parte in m for parte in partes) for m in mensajes), (partes, mensajes)


@then(parsers.re(r'las enviadas son "(?P<enviadas>[^"]*)" y las recibidas son "(?P<recibidas>[^"]*)"'))
def enviadas_y_recibidas(s, enviadas, recibidas):
    datos = s.respuesta.json()
    assert [f"{x['motivo']} ({x['estado']})" for x in datos["enviadas"]] == _lista(enviadas)
    assert [f"{x['motivo']} ({x['estado']})" for x in datos["recibidas"]] == _lista(recibidas)


@then(parsers.re(r"la solicitud aparece igual en las enviadas de (?P<solicitante>Ana|Bruno|Carla|Diego) "
                 r"y en las recibidas de (?P<destinatario>Ana|Bruno|Carla|Diego)"))
def doble_perspectiva(s, solicitante, destinatario):
    enviada = [x for x in _solicitudes(s, solicitante)["enviadas"] if x["id"] == s.solicitud_id]
    recibida = [x for x in _solicitudes(s, destinatario)["recibidas"] if x["id"] == s.solicitud_id]
    assert enviada == recibida and len(enviada) == 1


@then(parsers.re(r'"(?P<celular>\d+)" no recibió un SMS que contenga "(?P<texto>[^"]+)"'))
def no_recibio_sms(s, celular, texto):
    mensajes = _sms(s, celular)
    assert not any(texto in m for m in mensajes), mensajes


@then(parsers.re(rf'{_NOMBRE} usó hoy "(?P<monto>\d+\.\d\d)" de su límite diario'))
def uso_del_limite(s, nombre, monto):
    assert s.cliente.get("/api/limites", headers=_cabeceras(s, nombre)).json()["usado_hoy"] == monto


@then(parsers.re(r'el SMS de aceptación a "(?P<celular>\d+)" incluye el código de la operación'))
def sms_de_aceptacion(s, celular):
    codigo = s.respuesta.json()["codigo_operacion"]
    mensajes = _sms(s, celular)
    assert any("aceptó tu solicitud" in m and f"Operación {codigo}." in m for m in mensajes), mensajes


@then("la solicitud resuelta tiene fecha de resolución")
def fecha_de_resolucion(s):
    c = s.respuesta.json()
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d", c["resuelta_en"] or ""), c
    assert c["resuelta_en"] >= c["creada_en"]


@then(parsers.re(r"la solicitud queda con motivo_rechazo (?P<valor>.+)"))
def motivo_de_rechazo(s, valor):
    esperado = json.loads(valor)
    cuerpo = s.respuesta.json()
    assert cuerpo["motivo_rechazo"] == esperado
    enviadas = _solicitudes(s, _nombre_de(cuerpo["solicitante"]["celular"]))["enviadas"]
    assert next(x for x in enviadas if x["id"] == cuerpo["id"])["motivo_rechazo"] == esperado


@then(parsers.re(r'solo una de las peticiones simultáneas responde (?P<exito>\d{3}) y las demás (?P<estado>\d{3}) '
                 r'"(?P<codigo>[A-Z_]+)"'))
def una_sola_gana(s, exito, estado, codigo):
    estados = [r.status_code for r in s.respuestas]
    assert estados.count(int(exito)) == 1, estados
    for r in s.respuestas:
        if r.status_code != int(exito):
            assert (r.status_code, r.json()["codigo"]) == (int(estado), codigo), r.text


@then("ningún saldo, contacto ni solicitud cambió")
def nada_cambio(s):
    assert _foto(s) == s.foto


@then(parsers.re(r'el error de validación nombra el campo "(?P<campo>[^"]+)"'))
def error_de_campo(s, campo):
    cuerpo = s.respuesta.json()
    assert cuerpo["codigo"] == "SOLICITUD_INVALIDA", cuerpo
    assert campo in [e["campo"] for e in cuerpo["errores"]], cuerpo


@then("el error indica que el JSON está mal formado")
def json_mal_formado(s):
    cuerpo = s.respuesta.json()
    assert cuerpo["codigo"] == "SOLICITUD_INVALIDA", cuerpo
    assert any(e["mensaje"] == "JSON decode error" for e in cuerpo["errores"]), cuerpo


@then("la respuesta es un error del cliente con código y detalle")
def error_del_cliente(s):
    assert s.respuesta.status_code in (404, 422), s.respuesta.text
    cuerpo = s.respuesta.json()
    assert cuerpo["codigo"] and cuerpo["detail"], cuerpo


@then(parsers.re(r'la respuesta incluye la cabecera "(?P<cabecera>[^"]+)"'))
def incluye_cabecera(s, cabecera):
    assert s.respuesta.headers.get(cabecera), dict(s.respuesta.headers)


@then(parsers.re(r'la cabecera Allow lista los métodos "(?P<metodos>[^"]+)"'))
def cabecera_allow(s, metodos):
    permitidos = {m.strip() for m in s.respuesta.headers.get("allow", "").split(",")}
    assert permitidos == set(_lista(metodos))


@then(parsers.re(r'la respuesta trae "(?P<campo>[^"]+)" con el valor (?P<valor>.+)'))
def respuesta_trae(s, campo, valor):
    assert s.respuesta.json()[campo] == json.loads(valor), s.respuesta.text


@then(parsers.re(r'la respuesta cumple el contrato OpenAPI de "(?P<metodo>[A-Z]+) (?P<plantilla>/\S+)"'))
def cumple_contrato(s, metodo, plantilla):
    contrato = _contrato(s)
    respuesta = contrato["paths"][plantilla][metodo.lower()]["responses"][str(s.respuesta.status_code)]
    contenido = respuesta.get("content", {}).get("application/json")
    if contenido is None:
        assert s.respuesta.content == b""
        return
    assert s.respuesta.headers["content-type"].startswith("application/json")
    validador = jsonschema_rs.Draft202012Validator({**contenido["schema"], "components": contrato["components"]})
    errores = [str(e) for e in validador.iter_errors(s.respuesta.json())]
    assert not errores, errores


@then(parsers.re(r'el detalle del error es "(?P<detalle>[^"]+)"'))
def detalle_del_error(s, detalle):
    assert s.respuesta.json()["detail"] == detalle


@then("la respuesta pide autenticarse con Bearer")
def pide_bearer(s):
    assert s.respuesta.headers.get("www-authenticate") == "Bearer"
