# Paso B del recálculo con la tasa real — resultado completo (13/10/2026)

**Qué es:** los 6 grupos del corpus (saque, drive y revés; perfil y tres cuartos; dos sesiones) medidos sobre los **originales** del iPhone (~200 fps reales, marcas de tiempo reales), regularizados a la grilla de
240 Hz con los puntos interpolados contados, con la **misma constante de "ordenable" que el producto** (1/120 s = 8,33 ms, estricta; decisión 032). Arnés: `backend/app/medicion_paso_b.py`; resultados:
`paso-b-sesion-1.json` (réplica exploratoria, no independiente) y `paso-b-sesion-2.json` (medición); commit `7c9535c`, árbol limpio, motor 0.5.1. **76 repeticiones medidas** (35 + 41). Excluidas: las 2 que empiezan en la
rampa y las 6 de `IMG_6391` (original incompleto). El saque ya estaba resumido en `paso-b-saque.md`; **esto lo completa con drive y revés** y no lo reemplaza.

**Qué es el "resultado de la tesis":** el Paso B es la medición definitiva (plan de recálculo §3). El Paso A (`paso-a-resumen.md`) queda como control.

## 1. Orden de cadera y tronco por grupo

Δ = t_tronco − t_cadera: positivo = la cadera llegó primero; "dentro" = |Δ| ≤ 8,33 ms (no ordenable).

| Grupo | Válidas | Cadera primero | Tronco primero | Dentro de 8,33 ms | Mediana de Δ s1 · s2 (ms) |
| --- | --- | --- | --- | --- | --- |
| Saque · perfil | 10 | 0 | 8 | 2 | -18,7 · -162,5 |
| Saque · tres cuartos | 18 | 7 | 0 | 11 | 4,2 · 10,4 |
| Drive · perfil | 12 | 1 | 7 | 4 | -2,1 · -20,8 |
| Drive · tres cuartos | 12 | 3 | 0 | 9 | 6,2 · 0,0 |
| Revés · perfil | 11 | 3 | 3 | 5 | 4,2 · -4,2 |
| Revés · tres cuartos | 12 | 0 | 5 | 7 | -8,3 · -10,4 |

## 2. ¿Depende del encuadre? Por gesto

| Gesto | Perfil: cadera / tronco primero | Tres cuartos: cadera / tronco primero | Fisher (exploratorio) |
| --- | --- | --- | --- |
| Saque | 0 / 8 | 7 / 0 | p = 0,000 |
| Drive | 1 / 7 | 3 / 0 | p = 0,024 |
| Revés | 3 / 3 | 0 / 5 | p = 0,182 |

- **Saque y drive: sí, y en el mismo sentido.** En perfil el tronco llega primero y en tres cuartos la cadera llega primero o queda dentro de la tolerancia. Drive: p = 0,024 (exploratorio).
- **Revés: no sigue ese patrón.** En tres cuartos el tronco llega primero en las 5 repeticiones ordenables (ninguna con la cadera primero), y en perfil queda 3 contra 3. **Un cambio de encuadre no explica por sí solo
  el revés**: el "tronco primero" del revés de tres cuartos o es del gesto, o es otro sesgo del estimador. **No se puede decidir con estos datos.**
- **Todo es de un jugador, dos sesiones**; las repeticiones de una misma toma no son independientes. Los valores de p son exploratorios.

## 3. Criterio 1 (par cadera-tronco, tolerancia primaria 8,33 ms, 240 Hz regularizados)

| Grupo | Sesión 2 (medición): ordenables · 1a · 1b · orden · cumple | Sesión 1 (réplica): ordenables · 1a · 1b · orden · cumple |
| --- | --- | --- |
| Saque · perfil | 5/6 · 0,83 · 1,00 · tp · **sí** | 3/5 · 0,60 · 1,00 · tp · no |
| Saque · tres cuartos | 6/12 · 0,50 · 1,00 · pt · no | 1/6 · 0,17 · 1,00 · pt · no |
| Drive · perfil | 5/6 · 0,83 · 1,00 · tp · **sí** | 3/6 · 0,50 · 0,67 · tp · no |
| Drive · tres cuartos | 1/6 · 0,17 · 1,00 · pt · no | 2/6 · 0,33 · 1,00 · pt · no |
| Revés · perfil | 4/5 · 0,80 · 0,50 · tp · no | 2/6 · 0,33 · 0,50 · tp · no |
| Revés · tres cuartos | 3/6 · 0,50 · 1,00 · tp · no | 2/6 · 0,33 · 1,00 · tp · no |

