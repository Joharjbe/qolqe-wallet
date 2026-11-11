"""Pasos de pytest-bdd del núcleo: registro, sesión, saldo y perfil (HU-N-01 a HU-N-05)."""
import re
import threading
import time
from collections import Counter
from datetime import datetime, timedelta

import conftest  # Helpers compartidos: URL, USUARIOS, Sesiones.
import httpx
import jwt
from pytest_bdd import given, parsers, then, when

CLAVE_POR_DEFECTO = "qolqe-clave-de-desarrollo-no-usar-en-produccion"


def _registro_base(celular):
    """Cuerpo de registro válido salvo el campo que el caso quiera variar."""
    return {"dni": "12345678", "nombres": "Nombre Valido", "celular": celular, "pin": "4826"}


def _expandir(texto):
    """Permite tablas legibles: '80xa' = 80 letras 'a'; '80xa_SP' agrega espacios al inicio y al final.

    También traduce centinelas para valores con espacios, imposibles de escribir en una celda Gherkin.
    """
    centinelas = {"SOLO_ESPACIOS": "   ", "ESPACIO_A": " a  ", "80xa_CON_ESPACIOS": "  " + "a" * 80 + "  ",
                  "ANA_CON_ESPACIOS": "  Ana Lucía Torres  "}
    if texto in centinelas:
        return centinelas[texto]
    coincidencia = re.fullmatch(r"(\d+)x(.)", texto)
    if coincidencia:
        return coincidencia.group(2) * int(coincidencia.group(1))
    return texto


def _cabecera(token):
    return {"Authorization": f"Bearer {token}"}


def _login(s, celular, pin, dispositivo=None):
    cuerpo = {"celular": celular, "pin": pin}
    if dispositivo is not None:
        cuerpo["dispositivo_id"] = dispositivo
    return s.cliente.post("/api/auth/login", json=cuerpo)


def _entrar(s, nombre):
    """Inicia sesión por nombre, recuerda token, cabecera actual y respuesta."""
    celular, pin = conftest.USUARIOS[nombre]
    r = _login(s, celular, pin)
    s.respuesta = r
    if r.status_code == 200:
        s.login = r.json()
        s.tokens[nombre] = _cabecera(s.login["access_token"])
        s.cab = s.tokens[nombre]
    return r


def _simultaneo(peticiones):
    """Lanza N peticiones a la vez (un cliente por hilo, sincronizadas con Barrier)."""
    clientes = [httpx.Client(base_url=conftest.URL, timeout=30) for _ in peticiones]
    for cliente in clientes:
        cliente.get("/api/salud")  # Calienta la conexión para que la carrera sea real.
    barrera = threading.Barrier(len(peticiones))
    respuestas = [None] * len(peticiones)

    def correr(indice):
        metodo, ruta, opciones = peticiones[indice]
        barrera.wait()
        respuestas[indice] = clientes[indice].request(metodo, ruta, **opciones)

    hilos = [threading.Thread(target=correr, args=(i,)) for i in range(len(peticiones))]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
    for cliente in clientes:
        cliente.close()
    return Counter(r.status_code for r in respuestas)


def _contar_sms(s, celular):
    return len(s.cliente.get("/api/pruebas/notificaciones", params={"celular": celular}).json())


# ================= HU-N-01: Registrarme =================

@when("se registra la cuenta de ejemplo de Lucía")
def _registra_ejemplo(s):
    s.respuesta = s.cliente.post("/api/usuarios", json={
        "dni": "12345678", "nombres": "Lucía Fernández Rojas", "celular": "987000111",
        "pin": "4826", "correo": "Lucia.F@Correo.PE"})
    s.ultimo_celular, s.ultimo_pin = "987000111", "4826"


@when(parsers.parse('se registra a {celular} con nombres "{nombres}"'))
def _registra_nombres(s, celular, nombres):
    cuerpo = _registro_base(celular)
    cuerpo["nombres"] = _expandir(nombres)
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)
    s.ultimo_celular, s.ultimo_pin = celular, "4826"


@when(parsers.parse('se registra a {celular} con DNI "{dni}"'))
def _registra_dni(s, celular, dni):
    cuerpo = _registro_base(celular)
    cuerpo["dni"] = dni
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)


@when(parsers.parse('se registra con el celular "{celular}"'))
def _registra_celular(s, celular):
    s.respuesta = s.cliente.post("/api/usuarios", json=_registro_base(celular))


