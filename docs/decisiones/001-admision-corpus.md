# Decisión 001 — Cómo se verifica un video antes de entrar al corpus

**Fecha:** 26 de agosto de 2026
**Estado:** vigente
**Afecta a:** Etapa 1 del plan de desarrollo · protocolo de grabación · Capítulo 6

---

## El problema

Un archivo de video puede declarar 25 fps y aun así contener información temporal
suficiente para el análisis, si fue grabado en cámara lenta. Pero también puede declarar
25 fps y estar "estirado" duplicando fotogramas, en cuyo caso se ve lento pero no aporta
ninguna información adicional.

Los dos casos son **indistinguibles a simple vista** e **indistinguibles por metadatos**.
Hace falta un criterio para separarlos, porque el segundo tipo de material no sirve para
medir velocidades ni el orden de los picos de la cadena cinética.

---

## Qué probamos primero (y por qué falló)

La primera idea fue usar el filtro `mpdecimate` de ffmpeg, que descarta fotogramas
parecidos al anterior, y mirar qué proporción sobrevive.

Aplicado a un video de saques de Zverev ralentizados, dio **63 % de fotogramas
conservados**, lo que según ese criterio significaba que un tercio del material estaba
duplicado y había que descartarlo.

**Era incorrecto.** Al revisar 25 fotogramas consecutivos uno por uno, se vio que en cada
paso el brazo del jugador estaba en una posición distinta: no había ninguna repetición.

La razón del error: `mpdecimate` no compara si dos fotogramas son idénticos, compara si
son **suficientemente parecidos** según un umbral. En un video muy ralentizado el
movimiento entre cuadros consecutivos es diminuto, cae por debajo de ese umbral, y el
filtro los descarta como si fueran repetidos.

La conclusión es contraintuitiva y conviene tenerla presente:

> Cuanto mejor es la cámara lenta, más falsos duplicados reporta `mpdecimate`.

Usar esa prueba habría llevado a descartar justamente el material de mejor calidad.

---

## Qué usamos en su lugar

Comparación por **huella digital de cada fotograma**. Dos fotogramas tienen la misma
huella solo si son exactamente iguales, sin umbrales ni interpretación.

```bash
ffmpeg -ss 00:00:02 -to 00:00:32 -i VIDEO.mp4 \
  -an -f framehash -hash md5 - 2>/dev/null \
  | grep -v '^#' | awk '{print $NF}' > /tmp/hashes.txt

echo "Total:  $(wc -l < /tmp/hashes.txt)"
echo "Únicos: $(sort -u /tmp/hashes.txt | wc -l)"
```

**Cómo se lee:**

| Únicos respecto del total | Interpretación | Uso del clip |
| --- | --- | --- |
| ~100 % | Captura real, sin duplicación | Sirve para todo (E1 a E4) |
| ~70–95 % | Alguna repetición aislada | Utilizable con reservas |
| ~33 % o ~50 % | Fotogramas duplicados de forma sistemática | Solo E1 y E2 |

Los valores cercanos a un tercio o a la mitad no son casuales: corresponden a material
estirado repitiendo cada cuadro tres o dos veces.

---

## Procedimiento de admisión al corpus

Todo video, propio o descargado, pasa por estos cuatro pasos antes de entrar al catálogo:

1. **Metadatos.** `ffprobe` para leer frecuencia declarada, cantidad de fotogramas,
   duración y resolución.
2. **Unicidad.** Prueba de huella sobre un tramo representativo, no sobre el archivo
   entero (los títulos y transiciones ensucian el resultado).
3. **Factor de ralentización**, solo si el clip es de cámara lenta. Se cronometra en
   pantalla el tramo entre la posición de máxima carga y el impacto del saque, que en
   tiempo real dura aproximadamente 0,25 s.
   `factor = duración en pantalla ÷ 0,25` · `fps efectivos = fps declarados × factor`
4. **Registro en `catalogo.csv`**, incluyendo el resultado de la prueba de unicidad y el
   uso permitido del clip.

**Ejemplo aplicado:** `zverev_saque_sideview.mp4` declara 25 fps, dio 750 huellas únicas
sobre 750 fotogramas, y el tramo carga-impacto dura unos 5 segundos en pantalla. Factor
estimado 20, frecuencia efectiva aproximada 500 fps. Admitido para E1 a E4, con la escala
temporal marcada como desconocida.

---

## Qué implica para el sistema

**Para la Etapa 1.** La validación de video no puede basarse solo en leer los metadatos.
Debe verificar dos cosas independientes: la frecuencia declarada **y** la unicidad de los
fotogramas. Un archivo puede aprobar una y fallar la otra.

**Para el catálogo.** Todo clip descargado se registra con `escala_temporal = desconocida`.
Eso significa que sirve para determinar el **orden** de los picos de velocidad —que no
cambia si todo el eje temporal está estirado por igual, según el apartado 3.3.4.2— pero no
para reportar velocidades absolutas en grados por segundo.

**Para el Capítulo 6.** Este es un modo de falla que la literatura de estimación de pose en
deporte no discute: los trabajos asumen que la frecuencia declarada de un archivo refleja
la frecuencia de captura. Se documenta como riesgo del sistema y como limitación del
material de origen público.

---

## Nota sobre el material propio

Para los videos grabados por nosotros a 240 fps este procedimiento igual se aplica, pero el
riesgo es distinto: no es duplicación de fotogramas sino que el archivo declare la
frecuencia de reproducción en lugar de la de captura. Ver el protocolo de grabación,
sección 7.
