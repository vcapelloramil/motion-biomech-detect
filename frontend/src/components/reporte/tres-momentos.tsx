import { useEffect, useState } from "react";
import { CircleDashed, Loader2 } from "lucide-react";
import { NOMBRE_SEGMENTO, type PicoNoMedidoLeido, type artefactosDe } from "@/lib/reporte-simple";
import { urlsDeArtefactos } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";
import type { FotosTexto } from "@/lib/textos-reporte";

/**
 * Fotos y video (decisión 039): los fotogramas reales con el esqueleto en el giro más rápido de cadera, tronco y brazo, y el video corto.
 * Si cadera y tronco quedaron a la vez, se muestra UNA sola foto (serían casi el mismo fotograma). Cada pieza lleva una línea de qué mirar.
 */
export function TresMomentos({
  artefactos,
  noMedidos = [],
  textos,
  desdeS = null,
}: {
  artefactos: ReturnType<typeof artefactosDe>;
  /** Los picos que no se pudieron medir: se muestran como tarjeta, con su motivo, en vez de desaparecer. */
  noMedidos?: PicoNoMedidoLeido[];
  textos: FotosTexto;
  /** Dónde empieza el tramo analizado, en segundos del video: para decir "a los X s del video". */
  desdeS?: number | null;
}) {
  const [urls, setUrls] = useState<Record<string, string> | null>(null);
  const rutas = [...artefactos.fotogramas.map((f) => f.ruta), ...(artefactos.overlay ? [artefactos.overlay.ruta] : [])];
  const clave = rutas.join("|");

  useEffect(() => {
    let activo = true;
    urlsDeArtefactos(rutas)
      .then((u) => activo && setUrls(u))
      .catch(() => activo && setUrls({}));
    return () => {
      activo = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clave]);

  const sinImagenes = urls !== null && Object.keys(urls).length === 0;
  // Siempre en el orden cadera, tronco, brazo; donde no hay fotograma y se sabe por qué, la tarjeta de "no medido".
  type Tarjeta =
    | { tipo: "foto"; foto: (typeof artefactos.fotogramas)[number] }
    | { tipo: "falta"; segmento: PicoNoMedidoLeido["segmento"]; motivo: string };
  const tarjetas: Tarjeta[] = [];
  for (const s of ["pelvis", "torso", "brazo"] as const) {
    const foto = artefactos.fotogramas.find((f) => f.segmento === s);
    const falta = noMedidos.find((n) => n.segmento === s);
    // Foto única: cadera y tronco están en el mismo fotograma; se queda la del tronco (o la de la cadera si es la única).
    if (textos.fotoUnica && (s === "pelvis" || s === "torso")) {
      const otra = artefactos.fotogramas.find((f) => f.segmento === (s === "pelvis" ? "torso" : "pelvis"));
      if (s === "pelvis" && otra) continue;
      if (foto) tarjetas.push({ tipo: "foto", foto });
      continue;
    }
    if (foto) tarjetas.push({ tipo: "foto", foto });
    else if (falta) tarjetas.push({ tipo: "falta", segmento: s, motivo: falta.motivo });
  }
  // Portada del video: el fotograma del pico del tronco (si no, el primero), para que no se vea negro antes de reproducir.
  const portada = artefactos.fotogramas.find((f) => f.segmento === "torso") ?? artefactos.fotogramas[0];
  const lento = artefactos.overlay?.factor_lento ?? null;
  return (
    <section aria-labelledby="momentos" className="mt-12">
      <h2 id="momentos" className="font-mono text-xs uppercase tracking-widest text-state-ok">Fotos y video</h2>
      <p className="mt-2 font-display text-2xl font-bold md:text-3xl">Así se veía tu cuerpo en su giro más rápido</p>

      {urls === null ? (
        <p role="status" className="mt-5 flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando las imágenes…
        </p>
      ) : sinImagenes ? (
        <p className="mt-5 rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground">
          No pudimos cargar las imágenes ahora. El análisis no cambia: probá recargar la página en un momento.
        </p>
      ) : (
        <>
          {tarjetas.length > 0 && (
            <ul className="mt-5 flex snap-x gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-3 md:overflow-visible">
              {tarjetas.map((c) =>
                c.tipo === "foto" ? (
                  <li key={c.foto.segmento} className="min-w-[78%] snap-center overflow-hidden rounded-2xl border border-border bg-card md:min-w-0">
                    {urls[c.foto.ruta] ? (
                      <img
                        src={urls[c.foto.ruta]}
                        alt={
                          textos.fotoUnica
                            ? "Fotograma del golpe en el giro más rápido de tu cadera y de tu tronco, con el esqueleto dibujado"
                            : `Fotograma del golpe en el giro más rápido de tu ${NOMBRE_SEGMENTO[c.foto.segmento]}, con el esqueleto dibujado`
                        }
                        loading="lazy"
                        className="aspect-[3/4] w-full object-cover"
                      />
                    ) : (
                      <div className="flex aspect-[3/4] items-center justify-center text-sm text-muted-foreground">Sin imagen</div>
                    )}
                    <p className="px-4 py-3 text-sm">
                      {textos.fotoUnica && textos.etiquetaFotoUnica ? (
                        <span className="font-semibold">{textos.etiquetaFotoUnica}</span>
                      ) : (
                        <>
                          <span className="font-semibold">Giro más rápido de tu {NOMBRE_SEGMENTO[c.foto.segmento]}</span>
                          {desdeS !== null && (
                            <span className="font-mono text-xs text-muted-foreground"> · a los {fmt(desdeS + c.foto.instante_s, 2)} s del video</span>
                          )}
                        </>
                      )}
                    </p>
                  </li>
                ) : (
                  <li
                    key={c.segmento}
                    className="flex min-w-[78%] snap-center flex-col justify-center rounded-2xl border border-dashed border-border bg-card p-5 md:min-w-0"
                  >
                    <p className="flex items-center gap-2 font-semibold">
                      <CircleDashed className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                      Giro más rápido de tu {NOMBRE_SEGMENTO[c.segmento]}: no medido
                    </p>
                    <p className="mt-3 text-sm text-muted-foreground">{c.motivo}</p>
                  </li>
                ),
              )}
            </ul>
          )}
          {tarjetas.length > 0 && <p className="mt-3 text-sm text-muted-foreground">{textos.queMirarFoto}</p>}
          {artefactos.overlay && urls[artefactos.overlay.ruta] && (
            <div className="mt-6">
              <video
                src={urls[artefactos.overlay.ruta]}
                controls
                playsInline
                preload="metadata"
                poster={portada ? urls[portada.ruta] : undefined}
                className="w-full max-w-xs rounded-2xl border border-border bg-black md:max-w-sm"
                aria-label="Video corto del golpe con el esqueleto dibujado"
              />
              <p className="mt-2 text-sm text-muted-foreground">
                {textos.video ?? `Solo el tramo del golpe${lento ? `, en cámara lenta (${fmt(lento, 0)} veces más lento que la realidad)` : ""}.`}{" "}
                {textos.queMirarVideo} El esqueleto se dibuja únicamente donde el sistema detectó cada articulación con confianza suficiente.
              </p>
            </div>
          )}
        </>
      )}
    </section>
  );
}
