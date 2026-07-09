# Entrega LTspice - Sintetizador de ondas

Este paquete contiene el informe, la simulacion LTspice, las graficas y los
valores teoricos/simulados del proyecto.

## Contenido

- `documento/informe_etapas_sintetizador_ltspice.pdf`: informe final.
- `simulacion/EsquematicoSintetizador.asc`: esquema original editable.
- `simulacion/EsquematicoSintetizador.plt`: vista de ondas para LTspice.
- `simulacion/EsquematicoSintetizador_portable.cir`: simulacion transitoria
  portable, recomendada para correr en otra computadora.
- `simulacion/filtro5_bode_LF353_portable.cir`: Bode portable del filtro
  Chebyshev.
- `simulacion/modelos/`: modelos usados por la simulacion portable.
- `simulacion/simbolos/`: simbolos LTspice usados por el esquema editable.
- `graficas/`: graficas separadas y juntas en PDF/SVG.
- `datos/`: datos CSV exportados de las ondas.
- `valores_teoricos_simulados.csv`: tabla de valores y errores.
- `valores_teoricos_simulados.md`: resumen legible de resultados.

## Forma recomendada de correr la simulacion

1. Instalar LTspice.
2. Extraer el `.zip` completo.
3. Abrir `simulacion/EsquematicoSintetizador_portable.cir`.
4. Presionar `Run`.
5. Abrir `View > SPICE Error Log` para ver el resumen por etapas.
6. Abrir el archivo `.raw` generado para ver las senales guardadas:
   `SC`, `VC555`, `RST_DS`, `DS`, `SC_D2`, `TRI` y `SEN`.

La simulacion portable ya incluye los modelos locales:

- `modelos/NE555.sub`
- `modelos/LF353.mod`
- `modelos/CD4000.lib`

LTspice aporta desde su instalacion normal los modelos estandar de `1N4148` y
`2N3904` mediante `standard.dio` y `standard.bjt`.

## Correr el diagrama de Bode

1. Abrir `simulacion/filtro5_bode_LF353_portable.cir`.
2. Presionar `Run`.
3. Abrir `simulacion/filtro5_bode_LF353_portable.plt` si LTspice no carga la vista
   automaticamente.
4. La traza recomendada es `V(out)/V(in)`.

Resultados esperados:

```text
|H(1145 Hz)| = -11.1189 dB
fase H(1145 Hz) = -216.8655 deg
|H(3435 Hz)| = -62.2899 dB
fase H(3435 Hz) = -426.5995 deg
Atenuacion extra = 51.1710 dB
```

## Abrir el esquema editable `.asc`

La forma mas segura para otra computadora es correr el archivo portable `.cir`.
Si se desea abrir el esquema visual `.asc`, copiar los simbolos incluidos:

```text
simulacion/simbolos/Misc/NE555.asy
simulacion/simbolos/UserLibs/LTwiki/lf353_ns.asy
simulacion/simbolos/UserLibs/LTwiki/CD4013B.i.asy
```

a las carpetas equivalentes de simbolos de LTspice, por ejemplo:

```text
%LOCALAPPDATA%\LTspice\lib\sym\Misc
%LOCALAPPDATA%\LTspice\lib\sym\UserLibs\LTwiki
```

Tambien copiar los modelos:

```text
simulacion/modelos/NE555.sub
simulacion/modelos/LF353.mod
simulacion/modelos/CD4000.lib
```

a una carpeta de modelos accesible por LTspice. Si LTspice pide el archivo al
abrir el esquema, seleccionar el modelo correspondiente desde `simulacion/modelos`.

## Lectura del log

Los resultados del log estan ordenados asi:

```text
G00_ETAPA_1_SC_555      -> oscilador NE555 y cuadrada SC
G10_ETAPA_2_DS          -> diente de sierra DS
G20_ETAPA_3A_SC_D2      -> flip-flop divisor por 2
G30_ETAPA_3B_TRI        -> integrador triangular
G40_ETAPA_4_SEN         -> filtro Chebyshev y senoidal
G90_RESUMEN_RAPIDO      -> valores finales principales
```

Los nombres `Gxx` son separadores visuales porque LTspice no imprime tablas ni
encabezados bonitos dentro del `SPICE Error Log`.
