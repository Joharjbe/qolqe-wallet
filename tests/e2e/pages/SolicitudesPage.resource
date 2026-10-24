*** Keywords ***
Abrir página de solicitudes
    Click    css=[data-testid="nav-solicitudes"]
    Wait For Elements State    css=[data-testid="boton-solicitar"]    visible

Enviar solicitud a contacto
    [Arguments]    ${alias}    ${celular}    ${monto}    ${motivo}
    Wait For Elements State    css=[data-testid="select-solicitud-contacto"] option:has-text("${alias}")    attached
    Select Options By    css=[data-testid="select-solicitud-contacto"]    label    ${alias} (${celular})
    Fill Text    css=[data-testid="input-solicitud-monto"]    ${monto}
    Fill Text    css=[data-testid="input-solicitud-motivo"]    ${motivo}
    Click    css=[data-testid="boton-solicitar"]
    Wait For Elements State    css=[data-testid="solicitud-mensaje"]    visible
    ${mensaje}=    Get Text    css=[data-testid="solicitud-mensaje"]
    Should Contain    ${mensaje}    Solicitud enviada
    Comprobar estado de solicitud    ${motivo}    Pendiente

Aceptar solicitud recibida
    [Arguments]    ${motivo}
    ${fila}=    Set Variable    css=[data-testid="solicitud"]:has-text("${motivo}")
    Wait For Elements State    ${fila}    visible
    Click    ${fila} >> css=[data-testid="boton-aceptar-solicitud"]
    Wait For Elements State    css=[data-testid="dialogo-confirmar"]    visible
    Click    css=[data-testid="boton-confirmar-accion"]
    Comprobar estado de solicitud    ${motivo}    Aceptada
    ${detalle}=    Get Text    ${fila} >> css=[data-testid="solicitud-detalle"]
    Should Contain    ${detalle}    Operación

Ver solicitudes enviadas
    Click    css=[data-testid="pestana-enviadas"]

Comprobar estado de solicitud
    [Arguments]    ${motivo}    ${estado_esperado}
    ${selector}=    Set Variable    css=[data-testid="solicitud"]:has-text("${motivo}") [data-testid="solicitud-estado"]:has-text("${estado_esperado}")
    Wait For Elements State    ${selector}    visible
    ${estado}=    Get Text    ${selector}
    Should Be Equal    ${estado}    ${estado_esperado}