@when(parsers.parse('se registra a {celular} con PIN "{pin}"'))
def _registra_pin(s, celular, pin):
    cuerpo = _registro_base(celular)
    cuerpo["pin"] = pin
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)


@when(parsers.parse('se registra a {celular} con correo "{correo}"'))
def _registra_correo(s, celular, correo):
    cuerpo = _registro_base(celular)
    cuerpo["correo"] = correo
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)


@when(parsers.parse('se registra a {celular} con un correo de {largo:d} caracteres'))
def _registra_correo_largo(s, celular, largo):
    cuerpo = _registro_base(celular)
    cuerpo["correo"] = "a" * (largo - 5) + "@x.pe"
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)


@when(parsers.parse('se registra a {celular} con el correo {variante}'))
def _registra_correo_opcional(s, celular, variante):
    cuerpo = _registro_base(celular)
    if variante == "vacío":
        cuerpo["correo"] = ""
    elif variante == "espacios":
        cuerpo["correo"] = "   "
    elif variante == "nulo":
        cuerpo["correo"] = None
    # "omitido": no se agrega el campo.
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)
    s.ultimo_celular, s.ultimo_pin = celular, "4826"


@when(parsers.parse('se registra con dni "{dni}", celular "{celular}", pin "{pin}" y correo "{correo}"'))
def _registra_prioridad(s, dni, celular, pin, correo):
    cuerpo = {"dni": dni, "nombres": "Nombre Valido", "celular": celular, "pin": pin}
    if correo != "-":
        cuerpo["correo"] = correo
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)


@when(parsers.parse('se registra agregando campos ajenos con celular "{celular}"'))
def _registra_campos_ajenos(s, celular):
    cuerpo = _registro_base(celular)
    cuerpo.update({"saldo": "9999", "estado": "CERRADA", "limite_diario": "9000", "id": 1})
    s.respuesta = s.cliente.post("/api/usuarios", json=cuerpo)
    s.ultimo_celular, s.ultimo_pin = celular, "4826"


@when(parsers.parse('se envía al registro la variante "{variante}"'))
def _registra_variante_invalida(s, variante):
    base = _registro_base("987000141")
    if variante == "cuerpo vacío":
        s.respuesta = s.cliente.post("/api/usuarios", json={})
    elif variante.startswith("sin "):
        base.pop(variante[4:])
        s.respuesta = s.cliente.post("/api/usuarios", json=base)
    elif variante == "dni numérico":
        s.respuesta = s.cliente.post("/api/usuarios", json={**base, "dni": 12345678})
    elif variante == "pin numérico":
        s.respuesta = s.cliente.post("/api/usuarios", json={**base, "pin": 4826})
    elif variante == "nombres nulo":
        s.respuesta = s.cliente.post("/api/usuarios", json={**base, "nombres": None})
    elif variante == "json mal formado":
        s.respuesta = s.cliente.post("/api/usuarios", content=b"{mal",
                                     headers={"Content-Type": "application/json"})
    elif variante == "formulario":
        s.respuesta = s.cliente.post("/api/usuarios", data=base)


@when(parsers.parse('{cantidad:d} usuarios se registran a la vez con el celular "{celular}"'))
def _registro_simultaneo_celular(s, cantidad, celular):
    peticiones = [("POST", "/api/usuarios",
                   {"json": {"dni": f"1234567{i}", "nombres": "Carrera Celular", "celular": celular, "pin": "4826"}})
                  for i in range(cantidad)]
    s.resultado_simultaneo = _simultaneo(peticiones)


@when(parsers.parse('{cantidad:d} usuarios se registran a la vez con el correo "{correo}"'))
def _registro_simultaneo_correo(s, cantidad, correo):
    peticiones = [("POST", "/api/usuarios",
                   {"json": {"dni": "12345678", "nombres": "Carrera Correo",
                             "celular": f"9871231{20 + i:02d}", "pin": "4826", "correo": correo}})
                  for i in range(cantidad)]
    s.resultado_simultaneo = _simultaneo(peticiones)


@then(parsers.parse('el usuario registrado tiene nombres "{nombres}", celular "{celular}" y correo "{correo}"'))
def _registrado_datos(s, nombres, celular, correo):
    cuerpo = s.respuesta.json()
    assert (cuerpo["nombres"], cuerpo["celular"], cuerpo["correo"]) == (nombres, celular, correo), cuerpo
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", cuerpo["creado_en"]), cuerpo["creado_en"]


@then("el cuerpo del registro no incluye DNI ni PIN")
def _registro_sin_secretos(s):
    cuerpo = s.respuesta.json()
    assert "dni" not in cuerpo and "pin" not in cuerpo and "pin_hash" not in cuerpo, cuerpo


