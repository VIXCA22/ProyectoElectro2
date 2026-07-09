# Version alternativa sin flip-flop y sin series de armonicos

Esta version mantiene el `NE555` como integrado principal y evita usar un
`CD4013` u otro flip-flop externo. Tambien evita justificar la seleccion de la
entrada al filtro con series de Fourier; en su lugar usa ideas que si aparecen
en la materia: Bode, frecuencia normalizada, cascada de etapas, `Q`, banda de
paso y banda de rechazo.

## Datos del grupo

```text
X = 2
Y = 2
Z = 9
f0 = 2.29 kHz
```

Frecuencias pedidas:

```text
cuadrada:       f0     = 2.29 kHz
diente sierra:  2 f0   = 4.58 kHz
triangular:     f0 / 2 = 1.145 kHz
filtro:         Chebyshev, porque Z = 9
```

## 1. Cuadrada con NE555

Igual que en la version recomendada:

```text
TRIG y THRES unidos al capacitor Cosc
Rosc desde OUT hasta Cosc
RESET a Vcc
CONT desacoplado con 10 nF
Vcc = 15 V
```

El capacitor del 555 conmuta entre:

```text
VL = Vcc/3
VH = 2Vcc/3
```

Con una sola resistencia de carga/descarga:

```text
tH = R C ln(2)
tL = R C ln(2)
T  = 2 R C ln(2)
f0 = 1/(2 R C ln(2))
```

Con `Cosc = 10 nF`:

```text
Rosc = 31.5 kOhm
```

En LTspice se usa:

```text
Rosc = 31.46 kOhm
```

y se mide:

```text
f_square = 2290.02 Hz
duty = 50.00 %
```

## 2. Diente de sierra positivo a 2f0

Se conserva la etapa sencilla:

```text
1. Se carga Csaw desde +15 V mediante Rcharge.
2. En cada flanco de la cuadrada se genera un pulso corto.
3. El pulso activa un 2N3904 que descarga Csaw a tierra.
4. Como se descarga en ambos flancos, fsaw = 2f0.
```

Calculo:

```text
Tsaw = 1/(2f0) = 218.34 us
Vsaw = Vcc (1 - exp(-Tsaw/(Rcharge Csaw)))
Rcharge = -Tsaw/(Csaw ln(1 - Vsaw/Vcc))
```

Con:

```text
Vcc = 15 V
Vsaw = 5 V
Csaw = 10 nF
```

queda:

```text
Rcharge = 53.8 kOhm
```

Valor usado:

```text
Rcharge = 53.6 kOhm
```

## 3. Triangular a f0/2 sin flip-flop externo

En vez de usar un `CD4013`, se usa un segundo `NE555` en modo monoestable como
divisor por 2. La idea viene del funcionamiento de divisor de frecuencia del
555: mientras el monoestable esta temporizando, ignora el siguiente disparo.

La cuadrada principal tiene:

```text
T0 = 1/f0
T0 = 1/2290 = 436.68 us
```

Se escoge un pulso monoestable apenas mayor que un periodo del oscilador:

```text
tw = 1.05 T0
tw = 1.05(436.68 us)
tw = 458.52 us
```

Asi, el 555 se dispara en un flanco, ignora el siguiente, y vuelve a dispararse
dos periodos despues. Por tanto:

```text
Tdiv = 2T0
fdiv = f0/2 = 1145 Hz
```

Para el monoestable:

```text
tw = 1.1 Rdiv Cdiv
```

Con:

```text
Cdiv = 10 nF
```

se obtiene:

```text
Rdiv = tw/(1.1 Cdiv)
Rdiv = 458.52 us/(1.1*10 nF)
Rdiv = 41.7 kOhm
```

La salida del divisor no queda exactamente al 50%, porque `tw` se escogio un
poco mayor que `T0`. El ciclo alto queda:

```text
D = tw/(2T0) = 1.05/2 = 0.525
```

Para que el integrador no derive, el cambiador de nivel debe dar una senal de
entrada con area promedio cero. Se escoge:

```text
Vhigh = +1.00 V
```

y se calcula el nivel bajo:

```text
D Vhigh + (1-D) Vlow = 0
Vlow = -D Vhigh/(1-D)
Vlow = -0.525/(0.475)
Vlow = -1.105 V
```

