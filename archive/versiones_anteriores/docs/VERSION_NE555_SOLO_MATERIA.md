# Version NE555 basada solo en enunciado y materia vista

Esta version queda separada de las otras rutas. Usa:

- `NE555` para la onda cuadrada.
- Otro `NE555` en monoestable para obtener `f0/2`, sin flip-flop externo.
- `LF353` para acondicionamiento analogico: inversor/buffer, cambiador de nivel, integrador y filtro activo.
- Carga RC por resistencia para la diente de sierra, sin fuente ideal de corriente.
- Filtro pasabajas Chebyshev de orden 5 defendido con Bode, frecuencia normalizada `S`, `Q` y cascada de etapas.

## 1. Datos del enunciado

Orden alfabetico:

```text
Madriz, Torres, Vizcaino
```

Por tanto:

```text
X = 2
Y = 2
Z = 9
```

La frecuencia del oscilador es:

```text
f0 = X,YZ kHz
f0 = 2.29 kHz
f0 = 2290 Hz
```

Frecuencias requeridas:

```text
cuadrada:       f0     = 2290 Hz
diente sierra:  2f0    = 4580 Hz
triangular:     f0/2   = 1145 Hz
filtro:         Chebyshev, porque Z = 9
```

## 2. Onda cuadrada con NE555

Se usa el `NE555` como astable tipo Schmitt.

Conexion:

```text
TRIG y THRES unidos al capacitor Cosc
Rosc entre OUT y Cosc
RESET a Vcc
CONT con 10 nF a tierra
Vcc = 15 V
```

El capacitor conmuta entre:

```text
VL = Vcc/3
VH = 2Vcc/3
```

Como carga y descarga por la misma resistencia:

```text
tH = Rosc Cosc ln(2)
tL = Rosc Cosc ln(2)
T  = 2 Rosc Cosc ln(2)
f0 = 1/T
```

Despeje:

```text
Rosc = 1/(2 f0 Cosc ln(2))
```

Con:

```text
Cosc = 10 nF
f0 = 2290 Hz
```

Resultado:

```text
Rosc = 31.5 kOhm
```

Valor de simulacion:

```text
Rosc = 31.46 kOhm
```

Medicion LTspice:

```text
f_square = 2290.02 Hz
duty = 50.00 %
```

## 3. Diente de sierra positivo sin fuente de corriente

Se carga un capacitor desde `+15 V` usando una resistencia. En cada flanco de la cuadrada se activa un transistor `2N3904` que descarga el capacitor a tierra. Para obtener pulsos en ambos flancos se usa la cuadrada directa y una version invertida; esa inversion puede implementarse con una etapa `LF353`, que entra como acondicionamiento analogico y no como generador ideal.

Como se descarga en ambos flancos:

```text
fsaw = 2f0 = 4580 Hz
Tsaw = 1/fsaw = 218.34 us
```

Carga RC:

```text
Vsaw = Vcc (1 - exp(-Tsaw/(Rcharge Csaw)))
```

Despeje:

```text
Rcharge = -Tsaw / (Csaw ln(1 - Vsaw/Vcc))
```

Con:

```text
Vcc = 15 V
Vsaw = 5 V
Csaw = 10 nF
```

Resultado:

```text
Rcharge = 53.8 kOhm
```

Valor usado:

```text
Rcharge = 53.6 kOhm
```

Medicion LTspice:

```text
f_saw = 4575.10 Hz
```

## 4. Triangular a f0/2 sin flip-flop externo

Se usa un segundo `NE555` como monoestable. La cuadrada principal dispara el monoestable. Mientras el monoestable esta temporizando, ignora el siguiente disparo; por eso vuelve a activarse cada dos periodos del oscilador.

Periodo de la cuadrada:

```text
T0 = 1/f0
T0 = 1/2290 = 436.68 us
```

Se escoge:

```text
tw = 1.05 T0
tw = 458.52 us
```

Entonces:

```text
Tdiv = 2T0
fdiv = f0/2 = 1145 Hz
```

Para el monoestable con NE555:

```text
tw = 1.1 Rdiv Cdiv
```

Con:

```text
Cdiv = 10 nF
```

Despeje:

```text
Rdiv = tw/(1.1 Cdiv)
Rdiv = 41.7 kOhm
```

Medicion LTspice del divisor:

```text
f_div = 1145.00 Hz
duty_div = 52.45 %
```

Como el duty no es exactamente 50 %, el cambiador de nivel se ajusta para que la entrada del integrador tenga promedio cero.

Se escoge:

```text
Vhigh = +1.00 V
D = 0.525
```

Condicion:

```text
D Vhigh + (1-D) Vlow = 0
```

Despeje:

```text
Vlow = -D Vhigh/(1-D)
Vlow = -1.105 V
```

El bloque de nivel se implementa con `LF353` y convierte:

```text
0 V  -> -1.105 V
15 V -> +1.000 V
```

Luego un integrador inversor con `LF353` genera la triangular. Para el integrador:

```text
Delta V = Vhigh tw/(Rtri Ctri)
Delta V = 2 Vtri_pk
```

Despeje:

```text
Rtri = Vhigh tw/(2 Vtri_pk Ctri)
```

Con:

```text
Vtri_pk = 2 V
Ctri = 10 nF
```

Resultado:

```text
Rtri = 11.5 kOhm
```

## 5. Seleccion de entrada al filtro sin usar series

El enunciado pide escoger cual de las tres senales previas conviene filtrar para obtener una senal senoidal.

Con lo visto en Bode:

```text
Un pasabajas conserva mejor las variaciones lentas.
Un pasabajas reduce mas las variaciones rapidas.
```

