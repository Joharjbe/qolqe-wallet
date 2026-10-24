*** Keywords ***
Comprobar saldo en inicio
    [Arguments]    ${saldo_esperado}
    Click    css=[data-testid="nav-inicio"]
    Wait For Elements State    css=[data-testid="saldo-valor"]    visible
    ${saldo}=    Get Text    css=[data-testid="saldo-valor"]
    Should Be Equal    ${saldo}    ${saldo_esperado}
