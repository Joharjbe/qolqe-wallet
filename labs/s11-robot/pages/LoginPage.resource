*** Keywords ***
Ingresar como usuario
    [Arguments]    ${celular}    ${pin}
    Fill Text    css=[data-testid="input-celular"]    ${celular}
    Fill Text    css=[data-testid="input-pin"]    ${pin}
    Click    css=[data-testid="boton-ingresar"]
    Wait For Elements State    css=[data-testid="nav-contactos"]    visible

Cerrar sesión desde el menú
    Click    css=[data-testid="boton-cerrar-sesion"]
    Wait For Elements State    css=[data-testid="boton-ingresar"]    visible
