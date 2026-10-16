import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import { Info } from "lucide-react";
import { EsquemaEncuadre } from "@/components/esquema-encuadre";
import { DISPOSITIVOS, detectarDispositivo, type Dispositivo } from "@/lib/instrucciones-carga";
import type { LadoCamara } from "@/lib/esquema-encuadre";

/**
 * "Cómo grabar y subir los videos": un desplegable cerrado por defecto con una pestaña por dispositivo (la del dispositivo detectado
 * viene preseleccionada). La instrucción va ANTES de elegir el archivo (decisiones 029 y 030): si el teléfono convierte el video, no
 * hay arreglo posterior. Todas las pestañas llevan el esquema del encuadre recomendado.
 */
export function InstruccionesDeCarga({ lado }: { lado: LadoCamara }) {
  const [activa, setActiva] = useState<Dispositivo>("iphone");
  const botones = useRef<Record<string, HTMLButtonElement | null>>({});

  // Se detecta en el navegador (en el servidor no hay `navigator`): evita una diferencia entre el HTML del servidor y el del cliente.
  useEffect(() => {
    setActiva(detectarDispositivo(navigator.userAgent, navigator.maxTouchPoints));
  }, []);

  function alTeclear(e: KeyboardEvent<HTMLButtonElement>) {
    const i = DISPOSITIVOS.findIndex((d) => d.valor === activa);
    let n: number;
    if (e.key === "ArrowRight") n = (i + 1) % DISPOSITIVOS.length;
    else if (e.key === "ArrowLeft") n = (i - 1 + DISPOSITIVOS.length) % DISPOSITIVOS.length;
    else return;
    e.preventDefault();
    const v = DISPOSITIVOS[n].valor;
    setActiva(v);
    botones.current[v]?.focus();
  }

  return (
    <details className="mt-8 rounded-xl border border-neon/40 bg-neon/5 p-5">
      <summary className="flex cursor-pointer items-center gap-2 font-display text-base font-semibold">
        <Info className="h-4 w-4 text-neon" aria-hidden="true" />
        Cómo grabar y subir los videos
      </summary>

      <div role="tablist" aria-label="Dispositivo" className="mt-4 flex gap-1 border-b border-border">
        {DISPOSITIVOS.map((d) => {
          const sel = d.valor === activa;
          return (
            <button
              key={d.valor}
              ref={(el) => {
                botones.current[d.valor] = el;
              }}
              id={`tab-${d.valor}`}
              type="button"
              role="tab"
              aria-selected={sel}
              aria-controls={`panel-${d.valor}`}
              tabIndex={sel ? 0 : -1}
              onClick={() => setActiva(d.valor)}
              onKeyDown={alTeclear}
              className={
                "-mb-px rounded-t-md border-b-2 px-4 py-2 text-sm font-medium " +
                (sel ? "border-neon text-foreground" : "border-transparent text-muted-foreground hover:text-foreground")
              }
            >
              {d.etiqueta}
            </button>
          );
        })}
      </div>

      <div role="tabpanel" id={`panel-${activa}`} aria-labelledby={`tab-${activa}`} className="mt-4 text-sm">
        {activa === "iphone" && <PanelIphone />}
        {activa === "android" && <PanelAndroid />}
        {activa === "computadora" && <PanelComputadora />}

        <div className="mt-5 border-t border-border pt-4">
          <p className="text-xs text-muted-foreground">
            <span className="font-semibold text-foreground">Encuadre recomendado:</span> la cámara del lado contrario a la mano dominante
            (a la izquierda de un jugador diestro), fija, a la altura de la cadera y de día, sin contraluz. De perfil, a 90° del golpe; de
            tres cuartos, por delante en diagonal. Es la condición con la que se calibró el sistema; también se puede grabar del otro lado.
          </p>
          <div className="mt-3 grid grid-cols-2 gap-3">
            <EsquemaEncuadre encuadre="perfil" lado={lado} className="h-24 w-full" />
            <EsquemaEncuadre encuadre="tres_cuartos" lado={lado} className="h-24 w-full" />
          </div>
        </div>
      </div>
    </details>
  );
}

function PanelIphone() {
  return (
    <>
      <ol className="list-decimal space-y-1.5 pl-5">
        <li>
          Grabá en <strong>Cámara lenta</strong> a 240 fps, con el teléfono fijo.
        </li>
        <li>
          En <strong>Fotos → Editar</strong>, <strong>recortá</strong> solo el golpe (2 a 5 s) y, en la barra de rayitas, dejá{" "}
          <strong>todo el tramo a velocidad normal</strong>.
        </li>
        <li>
          Al subirlo, en el selector tocá <strong>Opciones → Formato: Actual</strong> (o guardalo en <strong>Archivos</strong> y elegilo desde
          ahí).
        </li>
      </ol>
      <p className="mt-3 text-xs text-muted-foreground">
        Lo que grabaste a 240 fps se conserva aunque se vea a velocidad normal. Si el recorte mantiene parte en cámara lenta, o si dejás el
        formato por defecto, el teléfono convierte el video y descarta fotogramas: queda por debajo de los 120 fps que hacen falta y no se
        puede analizar. Máximo 50 MB por video.
      </p>
    </>
  );
}

function PanelAndroid() {
  return (
    <>
      <ol className="list-decimal space-y-1.5 pl-5">
        <li>
          Grabá en <strong>Cámara lenta</strong> (no en «Súper cámara lenta»), con el teléfono fijo y a la mayor velocidad que ofrezca (240
          fps si la tiene; 120 fps como mínimo).
        </li>
        <li>
          En la <strong>Galería</strong> o en <strong>Fotos</strong>, <strong>recortá</strong> solo el golpe (2 a 5 s){" "}
          <strong>sin cambiar la velocidad</strong> ni aplicar efectos, y guardalo como un clip aparte.
        </li>
        <li>
          Elegí el archivo desde la carpeta de la <strong>Cámara</strong> o desde <strong>Archivos</strong>. <strong>Evitá</strong> subir un
          video que pasó por WhatsApp u otra app de mensajes (lo convierten) y, a veces, por Google Fotos: puede entregar una copia
          comprimida.
        </li>
      </ol>
      <p className="mt-3 text-xs text-muted-foreground">
        <strong>No está probado en todos los modelos de Android.</strong> El sistema lee la tasa real del archivo y te avisa si no llega a
        120 fps. Máximo 50 MB por video.
      </p>
    </>
  );
}

function PanelComputadora() {
  return (
    <>
      <ol className="list-decimal space-y-1.5 pl-5">
        <li>
          Pasá el <strong>original sin compresión</strong>: por cable (como unidad de archivos) o con <strong>«Descargar original»</strong>{" "}
          desde iCloud o Google Fotos. No uses copias «optimizadas» ni las que llegan por mensajería.
        </li>
        <li>
          <strong>Recortá sin recodificar</strong> (copia directa de los datos): por ejemplo con <strong>LosslessCut</strong>, que corta sin
          volver a codificar. Corta en fotogramas clave, así que el clip puede arrancar un poco antes del golpe. No uses «exportar» de un
          editor de video: recodifica.
        </li>
        <li>
          Comprobá que cada clip pese <strong>menos de 50 MB</strong> y tenga un solo golpe.
        </li>
      </ol>
      <p className="mt-3 text-xs text-muted-foreground">
        Si recodificás o bajás la calidad, se pierden fotogramas y el sistema puede rechazar el archivo (queda por debajo de 120 fps).
      </p>
    </>
  );
}
