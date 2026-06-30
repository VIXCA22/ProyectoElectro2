# Guia de diseno - Proyecto IE0413

Esta guia esta pensada para apoyar la memoria de calculo, no para pegarla como texto final. El enunciado pide que las deducciones y calculos se hagan a mano, asi que use estos pasos como verificacion y mantenga exactamente los mismos valores en LTspice y en la memoria.

Nota importante: el PDF `Plantilla_ProgramaCursos_EIE _IE0435.pdf` corresponde a otro curso. Para este trabajo se usa el enunciado `Proyecto - IE0413-2.pdf`, de Electronica II.

Todas las etapas con amplificador operacional usan el macromodelo no ideal `LF353/NS`, incluido localmente en `ltspice/lf353.mod`. No se usa el simbolo ideal `opamp2` como amplificador operacional.

## Parametros base

Ordene alfabeticamente los primeros apellidos del grupo y tome:

- `X`: primer digito no nulo del carne del integrante 1.
- `Y`: primer digito no nulo del carne del integrante 2.
- `Z`: primer digito no nulo del carne del integrante 3.

La frecuencia del oscilador es:

```text
f0 = (X + Y/10 + Z/100) kHz
```

Los archivos de LTspice usan por defecto `X=1`, `Y=2`, `Z=3`, por lo que el ejemplo queda en `f0 = 1.23 kHz`. Cambie esos tres parametros al inicio de cada `.cir`.

## 1. Oscilador central cuadrado

Se usa un oscilador de relajacion con LF353 en configuracion de comparador Schmitt.

```text
beta = R2/(R1 + R2)
T = 2 R C ln((1 + beta)/(1 - beta))
f0 = 1/T
```

Con `R1 = R2 = 100 kOhm`, `beta = 0.5`, y:

```text
Cosc = 10 nF
Rosc = 1/(2 f0 Cosc ln(3))
```

Para el ejemplo `f0 = 1.23 kHz`, la formula teorica da `Rosc = 37.0 kOhm`. En el archivo `oscilador_cuadrado_LF353.cir` deje `Ktrim = 1.0462` para compensar el retardo del macromodelo LF353 no ideal; por eso LTspice usa:

```text
Rosc_LTspice = Ktrim/(2 f0 Cosc ln(3))
```

Para el ejemplo, `Rosc_LTspice = 38.7 kOhm`. Si cambia `X,Y,Z`, revise `f_square` en el `.log`; si la frecuencia se mueve, ajuste `Ktrim` y anote ese valor como parte del calculo de simulacion.

## 2. Onda diente de sierra positiva

La etapa en LTspice usa una corriente casi constante que carga `Csaw` y un transistor `2N3904` que descarga el capacitor en cada flanco de la onda cuadrada. Los pulsos de reset salen de detectores de flanco RC; una version usa `V(sq)` y la otra usa `-V(sq)` para resetear en ambos semiciclos. Por eso la frecuencia de la rampa es `2 f0`.

```text
Tsaw = 1/(2 f0)
Vsaw_pk = (Isaw/Csaw) Tsaw
Isaw = Csaw Vsaw_pk 2 f0
```

Valores usados:

```text
Csaw = 10 nF
Vsaw_pk = 5 V
Isaw = Csaw Vsaw_pk 2 f0
```

Para el ejemplo, `Isaw = 123 uA`.

## 3. Onda triangular

La triangular debe quedar a `f0/2`. En la simulacion se representa la salida del divisor por 2 como una fuente equivalente sincronizada por la cuadrada; despues se usa un cambiador de nivel con LF353 para pasar de `0-2 V` a `-1 V/+1 V`, y finalmente un integrador inversor con LF353. Esa fuente equivalente no es un amplificador operacional ideal; solo sustituye el bloque divisor para concentrar la simulacion en las etapas analogicas vistas en el curso.

```text
ftri = f0/2
Vout_pk = VtriPk
pendiente = 2 VtriPk f0
Rtri = Vdrv/(2 VtriPk f0 Ctri)
```

Valores usados:

```text
Vdrv = 1 V
VtriPk = 2 V
Ctri = 10 nF
Rtri = Vdrv/(2 VtriPk f0 Ctri)
```

Para el ejemplo, `Rtri = 20.3 kOhm`.

## 4. Onda senoidal por filtro pasabajas de orden 5

La mejor entrada para obtener una senoide es la triangular. Una onda cuadrada tiene armonicos impares que decrecen como `1/n`; una diente de sierra tiene armonicos pares e impares que tambien decrecen como `1/n`. En cambio, la triangular solo tiene armonicos impares y decrecen como `1/n^2`, de modo que el tercer armonico ya viene mucho mas bajo antes del filtro.

Se fija:

```text
fc = 1.25 ftri
```

Asi la fundamental cae dentro de la banda de paso y el tercer armonico queda en `3 ftri = 2.4 fc`.

La respuesta depende de `Z`:

```text
Z = 1,2,3 -> Bessel
Z = 4,5,6 -> Butterworth
Z = 7,8,9 -> Chebyshev tipo I de 0.5 dB
```

El filtro usa una seccion RC activa de primer orden y dos secciones Sallen-Key de segundo orden con LF353. En las secciones Sallen-Key se usan `R1=R2=R`, `C1=C2=C`:

```text
f_n = 1/(2 pi R C)
Q = 1/(3 - K)
K = 3 - 1/Q
```

Con `C = 10 nF`, LTspice calcula cada `R` usando los multiplicadores normalizados incluidos en `filtro5_bode_LF353.cir`.

Use esta tabla para pasar los valores al calculo a mano:

| Respuesta | `fp1/fc` | `fn1/fc` | `Q1` | `K1` | `fn2/fc` | `Q2` | `K2` |
|---|---:|---:|---:|---:|---:|---:|---:|
| Bessel | 1.5023 | 1.5563 | 0.5635 | 1.2254 | 1.7554 | 0.9165 | 1.9089 |
| Butterworth | 1.0000 | 1.0000 | 0.6180 | 1.3820 | 1.0000 | 1.6180 | 2.3820 |
| Chebyshev 0.5 dB | 0.3623 | 0.6905 | 1.1778 | 2.1511 | 1.0177 | 4.5450 | 2.7800 |

Para cada fila:

```text
R_1er_orden = 1/(2 pi fp1 C)
R_SK1       = 1/(2 pi fn1 C)
R_SK2       = 1/(2 pi fn2 C)
```

## Archivos

- `ltspice/oscilador_cuadrado_LF353.cir`: solo la onda cuadrada.
- `ltspice/diente_sierra_2f0_LF353.cir`: etapa de diente de sierra positivo.
- `ltspice/triangular_f0_2_LF353.cir`: etapa triangular con cambiador de nivel e integrador.
- `ltspice/filtro5_bode_LF353.cir`: AC/Bode del filtro de orden 5.
- `ltspice/sintetizador_ie0413_LF353.cir`: simulacion transitoria estable para capturar las cuatro senales juntas; usa fuentes equivalentes para las senales ya generadas y LF353 no ideal en el filtro.
- `ltspice/lf353.mod`: modelo SPICE local del LF353 usado por todos los archivos.

En LTspice, abra el `.cir`, cambie `X`, `Y`, `Z`, ejecute la simulacion y grafique:

```text
V(sq), V(saw), V(tri), V(sine)
```

Para el Bode grafique:

```text
V(out)
```

Use las mediciones del archivo `.log` para verificar que las frecuencias coinciden con lo calculado.
