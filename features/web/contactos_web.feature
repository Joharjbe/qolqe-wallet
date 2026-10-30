# language: es
Característica: Pantalla de contactos (G4)
  Solo lo que únicamente se ve en la pantalla y los recorridos críticos.
  Las reglas de validación se prueban en la API (nivel más bajo donde se detectan).

  @HU-G4-01 @CA1 @CP-W01
  Escenario: CP-W01 Agregar un contacto desde la pantalla
    Dado que "Diego" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando agrega el contacto "912345678" con alias "Bruno Web"
    Entonces ve el aviso "Contacto \"Bruno Web\" agregado"
    Y el contacto "Bruno Web" aparece en la lista

  @HU-G4-01 @CA1 @CP-W02
  Escenario: CP-W02 El error de la API se muestra al usuario
    Dado que "Diego" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando agrega el contacto "900000999" con alias "No Existe"
    Entonces ve el error de contactos "no está registrado"
    Y el contacto "No Existe" no aparece en la lista

  @HU-G4-02 @CA1 @CP-W03
  Escenario: CP-W03 Favoritos primero, 10 por página y total visible
    Dado que "Diego" tiene 12 contactos y "Zeta 05" es favorito
    Y que "Diego" ingresó a Qolqe
    Cuando abre la pantalla de contactos
    Entonces el primer contacto de la lista es "Zeta 05"
    Y la página muestra 10 contactos con el texto "12 de 15 contactos" y "Página 1 de 2"
    Cuando pasa a la página siguiente
    Entonces la página muestra 2 contactos con el texto "12 de 15 contactos" y "Página 2 de 2"

  @HU-G4-02 @CA2 @CP-W04
  Escenario: CP-W04 Buscar sin tildes ni mayúsculas
    Dado que "Diego" tiene el contacto "912345678" con alias "José Pérez"
    Y que "Diego" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando busca "jose"
    Entonces la lista solo muestra el contacto "José Pérez"
    Cuando busca "xyz"
    Entonces ve el mensaje vacío "Ningún contacto coincide con la búsqueda"

  @HU-G4-02 @CA3 @CP-W05
  Escenario: CP-W05 Cada contacto muestra alias, nombre enmascarado, celular y favorito
    Dado que "Ana" ingresó a Qolqe
    Cuando abre la pantalla de contactos
    Entonces el contacto "Bruno" muestra "Bruno D. · 912345678" y está marcado como favorito
    Y el contacto "Prima Carla" muestra "Carla R. · 956781234" y no está marcado como favorito

  @HU-G4-03 @CA1 @CP-W06
  Escenario: CP-W06 Editar el alias y marcar como favorito
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando edita "Prima Carla" con el alias "Carlita" y la marca como favorito
    Entonces ve el aviso "Contacto actualizado"
    Y el contacto "Carlita" muestra "Carla R. · 956781234" y está marcado como favorito

  @HU-G4-04 @CA1 @CP-W07
  Escenario: CP-W07 Eliminar un contacto pide confirmación
    Dado que "Diego" tiene el contacto "912345678" con alias "Bruno"
    Y que "Diego" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando elimina el contacto "Bruno" y confirma
    Entonces ve el aviso "Contacto eliminado"
    Y el contacto "Bruno" no aparece en la lista

  @HU-G4-04 @CA2 @CP-W08
  Escenario: CP-W08 No se elimina un contacto con solicitudes pendientes
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando elimina el contacto "Bruno" y confirma
    Entonces ve el aviso "solicitudes de dinero pendientes"
    Y el contacto "Bruno" aparece en la lista

  @HU-G4-05 @CA1 @CP-W09
  Escenario: CP-W09 Transferir eligiendo un contacto
    Dado que "Ana" ingresó a Qolqe
    Y abre la pantalla de contactos
    Cuando transfiere "100.00" al contacto "Bruno"
    Entonces el comprobante muestra destino "Bruno D. (912345678)", total "S/ 100.00" y saldo "S/ 1,400.00"
    Y su saldo en inicio es "S/ 1,400.00"
