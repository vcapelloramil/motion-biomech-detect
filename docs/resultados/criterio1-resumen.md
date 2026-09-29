# Criterio 1 — resumen de la medición (decisión 014)

Generado por `python -m app.resumen_criterio1` desde los JSON de `docs/resultados/`. 1 fotograma = 4,17 ms.
**1a/1b** son la regla del criterio original (≥ 0,8 cada una); **1c** (coincidencia con el orden esperado) se
informa **aparte**, sin umbral, y no cuenta como éxito ni fallo. Para el brazo, 1c no es comparable con la
literatura (decisión 011).

## Sesión 2 — MEDICIÓN (conjunto de medición)

Motor `0.4.1`, commit `cefadb6575`, árbol sucio: False.

### τ = 1 fotograma(s) (PRIMARIA)

| grupo | conjunto | n | válidas | ordenables | 1a (todas) [IC95] | 1a (válidas) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |
| drive · perfil | par pelvis-torso | 6 | 6 | 6 | 1.00 [0.61–1.00] | 1.00 | 1.00 (`tp`) | 0.00 | **cumple** |
| drive · trescuartos | par pelvis-torso | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| drive · trescuartos | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| reves · perfil | par pelvis-torso | 6 | 6 | 4 | 0.67 [0.30–0.90] | 0.67 | 0.75 (`pt`) | 0.75 | no cumple |
| reves · trescuartos | par pelvis-torso | 6 | 6 | 6 | 1.00 [0.61–1.00] | 1.00 | 0.83 (`tp`) | 0.17 | **cumple** |
| reves · trescuartos | cadena | 6 | 6 | 6 | 1.00 [0.61–1.00] | 1.00 | 0.83 (`tpb`) | 0.17 | **cumple** |
| saque · perfil | par pelvis-torso | 6 | 6 | 6 | 1.00 [0.61–1.00] | 1.00 | 1.00 (`tp`) | 0.00 | **cumple** |
| saque · trescuartos | par pelvis-torso | 18 | 18 | 9 | 0.50 [0.29–0.71] | 0.50 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos | cadena | 18 | 18 | 9 | 0.50 [0.29–0.71] | 0.50 | 0.89 (`ptb`) | 0.89 | no cumple |
| saque · trescuartos · toma 02 | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02 | cadena | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`ptb`) | 1.00 | no cumple |
| saque · trescuartos · toma 02b | par pelvis-torso | 6 | 6 | 4 | 0.67 [0.30–0.90] | 0.67 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02b | cadena | 6 | 6 | 4 | 0.67 [0.30–0.90] | 0.67 | 0.75 (`ptb`) | 0.75 | no cumple |
| saque · trescuartos · toma 02c | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02c | cadena | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`ptb`) | 1.00 | no cumple |

### τ = 2 fotograma(s) (sensibilidad)

| grupo | conjunto | n | válidas | ordenables | 1a (todas) [IC95] | 1a (válidas) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |
| drive · perfil | par pelvis-torso | 6 | 6 | 6 | 1.00 [0.61–1.00] | 1.00 | 1.00 (`tp`) | 0.00 | **cumple** |
| drive · trescuartos | par pelvis-torso | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| drive · trescuartos | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| reves · perfil | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`pt`) | 1.00 | no cumple |
| reves · trescuartos | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`pt`) | 0.50 | no cumple |
| reves · trescuartos | cadena | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`ptb`) | 0.50 | no cumple |
| saque · perfil | par pelvis-torso | 6 | 6 | 6 | 1.00 [0.61–1.00] | 1.00 | 1.00 (`tp`) | 0.00 | **cumple** |
| saque · trescuartos | par pelvis-torso | 18 | 18 | 6 | 0.33 [0.16–0.56] | 0.33 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos | cadena | 18 | 18 | 5 | 0.28 [0.12–0.51] | 0.28 | 1.00 (`ptb`) | 1.00 | no cumple |
| saque · trescuartos · toma 02 | par pelvis-torso | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02 | cadena | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`ptb`) | 1.00 | no cumple |
| saque · trescuartos · toma 02b | par pelvis-torso | 6 | 6 | 4 | 0.67 [0.30–0.90] | 0.67 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02b | cadena | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`ptb`) | 1.00 | no cumple |
| saque · trescuartos · toma 02c | par pelvis-torso | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02c | cadena | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`ptb`) | 1.00 | no cumple |

