"""Pasos de pytest-bdd del G4 de la Parte 2: contactos y solicitudes (HU-G4-01 a HU-G4-10).

Varios los usan también los casos del núcleo y los técnicos de G4: inicio de sesión, estado HTTP, código de error, saldo y SMS,
entre otros. Los casos funcionales y técnicos que se sumaron después están en pasos_g4_extra.py.
"""
from datetime import datetime, timedelta

import conftest  # Helpers compartidos: USUARIOS y orden_alfabetico.
from pytest_bdd import given, parsers, then, when

# ---------- Dado ----------

@given(parsers.parse("que {nombre} inició sesión"))
def inicio_sesion(s, nombre):
    s.ingresar(nombre)


@given(parsers.parse("Diego tiene {total:d} contactos en total"))
def contactos_en_total(s, total):
    s.completar_contactos("Diego", total)


@given(parsers.parse('Diego tiene el contacto "{celular}" con alias "{alias}"'))
def tiene_contacto(s, celular, alias):
    s.agregar("Diego", celular, alias)


@given(parsers.parse('el contacto "{alias}" es favorito'))
def contacto_favorito(s, alias):
    s.pedir("PUT", f"/api/contactos/{s.contacto_id(alias)}", json={"favorito": True})


@given(parsers.parse("Diego marcó {total:d} contactos como favoritos"))
def marcar_favoritos(s, total):
    for contacto in s.contactos("Diego")[:total]:
        s.pedir("PUT", f"/api/contactos/{contacto['id']}", "Diego", json={"favorito": True})
        assert s.respuesta.status_code == 200, s.respuesta.text


@given(parsers.parse('Diego transfirió {monto} al contacto "{alias}"'))
def transfirio_a_contacto(s, monto, alias):
    r = s.pedir("POST", "/api/transferencias", "Diego",
                json={"tipo": "QOLQE", "monto": monto, "contacto_id": s.contacto_id(alias, "Diego")})
    assert r.status_code == 201, r.text
    s.codigo_operacion = r.json()["codigo_operacion"]


@given(parsers.parse("Diego envió {total:d} solicitudes a \"{alias}\""))
def envio_solicitudes(s, total, alias):
    contacto_id = s.contacto_id(alias, "Diego")
    for i in range(total):
        r = s.cliente.post("/api/solicitudes", headers=s.como("Diego"),
                           json={"contacto_id": contacto_id, "monto": "1.00", "motivo": f"Solicitud {i}"})
        assert r.status_code == 201, r.text
        s.solicitud_id = r.json()["id"]


@given(parsers.parse("que {solicitante} le solicitó {monto} a {destinatario}"))
def le_solicito(s, solicitante, monto, destinatario):
    s.solicitar_entre(solicitante, destinatario, monto)


@given(parsers.parse("Diego ya transfirió {monto} hoy"))
def ya_transfirio(s, monto):
    # El límite diario de Diego en la semilla es S/ 1,000; se transfiere en dos partes por RN-05.
    for parte in ("500.00", f"{float(monto) - 500:.2f}"):
        r = s.pedir("POST", "/api/transferencias", "Diego",
                    json={"tipo": "QOLQE", "monto": parte, "celular_destino": conftest.USUARIOS["Bruno"][0]})
        assert r.status_code == 201, r.text


@given("la solicitud vencida de Carla a Ana")
def solicitud_vencida(s):
    recibidas = s.cliente.get("/api/solicitudes", headers=s.como("Ana"), params={"estado": "VENCIDA"}).json()["recibidas"]
    s.solicitud_id = recibidas[0]["id"]


@given(parsers.parse("{nombre} aceptó la solicitud"))
def acepto(s, nombre):
    r = s.pedir("POST", f"/api/solicitudes/{s.solicitud_id}/aceptar", nombre)
    assert r.status_code == 200, r.text


# ---------- Cuando ----------

@when(parsers.parse('agrega el contacto "{celular}" con alias "{alias}"'))
def agrega(s, celular, alias):
    s.pedir("POST", "/api/contactos", json={"celular": celular, "alias": alias})


@when("consulta sus contactos")
def consulta_contactos(s):
    s.pedir("GET", "/api/contactos")