Por tanto, el bloque de nivel convierte la salida `0-15 V` del 555 en:

```text
0 V  -> -1.105 V
15 V -> +1.000 V
```

Una forma de implementarlo es:

```text
Vdrive = k Vdiv - Vref
k = (1 - (-1.105))/15 = 0.1403
Vref = 1.105 V
```

Con `Rbot = 10 kOhm`:

```text
divisor de Vdiv:
Rtop = 61.3 kOhm
Rbot = 10 kOhm

referencia Vref:
Rtop = 125.7 kOhm
Rbot = 10 kOhm
```

El integrador se calcula para que el cambio de salida durante `tw` sea de
`2Vtri_pk`:

```text
Delta V = Vhigh tw/(Rtri Ctri)
Delta V = 2 Vtri_pk
Rtri = Vhigh tw/(2 Vtri_pk Ctri)
```

Con:

```text
Vtri_pk = 2 V
Ctri = 10 nF
tw = 458.52 us
```

se obtiene:

```text
Rtri = 11.46 kOhm
```

Valor recomendado:

```text
Rtri = 11.5 kOhm
```

## 4. Filtro sin justificar con series de armonicos

La materia permite defender esta parte con Bode y filtros de orden superior:

```text
S = jw/w0 = jf/f0
H(S) = H0 N(S)/(1 + aS + bS^2)
Q = b/a
```

Para filtros de orden mayor a 2, la materia indica que se conectan etapas en
cascada. Como el enunciado pide orden 5:

```text
orden 5 = orden 1 + orden 2 + orden 2
```

Como `Z = 9`, se usa Chebyshev. Segun la materia, Chebyshev se caracteriza por
una transicion mas abrupta entre banda de paso y banda de rechazo, con rizado
en banda de paso. Esto conviene porque queremos conservar la frecuencia
principal y rechazar mas rapido las variaciones de frecuencia mayor.

Seleccion de la senal que entra al filtro, sin usar series de Fourier:

```text
cuadrada: cambia de nivel bruscamente dos veces por periodo.
sierra: sube de forma suave, pero vuelve a cero con un salto brusco.
triangular: no tiene saltos de voltaje; solo cambia de pendiente.
```

Un filtro pasabajas suaviza cambios rapidos. Por eso, entre las tres senales,
la triangular es la que exige menos correccion del filtro para parecerse a una
senoidal, porque ya es continua y no tiene saltos de voltaje.

Se fija:

```text
ftri = 1145 Hz
fc = 1.25 ftri = 1431.25 Hz
```

Asi la frecuencia de interes queda dentro de la banda de paso, y las
variaciones de frecuencia mayor entran en la zona donde el Chebyshev atenua
mas fuerte.

Valores del filtro Chebyshev tipo I de orden 5, con `C = 10 nF`:

```text
Atenuador de entrada:
Rtop = 498 kOhm
Rbot = 100 kOhm

Primer orden:
R = 30.7 kOhm
C = 10 nF

Sallen-Key 1:
R1 = R2 = 16.1 kOhm
C1 = C2 = 10 nF
Rg = 10 kOhm
Rf = 11.5 kOhm

Sallen-Key 2:
R1 = R2 = 10.9 kOhm
C1 = C2 = 10 nF
Rg = 10 kOhm
Rf = 17.8 kOhm
```

Verificacion por Bode:

```text
|H(1145 Hz)| = -11.12 dB
|H(3435 Hz)| = -62.29 dB
```

La diferencia es:

```text
62.29 - 11.12 = 51.17 dB
```

Por tanto, el filtro deja pasar mucho mas la frecuencia de interes que una
frecuencia tres veces mayor. Esta justificacion usa Bode y rechazo en
frecuencia, no series de armonicos.

## Resumen de integrados

```text
NE555 x2:
  1 para la cuadrada f0
  1 como divisor por 2 monoestable

LF353:
  cambiadores de nivel, integradores, buffers y filtro activo
```

## Comentario importante

Esta version evita el flip-flop externo, pero usa un segundo 555 como divisor
por 2. Si el profesor permite el `CD4013`, la version con flip-flop es mas
cuadrada y mas exacta. Si prefieren explicar todo con el 555, esta version es
mas coherente.