### τ = 3 fotograma(s) (sensibilidad)

| grupo | conjunto | n | válidas | ordenables | 1a (todas) [IC95] | 1a (válidas) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |
| drive · perfil | par pelvis-torso | 6 | 6 | 5 | 0.83 [0.44–0.97] | 0.83 | 1.00 (`tp`) | 0.00 | **cumple** |
| drive · trescuartos | par pelvis-torso | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| drive · trescuartos | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| reves · perfil | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`pt`) | 1.00 | no cumple |
| reves · trescuartos | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`pt`) | 0.50 | no cumple |
| reves · trescuartos | cadena | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`ptb`) | 0.50 | no cumple |
| saque · perfil | par pelvis-torso | 6 | 6 | 6 | 1.00 [0.61–1.00] | 1.00 | 1.00 (`tp`) | 0.00 | **cumple** |
| saque · trescuartos | par pelvis-torso | 18 | 18 | 2 | 0.11 [0.03–0.33] | 0.11 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos | cadena | 18 | 18 | 1 | 0.06 [0.01–0.26] | 0.06 | 1.00 (`ptb`) | 1.00 | no cumple |
| saque · trescuartos · toma 02 | par pelvis-torso | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos · toma 02 | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos · toma 02b | par pelvis-torso | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02b | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos · toma 02c | par pelvis-torso | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`pt`) | 1.00 | no cumple |
| saque · trescuartos · toma 02c | cadena | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`ptb`) | 1.00 | no cumple |

### Complemento DESCRIPTIVO (no pre-registrado)

| grupo | n | mediana \|pelvis−torso\| (fot.) | \|Δ\| ≤ 1 fot. | mediana torso→brazo (fot.) | brazo después | \|Δ\| > 1 fot. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| perfil · drive | 6 | 4.5 | 0/6 | -30.0 | 0/6 | 6/6 |
| perfil · reves | 6 | 46.0 | 1/5 | -7.5 | 1/6 | 4/6 |
| perfil · saque | 6 | 15.5 | 0/6 | 7.5 | 4/6 | 6/6 |
| trescuartos · drive | 6 | 1.0 | 6/6 | 28.5 | 6/6 | 6/6 |
| trescuartos · reves | 6 | 2.0 | 0/6 | 22.0 | 6/6 | 6/6 |
| trescuartos · saque | 18 | 1.5 | 9/18 | 24.0 | 16/17 | 17/17 |

## Sesión 1 — RÉPLICA EXPLORATORIA (no independiente)

Motor `0.4.1`, commit `cefadb6575`, árbol sucio: False.

### τ = 1 fotograma(s) (PRIMARIA)

| grupo | conjunto | n | válidas | ordenables | 1a (todas) [IC95] | 1a (válidas) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |
| drive · perfil | par pelvis-torso | 6 | 6 | 4 | 0.67 [0.30–0.90] | 0.67 | 1.00 (`tp`) | 0.00 | no cumple |
| drive · trescuartos | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`pt`) | 1.00 | no cumple |
| drive · trescuartos | cadena | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`ptb`) | 1.00 | no cumple |
| reves · perfil | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 0.67 (`pt`) | 0.67 | no cumple |
| reves · trescuartos | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 0.67 (`tp`) | 0.33 | no cumple |
| reves · trescuartos | cadena | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 0.67 (`tpb`) | 0.33 | no cumple |
| saque · perfil | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`tp`) | 0.00 | no cumple |
| saque · trescuartos | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 0.67 (`pt`) | 0.67 | no cumple |
| saque · trescuartos | cadena | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`ptb`) | 1.00 | no cumple |
| saque · trescuartos · toma 01 | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 0.67 (`pt`) | 0.67 | no cumple |
| saque · trescuartos · toma 01 | cadena | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`ptb`) | 1.00 | no cumple |