@then("el correo del nuevo usuario es nulo")
def _nuevo_sin_correo(s):
    r = _login(s, s.ultimo_celular, s.ultimo_pin)
    assert r.status_code == 200, r.text
    perfil = s.cliente.get("/api/cuentas/me", headers=_cabecera(r.json()["access_token"])).json()
    assert perfil["correo"] is None, perfil


# ================= HU-N-02: Iniciar sesión =================

@when(parsers.parse("{nombre} inicia sesión"))
def _inicia_sesion(s, nombre):
    _entrar(s, nombre)


@given(parsers.parse("{nombre} abre dos sesiones"))
@when(parsers.parse("{nombre} abre dos sesiones"))
def _abre_dos_sesiones(s, nombre):
    celular, pin = conftest.USUARIOS[nombre]
    s.sesion_par = [_login(s, celular, pin).json(), _login(s, celular, pin).json()]
    s.cab = _cabecera(s.sesion_par[1]["access_token"])


@when(parsers.parse('inicia sesión el celular "{celular}" con PIN "{pin}"'))
def _inicia_sesion_celular(s, celular, pin):
    r = _login(s, celular, pin)
    s.respuesta = r
    if r.status_code == 200:
        s.login = r.json()
        s.cab = _cabecera(s.login["access_token"])


@when(parsers.parse('ingresa con el celular "{celular}" y PIN "{pin}"'))
def _ingresa_celular_pin(s, celular, pin):
    r = _login(s, celular, pin)
    s.respuesta = r
    if r.status_code == 200:
        s.cab = _cabecera(r.json()["access_token"])


@when(parsers.parse("{nombre} falla el ingreso"))
def _falla_ingreso(s, nombre):
    celular = conftest.USUARIOS[nombre][0]
    s.respuesta = _login(s, celular, "0000")


@when(parsers.parse("{nombre} ingresa correctamente"))
def _ingresa_correcto(s, nombre):
    _entrar(s, nombre)
    assert s.respuesta.status_code == 200, s.respuesta.text


@when(parsers.parse("el reloj se adelanta {minutos:d} minutos"))
def _adelanta_reloj(s, minutos):
    assert s.cliente.put("/api/pruebas/reloj", json={"avanzar_minutos": minutos}).status_code == 200


@given(parsers.parse("que {nombre} está bloqueada por intentos fallidos"))
def _ya_bloqueada(s, nombre):
    celular = conftest.USUARIOS[nombre][0]
    for _ in range(3):
        _login(s, celular, "0000")


@when(parsers.parse("{nombre} recibe {cantidad:d} intentos fallidos simultáneos"))
def _intentos_simultaneos(s, nombre, cantidad):
    celular = conftest.USUARIOS[nombre][0]
    s.resultado_simultaneo = _simultaneo(
        [("POST", "/api/auth/login", {"json": {"celular": celular, "pin": "0000"}})] * cantidad)


@when(parsers.parse("{nombre} intenta ingresar con su PIN correcto"))
def _intenta_pin_correcto(s, nombre):
    celular, pin = conftest.USUARIOS[nombre]
    s.respuesta = _login(s, celular, pin)


@when(parsers.parse('{nombre} inicia sesión desde el dispositivo "{dispositivo}"'))
def _inicia_con_dispositivo(s, nombre, dispositivo):
    celular, pin = conftest.USUARIOS[nombre]
    r = _login(s, celular, pin, dispositivo=dispositivo)
    s.respuesta = r
    if r.status_code == 200:
        s.login = r.json()
        s.cab = _cabecera(s.login["access_token"])


@when(parsers.parse('se envía al login la variante "{variante}"'))
def _login_variante(s, variante):
    base = {"celular": "987654321", "pin": "4826"}
    if variante == "cuerpo vacío":
        s.respuesta = s.cliente.post("/api/auth/login", json={})
    elif variante == "sin pin":
        s.respuesta = s.cliente.post("/api/auth/login", json={"celular": "987654321"})
    elif variante == "pin numérico":
        s.respuesta = s.cliente.post("/api/auth/login", json={**base, "pin": 4826})
    elif variante == "dispositivo numérico":
        s.respuesta = s.cliente.post("/api/auth/login", json={**base, "dispositivo_id": 123})
    elif variante == "formulario":
        s.respuesta = s.cliente.post("/api/auth/login", data=base)
    elif variante == "método GET":
        s.respuesta = s.cliente.get("/api/auth/login")