@when(parsers.parse('busca contactos con "{texto}"'))
def busca(s, texto):
    s.pedir("GET", "/api/contactos", params={"buscar": texto})


@when(parsers.parse('edita el contacto "{alias}" con alias "{nuevo}" y favorito'))
def edita_con_favorito(s, alias, nuevo):
    s.duenio_contacto = s.actual
    s.pedir("PUT", f"/api/contactos/{s.contacto_id(alias)}", json={"alias": nuevo, "favorito": True})


@when(parsers.parse('edita el contacto "{alias}" con alias "{nuevo}"'))
def edita(s, alias, nuevo):
    s.pedir("PUT", f"/api/contactos/{s.contacto_id(alias)}", json={"alias": nuevo})


@when("marca como favorito el último contacto")
def favorito_ultimo(s):
    no_favoritos = [c for c in s.contactos() if not c["favorito"]]
    s.pedir("PUT", f"/api/contactos/{no_favoritos[-1]['id']}", json={"favorito": True})


@when(parsers.parse('elimina el contacto "{alias}"'))
def elimina(s, alias):
    s.pedir("DELETE", f"/api/contactos/{s.contacto_id(alias)}")


@when(parsers.parse('transfiere {monto} al contacto "{alias}"'))
def transfiere(s, monto, alias):
    s.pedir("POST", "/api/transferencias", json={"tipo": "QOLQE", "monto": monto, "contacto_id": s.contacto_id(alias)})


@when(parsers.parse('intenta {accion} el contacto "{alias}" de Ana'))
def intenta_ajeno(s, accion, alias):
    contacto_id = s.contacto_id(alias, "Ana")
    if accion == "editar":
        s.pedir("PUT", f"/api/contactos/{contacto_id}", "Carla", json={"favorito": False})
    else:
        s.pedir("DELETE", f"/api/contactos/{contacto_id}", "Carla")


@when(parsers.parse('solicita {monto} a "{alias}" por "{motivo}"'))
def solicita(s, monto, alias, motivo):
    s.pedir("POST", "/api/solicitudes", json={"contacto_id": s.contacto_id(alias), "monto": monto, "motivo": motivo})


@when(parsers.parse('solicita {monto} a "{alias}" con un motivo de {largo:d} caracteres'))
def solicita_con_largo(s, monto, alias, largo):
    s.pedir("POST", "/api/solicitudes", json={"contacto_id": s.contacto_id(alias), "monto": monto, "motivo": "m" * largo})


@when(parsers.parse('consulta sus solicitudes con estado "{estado}"'))
def consulta_solicitudes(s, estado):
    s.pedir("GET", "/api/solicitudes", params={"estado": estado})


@when(parsers.parse("el reloj avanza {minutos:d} minutos y Diego vuelve a ingresar"))
def avanza_reloj(s, minutos):
    # Se fija la hora exacta para que los segundos transcurridos no cambien el valor límite.
    creada = s.cliente.get("/api/solicitudes", headers=s.como("Diego")).json()["enviadas"][0]["creada_en"]
    momento = datetime.fromisoformat(creada) + timedelta(minutes=minutos)
    assert s.cliente.put("/api/pruebas/reloj", json={"ahora": momento.isoformat()}).status_code == 200
    s.ingresar("Diego")


@when(parsers.parse("{nombre} acepta la solicitud"))
def acepta(s, nombre):
    s.pedir("POST", f"/api/solicitudes/{s.solicitud_id}/aceptar", nombre)


@when(parsers.parse("{nombre} rechaza la solicitud con un motivo de {largo:d} caracteres"))
def rechaza(s, nombre, largo):
    cuerpo = {"motivo": "m" * largo} if largo else {}
    s.pedir("POST", f"/api/solicitudes/{s.solicitud_id}/rechazar", nombre, json=cuerpo)


@when(parsers.parse("{nombre} cancela la solicitud"))
def cancela(s, nombre):
    s.pedir("POST", f"/api/solicitudes/{s.solicitud_id}/cancelar", nombre)


# ---------- Entonces ----------

@then(parsers.parse("la respuesta tiene estado {estado:d}"))
def estado_http(s, estado):
    assert s.respuesta.status_code == estado, s.respuesta.text


