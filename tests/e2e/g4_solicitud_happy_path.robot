*** Settings ***
Documentation    G4: contacto, solicitud de dinero y aceptación con transferencia observable.
Library    Browser    timeout=15s    retry_assertions_for=5s
Library    support.py
Resource    pages/LoginPage.resource
Resource    pages/ContactosPage.resource
Resource    pages/SolicitudesPage.resource
Resource    pages/InicioPage.resource
Suite Setup    Preparar demo
Suite Teardown    Close Browser

*** Variables ***
${BASE_URL}    http://127.0.0.1:8000
${HEADLESS}    True
${DIEGO_CELULAR}    998877665
${DIEGO_PIN}    3604
${BRUNO_CELULAR}    912345678
${BRUNO_PIN}    7391
${ALIAS}    Bruno Demo
${MOTIVO}    Devolucion demo G4
${MONTO}    25.00

*** Test Cases ***
Solicitud de dinero aceptada de punta a punta
    [Documentation]    HU-G4-01/06/07/08; RN-09 y RN-10. Reinicio local antes de ejecutar.
    Ingresar como usuario    ${DIEGO_CELULAR}    ${DIEGO_PIN}
    Abrir página de contactos
    Agregar contacto y comprobarlo    ${BRUNO_CELULAR}    ${ALIAS}
    Abrir página de solicitudes
    Enviar solicitud a contacto    ${ALIAS}    ${BRUNO_CELULAR}    ${MONTO}    ${MOTIVO}
    Cerrar sesión desde el menú
    Ingresar como usuario    ${BRUNO_CELULAR}    ${BRUNO_PIN}
    Abrir página de solicitudes
    Aceptar solicitud recibida    ${MOTIVO}
    Comprobar estado de solicitud    ${MOTIVO}    Aceptada
    Comprobar saldo en inicio    S/ 775.00
    Cerrar sesión desde el menú
    Ingresar como usuario    ${DIEGO_CELULAR}    ${DIEGO_PIN}
    Abrir página de solicitudes
    Ver solicitudes enviadas
    Comprobar estado de solicitud    ${MOTIVO}    Aceptada
    Comprobar saldo en inicio    S/ 2,525.00

*** Keywords ***
Preparar demo
    Reiniciar datos locales de Qolqe    ${BASE_URL}
    New Browser    chromium    headless=${HEADLESS}
    New Page    ${BASE_URL}/login