@when(parsers.parse('Ana intenta ingresar con el dispositivo de prueba "{variante}"'))
def _ingreso_dispositivo_borde(s, variante):
    celular = conftest.USUARIOS["Ana"][0]
    if variante == "sin id":
        s.respuesta = _login(s, celular, "4826")
    elif variante == "id vacío":
        s.respuesta = _login(s, celular, "4826", dispositivo="")
    elif variante == "mayúsculas":
        s.respuesta = _login(s, celular, "4826", dispositivo="A1B2C3D4E5F60718")
    elif variante == "pin incorrecto":
        s.respuesta = _login(s, celular, "0000", dispositivo="nuevo-dispositivo")
    elif variante == "id numérico":
        s.respuesta = s.cliente.post("/api/auth/login",
                                     json={"celular": celular, "pin": "4826", "dispositivo_id": 123})


@then(parsers.parse('la sesión actual registra el dispositivo "{dispositivo}" con nombre "{nombre}"'))
def _sesion_dispositivo(s, dispositivo, nombre):
    sesiones = s.cliente.get("/api/seguridad/sesiones", headers=s.cab).json()
    actual = next(x for x in sesiones if x["actual"])
    esperado_nombre = None if nombre == "null" else nombre
    assert actual["dispositivo"] == {"id": dispositivo, "nombre": esperado_nombre}, actual


@then(parsers.parse('el dispositivo "{dispositivo}" de {nombre} no cambió su último ingreso'))
def _dispositivo_sin_cambios(s, dispositivo, nombre):
    cab = s.como(nombre)
    equipos = s.cliente.get("/api/seguridad/dispositivos", headers=cab).json()
    equipo = next(x for x in equipos if x["id"] == dispositivo)
    assert equipo["ultimo_ingreso"] is None, equipo


@when(parsers.parse('se cierra la cuenta actual con PIN "{pin}"'))
def _cierra_cuenta_actual(s, pin):
    s.respuesta = s.cliente.post("/api/cuentas/me/cierre", headers=s.cab, json={"pin": pin})


@then(parsers.parse("el token expira en {segundos:d} segundos"))
def _token_expira(s, segundos):
    cuerpo = s.login
    assert cuerpo["expires_in"] == segundos, cuerpo
    claims = jwt.decode(cuerpo["access_token"], options={"verify_signature": False})
    assert claims["exp"] - claims["iat"] == segundos, claims


@then(parsers.parse('el token identifica al usuario {uid:d} con celular "{celular}"'))
def _token_identifica(s, uid, celular):
    claims = jwt.decode(s.login["access_token"], options={"verify_signature": False})
    assert claims["sub"] == str(uid) and claims["cel"] == celular, claims
    assert s.login["usuario"]["id"] == uid and s.login["usuario"]["celular"] == celular, s.login


@then("la sesión creada figura como actual y vence a los 30 minutos")
def _sesion_actual(s):
    sesiones = s.cliente.get("/api/seguridad/sesiones", headers=s.cab).json()
    actual = next(x for x in sesiones if x["id"] == s.login["sesion_id"])
    assert actual["actual"] is True, actual
    delta = datetime.fromisoformat(actual["expira_en"]) - datetime.fromisoformat(actual["iniciada_en"])
    assert delta == timedelta(minutes=30), actual


@then("las dos sesiones son independientes")
def _dos_sesiones_independientes(s):
    a, b = s.sesion_par
    assert a["sesion_id"] != b["sesion_id"], (a, b)
    claims_a = jwt.decode(a["access_token"], options={"verify_signature": False})
    claims_b = jwt.decode(b["access_token"], options={"verify_signature": False})
    assert claims_a["jti"] != claims_b["jti"], (claims_a, claims_b)
    for sesion in (a, b):
        assert s.cliente.get("/api/cuentas/me", headers=_cabecera(sesion["access_token"])).status_code == 200


@then(parsers.parse('el saldo consultado es "{saldo}"'))
def _saldo_consultado(s, saldo):
    assert s.respuesta.json()["saldo"] == saldo, s.respuesta.text


@then(parsers.parse('la moneda consultada es "{moneda}"'))
def _moneda_consultada(s, moneda):
    assert s.respuesta.json()["moneda"] == moneda, s.respuesta.text


@then("el saldo consultado cumple el formato de centavos")
def _saldo_formato(s):
    assert re.fullmatch(r"-?\d+\.\d{2}", s.respuesta.json()["saldo"]), s.respuesta.text


