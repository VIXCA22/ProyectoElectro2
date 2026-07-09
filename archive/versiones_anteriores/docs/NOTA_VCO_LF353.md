# Nota de diseno: referencia tipo VCO con LF353

Esta nota resume como interpretar la figura del libro sin desviarse del
enunciado del proyecto IE0413. El enunciado es la referencia principal: las
frecuencias, formas de onda y simulaciones deben cumplir exactamente lo que se
pide ahi.

La figura tipo VCO no sustituye el diseno del proyecto. Solo sirve como apoyo
conceptual para entender el uso de un disparador Schmitt y una etapa de
integracion.

## 0. Requisitos que no se deben cambiar

Con los carnes usados en este repo:

```text
X = 2
Y = 2
Z = 9
f0 = 2.29 kHz
```

Por el enunciado, el diseno debe entregar:

```text
onda cuadrada:       f0      = 2.29 kHz, ciclo de trabajo 50%
diente de sierra:    2 f0    = 4.58 kHz, exclusivamente positiva
onda triangular:     f0 / 2  = 1.145 kHz, con excursion positiva y negativa
onda senoidal:       por filtro pasabajas activo de orden 5
filtro:              Chebyshev, porque Z = 9
simulacion final:    las cuatro senales juntas
```

Todo circuito propuesto debe respetar esas condiciones. Si una topologia genera
otra frecuencia, no se usa como salida final de esa seccion.

## 1. Que hace la figura original

La figura usa dos bloques:

- un integrador, que convierte una corriente casi constante en una rampa;
- un disparador Schmitt, que cambia de estado cuando la rampa cruza dos
  umbrales.

En el circuito original con 3160, la salida cuadrada conmuta un FET. Ese FET
cambia el signo de la corriente del integrador, de modo que la rampa sube y
baja con la misma pendiente. Por eso se obtiene una onda triangular y una onda
cuadrada sincronizadas.

Si se conservan las proporciones de la figura:

```text
R1 = R
R2 = R3 = R4 = R/2
R5 = R6 = R7
```

La corriente de integracion tiene magnitud:

```text
I = Vin/(2R)
```

Los umbrales del Schmitt son aproximadamente:

```text
V+ / 3  y  2V+ / 3
```

La excursion de la triangular es:

```text
Delta V = V+ / 3
```

Entonces:

```text
T = 4 R C V+ / (3 Vin)
f = 3 Vin / (4 R C V+)
```

Con los valores de la figura, `R = 100 kOhm` y `C = 0.05 uF`:

```text
f = 150 Vin/V+  Hz
```

## 2. Cambio importante al usar LF353

El 3160 de la figura se escogio porque puede trabajar con una sola fuente
positiva y acercar mucho su salida a los rieles. El LF353 no debe tratarse como
rail-to-rail.

El enunciado no especifica la alimentacion. Por tanto, la alimentacion es una
decision de diseno. En los archivos LTspice de este repo se escoge
alimentacion dual:

```text
VCC+ = +15 V
VCC- = -15 V
```

Esta escogencia no viene impuesta por el enunciado; se justifica porque deja
las entradas lejos del riel negativo, da margen a las salidas y coincide con el
macromodelo `LF353/NS` usado en la simulacion. Otra alimentacion podria usarse
si se demuestra que respeta el rango de entrada, la excursion de salida y las
formas de onda pedidas.

Por eso, la idea de la figura se aplica como arquitectura:

```text
Schmitt + integracion + realimentacion
```

pero no conviene copiar literalmente los umbrales `V+/3` y `2V+/3` suponiendo
salida entre `0 V` y `V+`.

## 3. Aplicacion correcta al enunciado

El proyecto no pide un VCO variable, sino frecuencias fijas segun los carnes.
Por eso no se disena una entrada `Vin` para variar la frecuencia. La frecuencia
central se fija directamente en:

```text
f0 = 2.29 kHz
```

La parte tipo VCO se puede usar conceptualmente para el oscilador central:
un Schmitt genera la cuadrada y una red RC fija el periodo. En el archivo
`ltspice/oscilador_cuadrado_LF353.cir` esto ya queda implementado con LF353.

Para esa etapa:

```text
beta = R2/(R1 + R2)
T = 2 R C ln((1 + beta)/(1 - beta))
f0 = 1/T
```

Con:

```text
R1 = R2 = 100 kOhm
beta = 0.5
C = 10 nF
```

Se obtiene:

```text
R = 1/(2 f0 C ln(3))
R = 19.9 kOhm
```

En LTspice se usa `20.3 kOhm` por el factor `Ktrim`, para compensar el retardo
del macromodelo no ideal del LF353. La medicion del log da aproximadamente:

```text
f_square = 2289.87 Hz
```

## 4. Relacion con las otras ondas del proyecto

La salida triangular directa de la figura original tendria la misma frecuencia
que la cuadrada. Eso no cumple la seccion triangular del enunciado, porque ahi
se pide:

```text
ftri = f0/2 = 1.145 kHz
```

Por eso, para el proyecto completo se mantiene esta separacion:

```text
onda cuadrada:       f0      = 2.29 kHz
diente de sierra:    2 f0    = 4.58 kHz
onda triangular:     f0 / 2  = 1.145 kHz
filtro pasabajas:    orden 5, Chebyshev porque Z = 9
```

La idea de la figura sirve muy bien para justificar el uso de Schmitt,
integracion y realimentacion. Pero la triangular que pide el enunciado debe
generarse desde una senal dividida por dos, seguida por cambiador de nivel e
integrador, como esta en `ltspice/triangular_f0_2_LF353.cir`.

## 5. Decision de diseno para la entrega

Para apegarse al enunciado, se mantiene el diseno ya separado por etapas:

- Con LF353, justificar la alimentacion escogida; en esta propuesta se usa
  `+15 V` y `-15 V` por margen de operacion y estabilidad en simulacion.
- Mantenga el oscilador central en `f0 = 2.29 kHz`.
- Use el Schmitt RC validado para la cuadrada.
- Genere la diente de sierra a `2f0` con reset en ambos flancos.
- Genere la triangular a `f0/2`; no use la triangular directa del VCO como
  salida final de esa seccion.
- Para la senoidal use la triangular, porque sus armonicos decrecen como
  `1/n^2` y el filtro necesita atenuar menos contenido no deseado.

En resumen: la figura del VCO ayuda a justificar teoria, pero la memoria y las
simulaciones deben seguir los bloques pedidos por el enunciado.
