import { useEffect, useState } from "react";
import { CircleDashed, Loader2 } from "lucide-react";
import { NOMBRE_SEGMENTO, type PicoNoMedidoLeido, type artefactosDe } from "@/lib/reporte-simple";
import { urlsDeArtefactos } from "@/lib/videos-data";
import { fmt } from "@/lib/formato";

/** Los tres fotogramas reales con el esqueleto en el pico de cadera, tronco y brazo, y el video corto con el esqueleto. */
export function TresMomentos({
  artefactos,
  noMedidos = [],
}: {
  artefactos: ReturnType<typeof artefactosDe>;
  /** Los picos que no se pudieron medir: se muestran como tarjeta, con su motivo, en vez de desaparecer. */
  noMedidos?: PicoNoMedidoLeido[];
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
    if (foto) tarjetas.push({ tipo: "foto", foto });
    else if (falta) tarjetas.push({ tipo: "falta", segmento: s, motivo: falta.motivo });
  }
  // Portada del video: el fotograma del pico del tronco (si no, el primero), para que no se vea negro antes de reproducir.
  const portada = artefactos.fotogramas.find((f) => f.segmento === "torso") ?? artefactos.fotogramas[0];
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
          {tarjetas.length > 0 && (
            <ul className="mt-5 flex snap-x gap-4 overflow-x-auto pb-2 md:grid md:grid-cols-3 md:overflow-visible">
              {tarjetas.map((c) =>
                c.tipo === "foto" ? (
                  <li key={c.foto.segmento} className="min-w-[78%] snap-center overflow-hidden rounded-2xl border border-border bg-card md:min-w-0">
                    {urls[c.foto.ruta] ? (
                      <img
                        src={urls[c.foto.ruta]}
                        alt={`Fotograma del golpe en el pico de velocidad de tu ${NOMBRE_SEGMENTO[c.foto.segmento]}, con el esqueleto dibujado`}
                        loading="lazy"
                        className="aspect-[3/4] w-full object-cover"
                      />
                    ) : (
                      <div className="flex aspect-[3/4] items-center justify-center text-sm text-muted-foreground">Sin imagen</div>
                    )}
                    <p className="px-4 py-3 text-sm">
                      <span className="font-semibold">Pico de tu {NOMBRE_SEGMENTO[c.foto.segmento]}</span>
                      <span className="font-mono text-xs text-muted-foreground"> · {fmt(c.foto.instante_s, 3)} s</span>
                    </p>
                  </li>
                ) : (
                  <li
                    key={c.segmento}
                    className="flex min-w-[78%] snap-center flex-col justify-center rounded-2xl border border-dashed border-border bg-card p-5 md:min-w-0"
                  >
                    <p className="flex items-center gap-2 font-semibold">
                      <CircleDashed className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                      Pico de tu {NOMBRE_SEGMENTO[c.segmento]}: no medido
                    </p>
                    <p className="mt-3 text-sm text-muted-foreground">{c.motivo}</p>
                  </li>
                ),
              )}
            </ul>
          )}
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