@then(parsers.parse('"{celular}" tiene {cantidad:d} mensajes SMS'))
def _cuenta_sms(s, celular, cantidad):
    assert _contar_sms(s, celular) == cantidad, s.cliente.get(
        "/api/pruebas/notificaciones", params={"celular": celular}).json()


@then(parsers.parse('el mensaje de error es "{texto}"'))
def _mensaje_error(s, texto):
    assert s.respuesta.json()["detail"] == texto, s.respuesta.text


# ================= HU-N-03: Cerrar sesión =================

@when(parsers.parse("{nombre} cierra su sesión"))
def _cierra_sesion(s, nombre):
    _entrar(s, nombre)
    s.cab_cerrada = s.cab
    s.respuesta = s.cliente.post("/api/auth/logout", headers=s.cab_cerrada)


@when("con el token cerrado se consulta el saldo")
def _token_cerrado_saldo(s):
    s.respuesta = s.cliente.get("/api/cuentas/me/saldo", headers=s.cab_cerrada)


@when("con el token cerrado se edita el nombre")
def _token_cerrado_edita(s):
    s.respuesta = s.cliente.put("/api/cuentas/me", headers=s.cab_cerrada, json={"nombres": "Ana Cambiada"})


@when(parsers.parse("{nombre} cierra la primera sesión"))
def _cierra_primera(s, nombre):
    s.cab_cerrada = _cabecera(s.sesion_par[0]["access_token"])
    s.respuesta = s.cliente.post("/api/auth/logout", headers=s.cab_cerrada)


@when(parsers.parse("{nombre} cierra la primera sesión desde seguridad"))
def _cierra_primera_seguridad(s, nombre):
    sesion_id = s.sesion_par[0]["sesion_id"]
    s.cab_cerrada = _cabecera(s.sesion_par[0]["access_token"])
    s.respuesta = s.cliente.request("DELETE", f"/api/seguridad/sesiones/{sesion_id}",
                                    headers=_cabecera(s.sesion_par[1]["access_token"]))


@when("con la primera sesión se consulta el saldo")
def _primera_sesion_saldo(s):
    s.respuesta = s.cliente.get("/api/cuentas/me/saldo", headers=s.cab_cerrada)


@when(parsers.parse('se cierra sesión con la variante "{variante}"'))
def _logout_variante(s, variante):
    if variante == "sin token":
        s.respuesta = s.cliente.post("/api/auth/logout")
    elif variante == "token inválido":
        s.respuesta = s.cliente.post("/api/auth/logout", headers={"Authorization": "Bearer abc"})
    elif variante == "token vencido":
        celular, pin = conftest.USUARIOS["Bruno"]
        token = _login(s, celular, pin).json()["access_token"]
        s.cliente.put("/api/pruebas/reloj", json={"avanzar_minutos": 30})
        s.respuesta = s.cliente.post("/api/auth/logout", headers=_cabecera(token))
    elif variante == "método GET":
        s.respuesta = s.cliente.get("/api/auth/logout")


@then("el segundo cierre de sesión es rechazado")
def _segundo_logout(s):
    r = s.cliente.post("/api/auth/logout", headers=s.cab_cerrada)
    assert r.status_code == 401, r.text


@then(parsers.parse("{nombre} conserva {cantidad:d} sesiones activas"))
def _conserva_sesiones(s, nombre, cantidad):
    token = s.sesion_par[1]["access_token"]
    sesiones = s.cliente.get("/api/seguridad/sesiones", headers=_cabecera(token)).json()
    assert len(sesiones) == cantidad, sesiones


@then(parsers.parse("la segunda sesión de {nombre} sigue activa como la actual"))
def _segunda_sesion_activa(s, nombre):
    token = s.sesion_par[1]["access_token"]
    sesiones = s.cliente.get("/api/seguridad/sesiones", headers=_cabecera(token)).json()
    actual = next(x for x in sesiones if x["id"] == s.sesion_par[1]["sesion_id"])
    assert actual["actual"] is True, actual


@when(parsers.parse("{nombre} vuelve a iniciar sesión"))
def _vuelve_a_iniciar(s, nombre):
    _entrar(s, nombre)


@then("el nuevo inicio de sesión tiene un identificador distinto")
def _nuevo_id_distinto(s):
    assert s.login["sesion_id"] != s.sesion_par[0]["sesion_id"], s.login
    assert s.cliente.get("/api/cuentas/me", headers=s.cab).status_code == 200


