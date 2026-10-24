*** Keywords ***
Abrir página de contactos
    Click    css=[data-testid="nav-contactos"]
    Wait For Elements State    css=[data-testid="boton-agregar-contacto"]    visible

Agregar contacto y comprobarlo
    [Arguments]    ${celular}    ${alias}
    Fill Text    css=[data-testid="input-celular"]    ${celular}
    Fill Text    css=[data-testid="input-alias"]    ${alias}
    Click    css=[data-testid="boton-agregar-contacto"]
    Fill Text    css=[data-testid="input-buscar-contacto"]    ${alias}
    Wait For Elements State    css=[data-testid="contacto-alias"]:has-text("${alias}")    visible
    ${texto}=    Get Text    css=[data-testid="contacto-alias"]:has-text("${alias}")
    Should Be Equal    ${texto}    ${alias}
