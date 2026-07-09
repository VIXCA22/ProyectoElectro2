# Valores teoricos y simulados

Frecuencia base:

```text
f0 = 2290 Hz
DS = 2*f0 = 4580 Hz
SC_D2 = TRI = SEN = f0/2 = 1145 Hz
```

## Etapa 1: oscilador NE555 / cuadrada SC

| Parametro | Teorico | Simulado LTspice | Error |
|---|---:|---:|---:|
| Frecuencia de SC | 2290 Hz | 2289.8233 Hz | -0.00771 % |
| Ciclo de trabajo de SC | 50 % | 50.0105 % | +0.02091 % |
| Vpp de SC | -- | 14.9961 V | -- |
| Vpp de VC555 | -- | 5.0060 V | -- |

## Etapa 2: diente de sierra DS

| Parametro | Teorico | Simulado LTspice | Error |
|---|---:|---:|---:|
| Frecuencia de DS | 4580 Hz | 4579.3252 Hz | -0.01473 % |
| Vpp de DS | -- | 4.8940 V | -- |
| Vmax de RST_DS | -- | 14.1075 V | -- |

## Etapa 3A: divisor por 2 SC_D2

| Parametro | Teorico | Simulado LTspice | Error |
|---|---:|---:|---:|
| Frecuencia de SC_D2 | 1145 Hz | 1144.9076 Hz | -0.00807 % |
| Vpp de SC_D2 | -- | 4.9709 V | -- |

## Etapa 3B: integrador triangular TRI

| Parametro | Teorico | Simulado LTspice | Error |
|---|---:|---:|---:|
| Frecuencia directa de TRI | 1145 Hz | 1145.9762 Hz | +0.08526 % |
| Frecuencia de referencia desde SC_D2 | 1145 Hz | 1144.9076 Hz | -0.00807 % |
| Vpp de TRI | -- | 3.9933 V | -- |
| Nivel medio de TRI | -- | -0.0694 V | -- |

## Etapa 4: filtro Chebyshev / senoidal SEN

| Parametro | Teorico | Simulado LTspice | Error |
|---|---:|---:|---:|
| Frecuencia de SEN | 1145 Hz | 1144.8698 Hz | -0.01137 % |
| Vpp de SEN | -- | 0.8762 V | -- |
| Nivel medio de SEN | -- | -0.0301 V | -- |
| Ganancia Vpp(SEN)/Vpp(TRI) | -- | 0.2194 V/V | -- |

Respuesta AC del filtro Chebyshev:

| Punto | Magnitud |
|---|---:|
| H(1145 Hz) | -11.1189 dB |
| H(3435 Hz) | -62.2899 dB |
| Atenuacion extra de 3ra armonica | 51.1710 dB |

Nota: para la triangular, la referencia recomendada de frecuencia es `SC_D2`,
porque el integrador cambia la forma y el nivel, pero no el periodo impuesto
por el flip-flop.