@when("con la segunda sesión se consulta el perfil")
def _segunda_consulta_perfil(s):
    s.respuesta = s.cliente.get("/api/cuentas/me", headers=_cabecera(s.sesion_par[1]["access_token"]))


@when(parsers.parse('con la segunda sesión se edita el nombre a "{nombres}"'))
def _segunda_edita_nombre(s, nombres):
    s.respuesta = s.cliente.put("/api/cuentas/me", headers=_cabecera(s.sesion_par[1]["access_token"]),
                                json={"nombres": nombres})


# ================= HU-N-04: Consultar saldo y perfil =================

@when(parsers.parse("{nombre} consulta su saldo"))
def _consulta_saldo(s, nombre):
    s.pedir("GET", "/api/cuentas/me/saldo", nombre)


@when(parsers.parse("{nombre} consulta su perfil"))
def _consulta_perfil(s, nombre):
    s.pedir("GET", "/api/cuentas/me", nombre)


@when("se consulta el saldo actual")
def _consulta_saldo_actual(s):
    s.respuesta = s.cliente.get("/api/cuentas/me/saldo", headers=s.cab)


@when("se consulta el perfil actual")
def _consulta_perfil_actual(s):
    s.respuesta = s.cliente.get("/api/cuentas/me", headers=s.cab)


@given(parsers.parse('que se fija el saldo de {nombre} en "{saldo}"'))
def _fija_saldo(s, nombre, saldo):
    celular = conftest.USUARIOS[nombre][0]
    assert s.cliente.put("/api/pruebas/saldo", json={"celular": celular, "saldo": saldo}).status_code == 200


@when(parsers.parse("con el token de {nombre} se consulta la cuenta {cuenta_id:d}"))
def _consulta_cuenta_ajena(s, nombre, cuenta_id):
    s.respuesta = s.pedir("GET", f"/api/cuentas/{cuenta_id}", nombre)


@then(parsers.parse('el saldo actual es "{saldo}"'))
def _saldo_actual(s, saldo):
    assert s.cliente.get("/api/cuentas/me/saldo", headers=s.cab).json()["saldo"] == saldo


@then(parsers.parse('el límite diario actual es "{limite}"'))
def _limite_actual(s, limite):
    datos = s.cliente.get("/api/limites", headers=s.cab).json()
    assert datos["limite_diario"] == limite and datos["disponible_hoy"] == limite and datos["usado_hoy"] == "0.00", datos


@then(parsers.parse('el perfil actual tiene estado "{estado}" y DNI "{dni}"'))
def _perfil_actual_estado(s, estado, dni):
    perfil = s.cliente.get("/api/cuentas/me", headers=s.cab).json()
    assert (perfil["estado"], perfil["dni"]) == (estado, dni), perfil


@then(parsers.parse('el perfil consultado muestra nombres "{nombres}", celular "{celular}", correo "{correo}", DNI "{dni}" y estado "{estado}"'))
def _perfil_consultado(s, nombres, celular, correo, dni, estado):
    perfil = s.respuesta.json()
    assert (perfil["nombres"], perfil["celular"], perfil["correo"], perfil["dni"], perfil["estado"]) == \
        (nombres, celular, correo, dni, estado), perfil


@then(parsers.parse('el DNI del perfil cumple el enmascarado y no revela "{dni}"'))
def _dni_enmascarado(s, dni):
    cuerpo = s.respuesta.text
    perfil = s.respuesta.json()
    assert re.fullmatch(r"[*]{4}\d{4}", perfil["dni"]), perfil
    assert dni not in cuerpo and "pin_hash" not in cuerpo and "pin" not in perfil, cuerpo


@then("el correo del perfil actual es nulo")
def _perfil_actual_sin_correo(s):
    assert s.respuesta.json()["correo"] is None, s.respuesta.text


@then(parsers.parse('el DNI del perfil actual es "{dni}"'))
def _perfil_actual_dni(s, dni):
    assert s.respuesta.json()["dni"] == dni, s.respuesta.text


