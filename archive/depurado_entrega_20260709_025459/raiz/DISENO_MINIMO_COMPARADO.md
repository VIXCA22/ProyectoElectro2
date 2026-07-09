# Diseno minimo comparado - NE555 + LF353

Esta es la version final y mas sencilla para defender calculos y simulacion:
un `NE555` como oscilador base y `LF353` en las etapas analogicas.

## Arquitectura recomendada

```text
NE555 astable a f0
  -> salida cuadrada a f0
  -> detectores de flanco para resetear la sierra a 2f0
  -> verificacion equivalente a f0/2 para excitar el integrador triangular

LF353
  -> inversor/buffer donde haga falta
  -> cambiador de nivel
  -> integrador triangular
  -> filtro activo Chebyshev de orden 5
```

Para verificar la triangular a `f0/2`, se usa una senal cuadrada equivalente de
periodo doble y despues el integrador LF353. Asi la simulacion comprueba la
etapa analogica sin agregar otro `NE555` ni un bloque extra que ensucie los
calculos.

## Datos base

```text
X = 2
Y = 2
Z = 9
f0 = 2.29 kHz = 2290 Hz
fsaw = 2 f0 = 4580 Hz
ftri = f0/2 = 1145 Hz
Filtro: Chebyshev, porque Z = 9
```

## 1. Cuadrada con un solo NE555

Conexion:

```text
TRIG = THRES = nodo del capacitor
Rosc entre OUT y el capacitor
Cosc a tierra
RESET a +15 V
CONT con 10 nF a tierra
```

Calculo:

```text
tH = Rosc Cosc ln(2)
tL = Rosc Cosc ln(2)
T = 2 Rosc Cosc ln(2)
Rosc = 1/(2 f0 Cosc ln(2))
```

Con:

```text
Cosc = 10 nF
```

Resultado:

```text
Rosc = 31.5 kOhm
```

En LTspice se usa:

```text
Rosc = 31.46 kOhm
```

## 2. Sierra positiva a 2f0

Se carga `Csaw` con una resistencia desde `+15 V` y se descarga rapidamente con
un `2N3904` en cada flanco de la cuadrada. Como se descarga en ambos flancos:

```text
fsaw = 2 f0
Tsaw = 1/(2 f0)
```

Carga RC:

```text
Vsaw = Vcc (1 - exp(-Tsaw/(Rcharge Csaw)))
```

Despeje:

```text
Rcharge = -Tsaw/(Csaw ln(1 - Vsaw/Vcc))
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

## 3. Triangular a f0/2 con LF353

La entrada cuadrada equivalente a `f0/2` se acondiciona a una senal de `-1 V` a
`+1 V` y entra al integrador inversor con LF353.

Para una entrada cuadrada simetrica de amplitud `Vdrv`, durante medio ciclo de
la triangular:

```text
Delta V = Vdrv T0/(Rtri Ctri)
```

Como la triangular debe cambiar de `-Vtri_pk` a `+Vtri_pk`:

```text
Delta V = 2 Vtri_pk
```

Entonces:

```text
Rtri = Vdrv/(2 Vtri_pk f0 Ctri)
```

Con:

```text
Vdrv = 1 V
Vtri_pk = 2 V
Ctri = 10 nF
f0 = 2290 Hz
```

Resultado:

```text
Rtri = 10.9 kOhm
```

## 4. Filtro activo

Se usa el filtro Chebyshev tipo I de orden 5 ya calculado con las tablas de la
materia. La entrada recomendada es la triangular porque es la senal previa mas
continua: no tiene salto de voltaje, solo cambio de pendiente.

```text
ftri = 1145 Hz
fc = 1.25 ftri = 1431.25 Hz
```

Valores principales:

```text
Atenuador:
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

## Comparacion calculo vs simulacion

| Senal | Calculado | Simulado LTspice | Error |
|---|---:|---:|---:|
| Cuadrada | 2290.00 Hz | 2290.02 Hz | +0.0007 % |
| Sierra | 4580.00 Hz | 4579.997 Hz | -0.00007 % |
| Triangular | 1145.00 Hz | 1144.999 Hz | -0.00005 % |

Para la sierra se usa la medicion promedio de dos rampas consecutivas:
`f_saw_avg = 2/T_saw_2cy`. Esto compensa el pequeno retardo diferente entre el
flanco directo y el flanco invertido. Para la triangular se mide el periodo de
`tri_drive`, la senal de `+1 V/-1 V` que entra al integrador LF353. El integrador
no cambia el periodo, solo convierte la cuadrada acondicionada en rampa
triangular.

Para el filtro:

| Punto de Bode | Simulacion |
|---|---:|
| `|H(1145 Hz)|` | `-11.12 dB` |
| `|H(3435 Hz)|` | `-62.29 dB` |
| Diferencia | `51.17 dB` |

Eso confirma que el pasabajas conserva mucho mas la frecuencia de interes que
una frecuencia bastante mayor.

En transitorio, la salida filtrada se grafica despues del arranque del filtro.
La medicion de la senoidal da:

```text
f_sine = 1145.00000589 Hz
```

## Archivos usados para comparar

```text
ltspice/oscilador_555_astable_f0.cir
ltspice/diente_sierra_2f0_LF353.cir
ltspice/triangular_f0_2_LF353.cir
ltspice/filtro5_bode_LF353.cir
ltspice/filtro5_transitorio_LF353.cir
```
