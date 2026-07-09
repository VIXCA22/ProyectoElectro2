# Diseno simple para cumplir el enunciado IE0413

Esta es la version recomendada para defender el proyecto sin usar fuentes
`PULSE` como generadores de onda. La idea es mantener cada bloque simple y
explicable.

## Datos del grupo

Orden alfabetico por primer apellido:

```text
Madriz, Torres, Vizcaino
```

Por tanto:

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

## 1. Onda cuadrada: astable con NE555

El enunciado pide un circuito astable. La opcion mas sencilla es un NE555 en
modo Schmitt:

```text
TRIG y THRS unidos al capacitor Cosc.
Rosc desde OUT hasta Cosc.
Cosc a tierra.
RESET a Vcc.
Vcc = 15 V DC.
```

El capacitor carga y descarga entre `1/3 Vcc` y `2/3 Vcc`, por lo que:

```text
tH = R C ln(2)
tL = R C ln(2)
T  = 2 R C ln(2)
f0 = 1 / (2 R C ln(2))
```

Con:

```text
Cosc = 10 nF
f0 = 2290 Hz
```

```text
Rosc = 1 / (2 f0 Cosc ln(2))
Rosc = 31.5 kOhm
```

En LTspice se usa:

```text
Rosc = 31.46 kOhm
```

para compensar el modelo del NE555. La simulacion da:

```text
f_square = 2290.02 Hz
duty = 50.00 %
```

Archivo:

```text
ltspice/oscilador_555_astable_f0.cir
```

## 2. Diente de sierra positivo a 2f0

La forma mas sencilla es cargar un capacitor y descargarlo rapidamente en cada
flanco de la onda cuadrada.

Bloques:

```text
1. Onda cuadrada del 555.
2. Inversor con 2N3904 para obtener la cuadrada invertida.
3. Dos detectores de flanco RC, uno con la cuadrada y otro con la invertida.
4. Diodos 1N4148 para unir los pulsos de reset.
5. 2N3904 de descarga del capacitor.
6. Resistencia de carga desde +15 V al capacitor de sierra.
```

Como se descarga en ambos flancos:

```text
fsaw = 2 f0 = 4580 Hz
Tsaw = 1 / fsaw = 218.3 us
```

Para una sierra positiva de aproximadamente `0 V` a `5 V`, con carga RC desde
`15 V`:

```text
Vsaw = Vcc (1 - exp(-Tsaw/(R C)))
```

Despejando:

```text
R = -Tsaw / (C ln(1 - Vsaw/Vcc))
```

Con:

```text
Vcc = 15 V
Vsaw = 5 V
Csaw = 10 nF
```

```text
Rcharge = 53.8 kOhm
```

Valores recomendados:

```text
Rcharge = 53.6 kOhm
Csaw    = 10 nF
Cedge   = 220 pF, dos unidades
Redge   = 10 kOhm, dos unidades
D       = 1N4148
Qreset  = 2N3904
```

## 3. Onda triangular a f0/2

Para que la triangular quede a la mitad de la frecuencia del oscilador, se usa
un divisor por 2 real, por ejemplo un CD4013.

Bloques:

```text
1. Cuadrada del 555.
2. CD4013 conectado como divisor por 2.
3. Divisor resistivo para pasar de 0-15 V a 0-2 V.
4. Restador con LF353 para convertir 0-2 V en -1 V a +1 V.
5. Integrador inversor con LF353.
```

Para el divisor resistivo:

```text
0-15 V  ->  0-2 V
```

se usa:

```text
Rtop = 65 kOhm
Rbot = 10 kOhm
```

Para la referencia de `1 V`:

```text
Rtop = 140 kOhm
Rbot = 10 kOhm
```

El restador usa cuatro resistencias iguales:

```text
R = 10 kOhm
```

El integrador debe producir `Vtri_pk = 2 V`. Con entrada de `Vdrv = 1 V`:

```text
Rtri = Vdrv / (2 Vtri_pk f0 Ctri)
```

Con:

```text
Vdrv = 1 V
Vtri_pk = 2 V
Ctri = 10 nF
f0 = 2290 Hz
```

```text
Rtri = 10.9 kOhm
```

## 4. Senoidal: filtro pasabajas de orden 5

La entrada recomendada para el filtro es la triangular, porque sus armonicos
decrecen como `1/n^2`.

Como:

```text
Z = 9
```

el enunciado pide respuesta:

```text
Chebyshev
```

Se usa Chebyshev tipo I de `0.5 dB`, orden 5, formado por:

```text
1 etapa RC de primer orden
2 etapas Sallen-Key de segundo orden
```

Frecuencia de corte:

```text
ftri = 1145 Hz
fc = 1.25 ftri = 1431.25 Hz
```

Valores con `C = 10 nF`:

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

### Como defender la parte de filtros

La entrada al filtro debe ser la triangular. La razon matematica es que sus
armonicos decrecen mas rapido:

```text
cuadrada:  armonicos impares con amplitud proporcional a 1/n
sierra:    armonicos pares e impares con amplitud proporcional a 1/n
triangular: armonicos impares con amplitud proporcional a 1/n^2
```

Comparando el primer armonico no deseado:

```text
cuadrada:   tercer armonico = 1/3  = -9.54 dB respecto a la fundamental
triangular: tercer armonico = 1/9  = -19.08 dB respecto a la fundamental
```

La triangular ya llega al filtro con el tercer armonico `9.54 dB` mas bajo que
la cuadrada, y ademas no tiene armonicos pares. Por eso necesita menos esfuerzo
del filtro para parecer senoidal.

Para conectar con la materia de filtros activos:

```text
S = j w / w0
orden 5 = 1 + 2 + 2
```

La etapa real de primer orden tiene la forma:

```text
H1(S) = H0 / (1 + a S)
```

Cada etapa Sallen-Key de segundo orden se usa con componentes iguales:

```text
R1 = R2 = R
C1 = C2 = C
fn = 1/(2 pi R C)
Q = 1/(3 - K)
K = 3 - 1/Q
K = 1 + Rf/Rg
```

El Bode simulado del filtro da:

```text
|H(ftri)|  = -11.12 dB  en 1145 Hz
|H(3ftri)| = -62.29 dB  en 3435 Hz
```

Solo por el filtro, el tercer armonico cae:

```text
62.29 - 11.12 = 51.17 dB
```

Sumando que la triangular ya trae su tercer armonico `19.08 dB` por debajo de
la fundamental, el tercer armonico a la salida queda aproximadamente:

```text
51.17 + 19.08 = 70.25 dB
```

por debajo de la fundamental. Eso justifica que la salida se vea senoidal con
margen.

## Resumen de integrados

```text
NE555   x1  oscilador cuadrado
CD4013  x1  divisor por 2 para triangular
LF353   x3  restador, integrador, buffers y filtro activo
```

## Por que esta version es la mas simple

- Cumple el astable real pedido por el enunciado.
- No usa una fuente `PULSE` para fingir la cuadrada.
- Usa el LF353 donde es natural usar op amps: integradores, buffers y filtros.
- Mantiene el filtro de orden 5 ya calculado.
- Evita usar el LF353 como comparador principal, que es mas problematico en
  simulacion.