@when(parsers.parse('se consulta {ruta} con la credencial "{variante}"'))
def _consulta_con_credencial(s, ruta, variante):
    headers = None
    if variante == "token básico":
        headers = {"Authorization": "Basic YWJjOmRlZg=="}
    elif variante == "bearer sin valor":
        headers = {"Authorization": "Bearer"}
    elif variante == "bearer basura":
        headers = {"Authorization": "Bearer abc.def.ghi"}
    elif variante == "firma alterada":
        token = _entrar(s, "Ana").json()["access_token"]
        headers = _cabecera(token[:-2] + ("aa" if token[-2:] != "aa" else "bb"))
    elif variante == "otra clave":
        token = jwt.encode({"sub": "1", "jti": "x" * 32, "exp": int(time.time()) + 600},
                           "una-clave-distinta-de-treinta-y-dos-bytes", algorithm="HS256")
        headers = _cabecera(token)
    elif variante == "algoritmo none":
        token = jwt.encode({"sub": "1", "jti": "x" * 32, "exp": int(time.time()) + 600}, None, algorithm="none")
        headers = _cabecera(token)
    # "sin token": headers se queda en None.
    s.respuesta = s.cliente.get(ruta, headers=headers)


@when(parsers.parse('se consulta el saldo tras "{variante}"'))
def _consulta_saldo_tras(s, variante):
    if variante == "token vencido":
        celular, pin = conftest.USUARIOS["Bruno"]
        token = _login(s, celular, pin).json()["access_token"]
        s.cliente.put("/api/pruebas/reloj", json={"avanzar_minutos": 30})
        s.respuesta = s.cliente.get("/api/cuentas/me/saldo", headers=_cabecera(token))
    elif variante == "sesión cerrada":
        celular, pin = conftest.USUARIOS["Ana"]
        s1 = _login(s, celular, pin).json()
        s2 = _login(s, celular, pin).json()
        s.cliente.request("DELETE", f"/api/seguridad/sesiones/{s1['sesion_id']}",
                          headers=_cabecera(s2["access_token"]))
        s.respuesta = s.cliente.get("/api/cuentas/me/saldo", headers=_cabecera(s1["access_token"]))


@when(parsers.parse('se consulta el perfil con un token forjado con sub "{sub}"'))
def _perfil_token_forjado(s, sub):
    token = jwt.encode({"sub": sub, "jti": "y" * 32, "exp": int(time.time()) + 600},
                       CLAVE_POR_DEFECTO, algorithm="HS256")
    # Cliente aparte: si la API responde 500 corta la conexión y no debe afectar al cliente del escenario.
    with httpx.Client(base_url=conftest.URL, timeout=30) as cliente:
        s.respuesta = cliente.get("/api/cuentas/me", headers=_cabecera(token))


@when("se edita el perfil sin token")
def _edita_sin_token(s):
    s.respuesta = s.cliente.put("/api/cuentas/me", json={"nombres": "Intruso"})


@then(parsers.parse('el nombre guardado de {nombre} sigue siendo "{nombres}"'))
def _nombre_sin_cambios(s, nombre, nombres):
    celular, pin = conftest.USUARIOS[nombre]
    token = _login(s, celular, pin).json()["access_token"]
    assert s.cliente.get("/api/cuentas/me", headers=_cabecera(token)).json()["nombres"] == nombres


# ================= HU-N-05: Editar mi perfil =================

@when(parsers.parse('{origen} transfiere {monto} soles a {destino}'))
def _transfiere_soles(s, origen, monto, destino):
    celular_destino = conftest.USUARIOS[destino][0]
    s.respuesta = s.pedir("POST", "/api/transferencias", origen,
                          json={"tipo": "QOLQE", "monto": monto, "celular_destino": celular_destino})


@when(parsers.parse('{nombre} edita sus nombres a "{nombres}"'))
def _edita_nombres(s, nombre, nombres):
    valor = None if nombres == "NULO" else _expandir(nombres)
    s.respuesta = s.pedir("PUT", "/api/cuentas/me", nombre, json={"nombres": valor})


@when(parsers.parse('{nombre} edita su correo a "{correo}"'))
def _edita_correo(s, nombre, correo):
    cuerpo = {"correo": None if correo == "null" else correo}
    s.respuesta = s.pedir("PUT", "/api/cuentas/me", nombre, json=cuerpo)


@when(parsers.parse('{nombre} vacía su correo'))
def _vacia_correo(s, nombre):
    s.respuesta = s.pedir("PUT", "/api/cuentas/me", nombre, json={"correo": ""})


@when(parsers.parse('{nombre} edita el perfil con nombres "{nombres}" y correo "{correo}"'))
def _edita_nombres_correo(s, nombre, nombres, correo):
    cuerpo = {}
    if nombres != "-":
        cuerpo["nombres"] = _expandir(nombres)
    if correo != "-":
        cuerpo["correo"] = correo
    s.respuesta = s.pedir("PUT", "/api/cuentas/me", nombre, json=cuerpo)