Comparacion temporal:

```text
Cuadrada:
  cambia de nivel bruscamente.

Diente de sierra:
  sube de manera suave, pero regresa con un salto.

Triangular:
  no presenta salto de voltaje; solo cambia la pendiente.
```

Como la senal senoidal tambien es continua y sin saltos de voltaje, la triangular es la entrada mas conveniente para el pasabajas.

## 6. Filtro pasabajas de orden 5

El filtro activo se implementa con `LF353`, usando una etapa de primer orden y dos secciones Sallen-Key en cascada. Por el enunciado:

```text
Z = 9 -> Chebyshev
```

La materia indica que un filtro Chebyshev tiene transicion mas abrupta entre banda de paso y banda de rechazo, con rizado en banda de paso.

Frecuencia de entrada al filtro:

```text
ftri = 1145 Hz
```

Se escoge:

```text
fc = 1.25 ftri
fc = 1431.25 Hz
```

Asi, la frecuencia de interes queda dentro de la banda de paso.

La materia de filtros de orden superior indica que se conectan etapas en cascada:

```text
orden 5 = orden 1 + orden 2 + orden 2
```

Frecuencia normalizada:

```text
S = jw/w0 = jf/f0
```

Forma de segundo orden:

```text
H(S) = H0 N(S)/(1 + aS + bS^2)
```

Para pasabajas:

```text
N(S) = 1
```

Factor de calidad:

```text
Q = sqrt(b)/a
```

## 7. Tabla Chebyshev y calculo de componentes

De la tabla de coeficientes para un filtro Chebyshev tipo I de quinto orden se toman tres etapas:

```text
Etapa   Orden   a_i      b_i
1       1       2.7600   0
2       2       1.2296   2.0975
3       2       0.2162   0.9655
```

### Etapa 1: primer orden

Para una etapa pasabajas de primer orden:

```text
H1(S) = H01/(1 + a1 S)
```

La frecuencia del polo fisico es:

```text
fp1 = fc/a1
```

Con:

```text
fc = 1431.25 Hz
a1 = 2.7600
C = 10 nF
```

se obtiene:

```text
fp1 = 1431.25/2.7600 = 518.57 Hz
R1 = 1/(2 pi fp1 C)
R1 = 30.7 kOhm
```

Forma equivalente usando la tabla:

```text
R1 = a1/(2 pi fc C)
R1 = 30.7 kOhm
```

### Etapa 2: Sallen-Key de segundo orden

Para una etapa de segundo orden:

```text
H2(S) = H02/(1 + a2 S + b2 S^2)
```

La materia usa:

```text
Q2 = sqrt(b2)/a2
```

y la frecuencia natural fisica queda:

```text
fn2 = fc/sqrt(b2)
```

Con:

```text
a2 = 1.2296
b2 = 2.0975
```

se obtiene:

```text
Q2 = sqrt(2.0975)/1.2296 = 1.178
fn2 = 1431.25/sqrt(2.0975) = 988.25 Hz
R_SK1 = 1/(2 pi fn2 C)
R_SK1 = 16.1 kOhm
```

Para Sallen-Key con componentes iguales:

```text
Q = 1/(3 - K)
K = 3 - 1/Q
```

Entonces:

```text
K1 = 3 - 1/1.178 = 2.151
```

Con `Rg = 10 kOhm`:

```text
Rf1 = (K1 - 1)Rg
Rf1 = 11.5 kOhm
```

### Etapa 3: Sallen-Key de segundo orden

De la tabla:

```text
a3 = 0.2162
b3 = 0.9655
```

Entonces:

```text
Q3 = sqrt(0.9655)/0.2162 = 4.545
fn3 = 1431.25/sqrt(0.9655) = 1456.63 Hz
R_SK2 = 1/(2 pi fn3 C)
R_SK2 = 10.9 kOhm
```

Ganancia de la etapa:

```text
K2 = 3 - 1/4.545 = 2.780
```

Con `Rg = 10 kOhm`:

```text
Rf2 = (K2 - 1)Rg
Rf2 = 17.8 kOhm
```

### Atenuador de entrada

Las dos etapas Sallen-Key tienen ganancia:

```text
Ktotal = K1 K2
Ktotal = 2.151(2.780)
Ktotal = 5.98
```

Para compensar esa ganancia se usa un divisor de entrada:

```text
A = 1/Ktotal
Rtop = Rbot(Ktotal - 1)
```

Con:

```text
Rbot = 100 kOhm
```

queda:

```text
Rtop = 498 kOhm
```

## 8. Valores finales del filtro

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

## 9. Verificacion con Bode

La simulacion AC del filtro da:

```text
|H(1145 Hz)| = -11.12 dB
|H(3435 Hz)| = -62.29 dB
```

Diferencia:

```text
62.29 - 11.12 = 51.17 dB
```

Entonces el filtro deja pasar mucho mas la frecuencia de interes que una frecuencia tres veces mayor. Esto valida el comportamiento pasabajas con diagramas de Bode, tal como se trabaja en la materia.

## 10. Resumen

```text
NE555 astable:
Rosc = 31.46 kOhm
Cosc = 10 nF
f_square = 2290.02 Hz

Diente de sierra:
Rcharge = 53.6 kOhm
Csaw = 10 nF
f_saw = 4575.10 Hz

NE555 monoestable divisor:
Rdiv = 41.7 kOhm
Cdiv = 10 nF
f_div = 1145.00 Hz

Integrador triangular:
Rtri = 11.5 kOhm
Ctri = 10 nF
opamp = LF353

Filtro:
Chebyshev tipo I, orden 5
fc = 1431.25 Hz
opamp = LF353
```