@then(parsers.parse('el código de error es "{codigo}"'))
def codigo_error(s, codigo):
    cuerpo = s.respuesta.json()
    assert cuerpo["codigo"] == codigo, cuerpo
    assert cuerpo["detail"], "Todo error debe incluir un mensaje"


@then(parsers.parse('el contacto creado tiene alias "{alias}" y nombre enmascarado "{nombre}"'))
def contacto_creado(s, alias, nombre):
    cuerpo = s.respuesta.json()
    assert (cuerpo["alias"], cuerpo["nombre"]) == (alias, nombre)


@then(parsers.parse("la página tiene {cantidad:d} contactos de un total de {total:d}"))
def pagina_contactos(s, cantidad, total):
    cuerpo = s.respuesta.json()
    assert (len(cuerpo["contactos"]), cuerpo["total"], cuerpo["por_pagina"]) == (cantidad, total, 10)


@then(parsers.parse('el primer contacto es "{alias}"'))
def primer_contacto(s, alias):
    assert s.respuesta.json()["contactos"][0]["alias"] == alias


@then("los demás contactos están ordenados por alias")
def demas_ordenados(s):
    alias = [c["alias"] for c in s.respuesta.json()["contactos"][1:]]
    assert alias == sorted(alias, key=conftest.orden_alfabetico), alias


@then(parsers.parse("la búsqueda encuentra {total:d} contactos"))
def busqueda_total(s, total):
    assert s.respuesta.json()["total"] == total


@then(parsers.parse('el primer contacto tiene alias "{alias}", nombre "{nombre}", celular "{celular}" y favorito'))
def detalle_contacto(s, alias, nombre, celular):
    c = s.respuesta.json()["contactos"][0]
    assert (c["alias"], c["nombre"], c["celular"], c["favorito"]) == (alias, nombre, celular, True)


@then(parsers.parse('el contacto "{alias}" ya no aparece'))
def contacto_eliminado(s, alias):
    assert alias not in [c["alias"] for c in s.contactos()]


@then("la transferencia sigue en sus movimientos")
def transferencia_conservada(s):
    r = s.pedir("GET", f"/api/movimientos/{s.codigo_operacion}")
    assert r.status_code == 200, r.text


@then(parsers.parse('el saldo de {nombre} es "{saldo}"'))
def saldo_de(s, nombre, saldo):
    assert s.saldo(nombre) == saldo


@then(parsers.parse('la solicitud está en estado "{estado}"'))
def solicitud_estado(s, estado):
    assert s.respuesta.json()["estado"] == estado


@then("la solicitud vence 48 horas después de creada")
def vence_48(s):
    c = s.respuesta.json()
    assert datetime.fromisoformat(c["vence_en"]) - datetime.fromisoformat(c["creada_en"]) == timedelta(hours=48)


@then(parsers.parse('"{celular}" recibió un SMS que contiene "{texto}"'))
def recibio_sms(s, celular, texto):
    mensajes = s.cliente.get("/api/pruebas/notificaciones", params={"celular": celular}).json()
    assert any(texto in m["mensaje"] for m in mensajes), mensajes


@then(parsers.parse("tiene {enviadas:d} enviadas y {recibidas:d} recibidas"))
def enviadas_recibidas(s, enviadas, recibidas):
    cuerpo = s.respuesta.json()
    assert (len(cuerpo["enviadas"]), len(cuerpo["recibidas"])) == (enviadas, recibidas)


@then(parsers.parse('su solicitud enviada figura como "{estado}"'))
def enviada_estado(s, estado):
    assert s.cliente.get("/api/solicitudes", headers=s.como("Diego")).json()["enviadas"][0]["estado"] == estado


@then("la solicitud tiene código de operación")
def tiene_codigo(s):
    assert s.respuesta.json()["codigo_operacion"]


@then(parsers.parse('{nombre} ve la solicitud en estado "{estado}"'))
def ve_estado(s, nombre, estado):
    recibidas = s.cliente.get("/api/solicitudes", headers=s.como(nombre)).json()["recibidas"]
    assert next(x for x in recibidas if x["id"] == s.solicitud_id)["estado"] == estado