@when(parsers.parse('{nombre} edita el perfil enviando DNI "{dni}", celular "{celular}" y nombres "{nombres}"'))
def _edita_con_dni_celular(s, nombre, dni, celular, nombres):
    s.respuesta = s.pedir("PUT", "/api/cuentas/me", nombre,
                          json={"dni": dni, "celular": celular, "nombres": nombres})


@when(parsers.parse('{nombre} edita el perfil enviando solo DNI "{dni}" y celular "{celular}"'))
def _edita_solo_dni_celular(s, nombre, dni, celular):
    s.respuesta = s.pedir("PUT", "/api/cuentas/me", nombre, json={"dni": dni, "celular": celular})


@when(parsers.parse('{nombre} edita el perfil con la variante "{variante}"'))
def _edita_variante(s, nombre, variante):
    cab = s.como(nombre)
    if variante == "nombres numérico":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"nombres": 123})
    elif variante == "correo numérico":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"correo": 123})
    elif variante == "cuerpo lista":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json=[1, 2])
    elif variante == "json mal formado":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers={**cab, "Content-Type": "application/json"},
                                    content=b"nojson")


@then(parsers.parse('el perfil de {nombre} guardó nombres "{nombres}"'))
def _perfil_guardo_nombres(s, nombre, nombres):
    perfil = s.cliente.get("/api/cuentas/me", headers=s.como(nombre)).json()
    esperado = "Ana Torres Quispe" if nombres == "SIN_CAMBIO" else _expandir(nombres)
    assert perfil["nombres"] == esperado, perfil


@when(parsers.parse('se consulta el perfil del caso "{caso}"'))
def _perfil_caso(s, caso):
    if caso == "usuario de carga":
        token = _login(s, "900000001", "2580").json()["access_token"]
    else:
        s.cliente.post("/api/usuarios", json={"dni": "00000000", "nombres": "Nuevo Sin Correo",
                                              "celular": "987000161", "pin": "4826"})
        token = _login(s, "987000161", "4826").json()["access_token"]
    s.respuesta = s.cliente.get("/api/cuentas/me", headers=_cabecera(token))


@when(parsers.parse('Ana envía el cambio de perfil "{variante}"'))
def _cambio_sin_correo_nuevo(s, variante):
    cab = s.como("Ana")
    if variante == "solo nombres":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"nombres": "Ana T"})
    elif variante == "mismo correo otra caja":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"correo": "ANA.TORRES@correo.pe"})
    elif variante == "correo de otro":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"correo": "bruno.diaz@correo.pe"})
    elif variante == "correo inválido":
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"correo": "mal"})


@when(parsers.parse('se cambia el correo del caso "{caso}"'))
def _cambia_correo_caso(s, caso):
    if caso == "Ana quita el correo":
        cab = _cabecera(_login(s, "987654321", "4826").json()["access_token"])
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"correo": ""})
    elif caso == "usuario de carga agrega correo":
        cab = _cabecera(_login(s, "900000001", "2580").json()["access_token"])
        s.respuesta = s.cliente.put("/api/cuentas/me", headers=cab, json={"correo": "carga1@correo.pe"})


@then(parsers.parse('el correo guardado de {nombre} es "{correo}"'))
def _correo_guardado(s, nombre, correo):
    actual = s.cliente.get("/api/cuentas/me", headers=s.como(nombre)).json()["correo"]
    assert actual == (None if correo == "null" else correo), actual


@then(parsers.parse('el perfil de {nombre} no cambió respecto de nombres "{nombres}" y correo "{correo}"'))
def _perfil_sin_cambios(s, nombre, nombres, correo):
    perfil = s.cliente.get("/api/cuentas/me", headers=s.como(nombre)).json()
    assert perfil["nombres"] == nombres and perfil["correo"] == (None if correo == "null" else correo), perfil


@then(parsers.parse('el perfil de {nombre} conserva DNI "{dni}" y celular "{celular}"'))
def _perfil_conserva_identidad(s, nombre, dni, celular):
    perfil = s.cliente.get("/api/cuentas/me", headers=s.como(nombre)).json()
    assert (perfil["dni"], perfil["celular"]) == (dni, celular), perfil


# ================= Concurrencia: oráculos compartidos =================

@then(parsers.parse('el registro simultáneo deja {ok:d} creado y {conflicto:d} en conflicto sin errores 500'))
def _registro_simultaneo_resultado(s, ok, conflicto):
    est = s.resultado_simultaneo
    assert est.get(201, 0) == ok and est.get(409, 0) == conflicto and est.get(500, 0) == 0, dict(est)