- **Solo cumplen, en la sesión de medición, el saque de perfil y el drive de perfil**, los dos con el tronco primero. **En la réplica no cumple ningún grupo.** Ningún grupo de tres cuartos cumple: la causa es la resolución (más de la
  mitad de las repeticiones queda dentro de 8,33 ms), no la inconsistencia (1b = 1,00 en saque y drive).
- **Cambio contra el Paso A:** con los originales el drive de perfil pasa de 1a 0,50 a 0,83 (resolución de 5 ms en lugar de 8,3 ms). Es lo que el plan de recálculo anticipaba: algunos empates se resuelven y otros no.
- **Los grupos que cumplen son justamente los que el Paso A y el B ponen bajo sospecha** (el orden "tronco primero" que además depende del encuadre).

## 4. Controles exploratorios (no pre-registrados)

| Grupo | Correlación ω cadera–tronco (mediana s1 · s2) | Orden modal Winter · giro axial (s2) |
| --- | --- | --- |
| Saque · perfil | 0,92 · 0,55 | tp (5) · tp (5) |
| Saque · tres cuartos | 0,94 · 0,82 | pt (6) · pt (7) |
| Drive · perfil | 0,88 · 0,76 | tp (5) · tp (5) |
| Drive · tres cuartos | 0,92 · 0,93 | pt (1) · pt (1) |
| Revés · perfil | 0,80 · 0,53 | tp (4) · pt (3) |
| Revés · tres cuartos | 0,73 · 0,86 | tp (3) · tp (4) |

- **Sesión 2:** la correlación entre la velocidad angular de la cadera y la del tronco es **más baja en perfil (0,53–0,76) que en tres cuartos (0,82–0,93)**: en perfil la cadera es una señal más propia (y más ruidosa); en tres
  cuartos casi acompaña al tronco. **En la sesión 1** es alta en todos los grupos (0,73–0,94), así que la diferencia no es sistemática.
- **El orden modal no cambia con el giro axial** salvo en el **revés de perfil** (Winter: tronco primero; giro axial: cadera primero, 3 repeticiones): ese grupo es sensible al método y no se puede leer.

## 5. Consecuencias

1. **La decisión 035 (aplicada el 13/10) se sostiene y se extiende:** el saque no emite veredicto; **el drive tiene el mismo patrón** (perfil tronco primero, tres cuartos cadera primero) y no tiene referencia del orden en
   la tesis, así que no emite veredicto por la condición (a) de la 031.
2. **`RESPALDO_POR_GRUPO` (condición (b)) hay que revisarlo con estas cifras** (pendiente, **no se tocó**): `drive|perfil` pasa a cumplir (1a 0,83); `reves|tres_cuartos` y `reves|perfil` siguen sin cumplir; ningún veredicto
   cambia porque falta (a).
3. **D (contraste del encuadre) para drive y revés** necesita calibrarse con las poses de este Paso B (hoy solo está calibrado con el saque). El revés pide además otra pregunta (por qué el tronco primero en tres cuartos).
4. **Para el Capítulo 7:** el orden cadera-tronco medido con una sola cámara **no es confiable como veredicto** en este material: depende del encuadre en dos de tres gestos, y los grupos que cumplen el Criterio 1 son
   los sospechosos. Es un resultado con valor propio (límite declarado del instrumento).

## 6. Limitaciones

- Un jugador; 6 repeticiones por grupo y sesión (12 el saque de tres cuartos de la sesión 2); resolución de 5 ms por fotograma real.
- Sin medición independiente de la pelvis: no se puede decir cuál encuadre mide bien, solo qué dice el sistema en cada uno.
- Sin calibrar el contraste de encuadre para drive y revés; sin el Criterio 3 recalculado con el tiempo real (la métrica (ii) depende del tiempo).

## Reproducir

```bash
cd backend
PYTHONPATH=. .venv/Scripts/python.exe -u -m app.medicion_paso_b --reales "C:/Users/valen/Desktop/corpus-originales-reales" --salida ../docs/resultados/paso-b
```

Las poses salen de `backend/.cache/corpus-real-pose-b` (no versionada); los videos no están en el repositorio. Se niega a correr con el árbol sucio (decisión 014).
