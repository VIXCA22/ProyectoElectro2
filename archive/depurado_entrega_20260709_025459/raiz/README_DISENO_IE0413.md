# Guia final - Proyecto IE0413

Esta carpeta queda depurada para trabajar con una sola version: el diseno
minimo con `NE555` para la cuadrada y `LF353` para las etapas analogicas y el
filtro. Las versiones anteriores estan guardadas en
`archive/versiones_anteriores/` solo como respaldo.

## Version vigente

Use estos archivos como base de la entrega:

- `memoria_calculo_minimo_comparado.pdf`: memoria de calculo final.
- `memoria_calculo_minimo_comparado.tex`: fuente LaTeX de la memoria.
- `DISENO_MINIMO_COMPARADO.md`: resumen tecnico y comparacion calculo vs
  simulacion.
- `figuras/esquematico_minimo_ne555_lf353.png`: esquema limpio para insertar.
- `figuras/esquematico_minimo_ne555_lf353.svg`: esquema editable.

## Datos base

```text
X = 2
Y = 2
Z = 9
f0 = 2.29 kHz = 2290 Hz
fsaw = 2 f0 = 4580 Hz
ftri = f0/2 = 1145 Hz
Filtro = Chebyshev tipo I, orden 5
```

## Circuito final

La ruta final usa:

- Un `NE555` astable para la onda cuadrada a `f0`.
- Reset por flancos para obtener la sierra positiva a `2f0`.
- `LF353` para acondicionamiento, integrador triangular y filtro activo.
- Filtro pasabajas Chebyshev de quinto orden implementado como una etapa de
  primer orden y dos etapas Sallen-Key.

No se usa un segundo `NE555`. Las simulaciones se mantienen separadas por etapa
para que converjan limpio y para comparar directamente cada calculo con su
resultado de LTspice.

## Simulaciones finales

Los netlists vigentes son:

```text
ltspice/oscilador_555_astable_f0.cir
ltspice/diente_sierra_2f0_LF353.cir
ltspice/triangular_f0_2_LF353.cir
ltspice/filtro5_bode_LF353.cir
ltspice/filtro5_transitorio_LF353.cir
```

Modelos locales usados:

```text
ltspice/NE555.sub
ltspice/lf353.mod
```

## Comparacion principal

```text
Cuadrada:    2290.00 Hz calculado | 2290.02 Hz simulado  | error +0.0007 %
Sierra:      4580.00 Hz calculado | 4579.997 Hz simulado | error -0.00007 %
Triangular:  1145.00 Hz calculado | 1144.999 Hz simulado | error -0.00005 %
```

Para el filtro:

```text
|H(1145 Hz)| = -11.12 dB
|H(3435 Hz)| = -62.29 dB
Diferencia  =  51.17 dB
Senoidal filtrada en tiempo = 1145.00000589 Hz
```

## Regenerar archivos

Para regenerar el esquema:

```powershell
python scripts\generar_esquematico_minimo_ne555_lf353.py
```

Para regenerar las graficas desde los `.raw` de LTspice:

```powershell
python scripts\exportar_graficas.py
```

Para recompilar la memoria:

```powershell
pdflatex -interaction=nonstopmode memoria_calculo_minimo_comparado.tex
```

## Archivo

Todo lo que no pertenece a esta version final quedo en:

```text
archive/versiones_anteriores/
```

Si algun archivo de esa carpeta aparece abierto en el editor, se puede cerrar
para evitar confundirlo con la entrega final.
