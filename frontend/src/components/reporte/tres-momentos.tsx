import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { NOMBRE_SEGMENTO, type artefactosDe } from "@/lib/reporte-simple";
import { urlsDeArtefactos } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

/** Los tres fotogramas reales con el esqueleto en el pico de cadera, tronco y brazo, y el video corto con el esqueleto. */
export function TresMomentos({ artefactos }: { artefactos: ReturnType<typeof artefactosDe> }) {
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
  const lento = artefactos.overlay?.factor_lento ?? null;
  return (
    <section aria-labelledby="momentos" className="mt-12">
      <h2 id="momentos" className="font-mono text-xs uppercase tracking-widest text-state-ok">Tres momentos de tu golpe</h2>
      <p className="mt-2 font-display text-2xl font-bold md:text-3xl">Así se veía tu cuerpo en cada pico</p>

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
          {artefactos.fotogramas.length > 0 && (
            <ul className="mt-5 flex snap-x gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-3 md:overflow-visible">
              {artefactos.fotogramas.map((f) => (
                <li key={f.segmento} className="min-w-[78%] snap-center overflow-hidden rounded-2xl border border-border bg-card md:min-w-0">
                  {urls[f.ruta] ? (
                    <img
                      src={urls[f.ruta]}
                      alt={`Fotograma del golpe en el pico de velocidad de tu ${NOMBRE_SEGMENTO[f.segmento]}, con el esqueleto dibujado`}
                      loading="lazy"
                      className="aspect-[3/4] w-full object-cover"
                    />
                  ) : (
                    <div className="flex aspect-[3/4] items-center justify-center text-sm text-muted-foreground">Sin imagen</div>
                  )}
                  <p className="px-4 py-3 text-sm">
                    <span className="font-semibold">Pico de tu {NOMBRE_SEGMENTO[f.segmento]}</span>
                    <span className="font-mono text-xs text-muted-foreground"> · {fmt(f.instante_s, 3)} s</span>
                  </p>
                </li>
              ))}
            </ul>
          )}
          {artefactos.overlay && urls[artefactos.overlay.ruta] && (
            <div className="mt-6">
              <video
                src={urls[artefactos.overlay.ruta]}
                controls
                playsInline
                preload="metadata"
                className="w-full max-w-xs rounded-2xl border border-border bg-black md:max-w-sm"
                aria-label="Video corto del golpe con el esqueleto dibujado"
              />
              <p className="mt-2 text-xs text-muted-foreground">
                Solo el tramo del golpe{lento ? `, en cámara lenta (${fmt(lento, 0)} veces más lento que la realidad)` : ""}. El esqueleto se
                dibuja únicamente donde el sistema detectó cada articulación con confianza suficiente.
              </p>
            </div>
          )}
        </>
      )}
    </section>
  );
}