### τ = 2 fotograma(s) (sensibilidad)

| grupo | conjunto | n | válidas | ordenables | 1a (todas) [IC95] | 1a (válidas) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |
| drive · perfil | par pelvis-torso | 6 | 6 | 4 | 0.67 [0.30–0.90] | 0.67 | 1.00 (`tp`) | 0.00 | no cumple |
| drive · trescuartos | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`pt`) | 1.00 | no cumple |
| drive · trescuartos | cadena | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`ptb`) | 1.00 | no cumple |
| reves · perfil | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`pt`) | 0.50 | no cumple |
| reves · trescuartos | par pelvis-torso | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`tp`) | 0.00 | no cumple |
| reves · trescuartos | cadena | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`tpb`) | 0.00 | no cumple |
| saque · perfil | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 1.00 (`tp`) | 0.00 | no cumple |
| saque · trescuartos | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`pt`) | 0.50 | no cumple |
| saque · trescuartos | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos · toma 01 | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`pt`) | 0.50 | no cumple |
| saque · trescuartos · toma 01 | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |

### τ = 3 fotograma(s) (sensibilidad)

| grupo | conjunto | n | válidas | ordenables | 1a (todas) [IC95] | 1a (válidas) | 1b (orden modal) | 1c (esperado) | Criterio 1 |
| --- | --- | ---: | ---: | ---: | --- | ---: | --- | ---: | --- |
| drive · perfil | par pelvis-torso | 6 | 6 | 3 | 0.50 [0.19–0.81] | 0.50 | 1.00 (`tp`) | 0.00 | no cumple |
| drive · trescuartos | par pelvis-torso | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`pt`) | 1.00 | no cumple |
| drive · trescuartos | cadena | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`ptb`) | 1.00 | no cumple |
| reves · perfil | par pelvis-torso | 6 | 6 | 2 | 0.33 [0.10–0.70] | 0.33 | 0.50 (`pt`) | 0.50 | no cumple |
| reves · trescuartos | par pelvis-torso | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`tp`) | 0.00 | no cumple |
| reves · trescuartos | cadena | 6 | 6 | 1 | 0.17 [0.03–0.56] | 0.17 | 1.00 (`tpb`) | 0.00 | no cumple |
| saque · perfil | par pelvis-torso | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos | par pelvis-torso | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos · toma 01 | par pelvis-torso | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |
| saque · trescuartos · toma 01 | cadena | 6 | 6 | 0 | 0.00 [0.00–0.39] | 0.00 | - (`-`) | - | no cumple |

### Complemento DESCRIPTIVO (no pre-registrado)

| grupo | n | mediana \|pelvis−torso\| (fot.) | \|Δ\| ≤ 1 fot. | mediana torso→brazo (fot.) | brazo después | \|Δ\| > 1 fot. |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| perfil · drive | 6 | 4.0 | 2/6 | -12.0 | 1/5 | 5/5 |
| perfil · reves | 6 | 1.5 | 3/6 | -4.5 | 1/6 | 6/6 |
| perfil · saque | 6 | 3.0 | 1/3 | 15.0 | 3/5 | 5/5 |
| trescuartos · drive | 6 | 1.5 | 3/6 | 27.5 | 5/6 | 6/6 |
| trescuartos · reves | 6 | 1.5 | 3/6 | 19.0 | 6/6 | 6/6 |
| trescuartos · saque | 6 | 1.5 | 3/6 | 26.5 | 6/6 | 5/6 |
