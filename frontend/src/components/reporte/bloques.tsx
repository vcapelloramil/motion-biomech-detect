import type { ReactNode } from "react";
import { Link } from "@tanstack/react-router";
import { ArrowRight, BookOpen, ChevronDown, Info } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { BotonDescargarPdf } from "@/components/reporte/pdf";
import {
  GLOSARIO,
  VERSION_TEXTOS,
  type ClaveAyuda,
  type GrupoDetalle,
  type Item,
  type Literatura,
  type Profesional,
} from "@/lib/textos-reporte";

/**
 * Los bloques de pantalla de los reportes del golpe y de la sesión (decisión 039). Solo dibujan lo que arma `lib/textos-reporte.ts`:
 * ninguna frase se escribe acá, así la pantalla y el PDF dicen lo mismo.
 */

const TITULO = "font-mono text-xs uppercase tracking-widest text-state-ok";

/** El ⓘ: la explicación corta de un dato. Se abre con un toque (no depende de pasar el mouse) y se cierra con Escape. */
export function Ayuda({ clave }: { clave: ClaveAyuda }) {
  const g = GLOSARIO[clave];
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button
          type="button"
          aria-label={`Qué significa: ${g.termino}`}
          className="ml-1 inline-flex h-7 w-7 translate-y-[3px] items-center justify-center rounded-full text-muted-foreground hover:text-foreground focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent print:hidden"
        >
          <Info className="h-4 w-4" aria-hidden="true" />
        </button>
      </PopoverTrigger>
      <PopoverContent className="w-[min(18rem,calc(100vw-2rem))] text-sm" side="top" collisionPadding={16}>
        <p className="font-semibold">{g.termino}</p>
        <p className="mt-1 text-muted-foreground">{g.corto}</p>
      </PopoverContent>
    </Popover>
  );
}

/** Una línea de texto con su ⓘ y, si lleva, su enlace a la sesión, a Evolución o a un golpe. */
function Linea({ item, sesionId }: { item: Item; sesionId?: string | null }) {
  return (
    <>
      {item.titulo && <strong className="font-semibold">{item.titulo} </strong>}
      {item.texto}
      {item.ayuda && <Ayuda clave={item.ayuda} />}
      {item.enlace === "sesion" && sesionId && (
        <>
          {" "}
          <Link to="/sesion/$sesionId" params={{ sesionId }} className="inline-flex items-center gap-1 font-semibold text-state-ok hover:underline">
            Ver la sesión <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
          </Link>
        </>
      )}
      {item.enlace === "evolucion" && (
        <>
          {" "}
          <Link to="/evolucion" className="inline-flex items-center gap-1 font-semibold text-state-ok hover:underline">
            Ir a Evolución <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
          </Link>
        </>
      )}
      {item.golpeId && (
        <>
          {" "}
          <Link to="/reporte/$videoId" params={{ videoId: item.golpeId }} className="inline-flex items-center gap-1 font-semibold text-state-ok hover:underline">
            Ver ese golpe <ArrowRight className="h-3.5 w-3.5" aria-hidden="true" />
          </Link>
        </>
      )}
    </>
  );
}

export function EnUnaFrase({ texto }: { texto: string }) {
  return (
    <section aria-labelledby="una-frase" className="mt-10">
      <h2 id="una-frase" className={TITULO}>En una frase</h2>
      <p className="mt-3 rounded-2xl border border-border bg-card px-5 py-4 font-display text-xl font-bold leading-snug md:text-2xl">{texto}</p>
    </section>
  );
}

export function QueVimos({
  medido,
  noMedido,
  seAparta = [],
  sesionId,
}: {
  medido: Item[];
  noMedido: Item[];
  seAparta?: Item[];
  sesionId?: string | null;
}) {
  return (
    <section aria-labelledby="que-vimos" className="mt-12">
      <h2 id="que-vimos" className={TITULO}>Qué vimos</h2>
      {medido.length > 0 ? (
        <ul className="mt-4 space-y-3">
          {medido.map((m, i) => (
            <li key={i} className="rounded-2xl border border-border bg-card px-5 py-4 text-base leading-relaxed">
              <Linea item={m} sesionId={sesionId} />
            </li>
          ))}
        </ul>
      ) : (
        <p className="mt-4 rounded-2xl border border-dashed border-border px-5 py-4 text-sm text-muted-foreground">
          De este reporte no hay una medición con confianza suficiente para resumir.
        </p>
      )}
      {seAparta.length > 0 && (
        <ul className="mt-3 space-y-3">
          {seAparta.map((m, i) => (
            <li key={i} className="flex items-start gap-3 rounded-2xl border border-dashed border-border px-5 py-4 text-sm leading-relaxed">
              <Info className="mt-0.5 h-4 w-4 shrink-0 text-acento" aria-hidden="true" />
              <span>
                <Linea item={m} sesionId={sesionId} />
              </span>
            </li>
          ))}
        </ul>
      )}
      {noMedido.length > 0 && (
        <div className="mt-5">
          <h3 className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Lo que no se pudo medir</h3>
          <ul className="mt-2 space-y-2 text-sm leading-relaxed text-muted-foreground">
            {noMedido.map((m, i) => (
              <li key={i} className="border-l-2 border-dashed border-border pl-3">
                <Linea item={m} sesionId={sesionId} />
              </li>
            ))}
          </ul>
        </div>
      )}
    </section>
  );
}

function Subtitulo({ children }: { children: ReactNode }) {
  return <h3 className="mt-6 font-mono text-[10px] uppercase tracking-widest text-muted-foreground first:mt-0">{children}</h3>;
}

function ListaDeItems({ items, sesionId }: { items: Item[]; sesionId?: string | null }) {
  return (
    <ul className="mt-2 list-disc space-y-2 pl-5 text-sm leading-relaxed">
      {items.map((m, i) => (
        <li key={i}>
          <Linea item={m} sesionId={sesionId} />
        </li>
      ))}
    </ul>
  );
}

/** El recuadro de la literatura: aparte, con otro borde, sin ningún dato del jugador adentro. */
export function RecuadroLiteratura({ literatura }: { literatura: Literatura }) {
  return (
    <aside aria-label={literatura.titulo} className="mt-6 rounded-2xl border-2 border-dashed border-border bg-muted/30 px-5 py-4">
      <p className="flex items-center gap-2 font-mono text-[10px] uppercase tracking-widest text-muted-foreground">
        <BookOpen className="h-3.5 w-3.5" aria-hidden="true" /> {literatura.titulo}
      </p>
      <p className="mt-1 text-xs text-muted-foreground">{literatura.aclaracion}</p>
      <p className="mt-2 text-sm leading-relaxed">{literatura.texto}</p>
    </aside>
  );
}

export function QuePodesHacer({
  medir,
  usar,
  literatura,
  sesionId,
}: {
  medir: Item[];
  usar: Item[];
  literatura: Literatura;
  sesionId?: string | null;
}) {
  return (
    <section aria-labelledby="que-podes-hacer" className="mt-12">
      <h2 id="que-podes-hacer" className={TITULO}>Qué podés hacer con esto</h2>
      {medir.length > 0 && (
        <>
          <Subtitulo>Para medir mejor</Subtitulo>
          <ListaDeItems items={medir} sesionId={sesionId} />
        </>
      )}
      {usar.length > 0 && (
        <>
          <Subtitulo>Para usar estos datos al entrenar</Subtitulo>
          <ListaDeItems items={usar} sesionId={sesionId} />
        </>
      )}
      <RecuadroLiteratura literatura={literatura} />
    </section>
  );
}

export function ParaTuProfesional({ profesional }: { profesional: Profesional }) {
  return (
    <section aria-labelledby="para-tu-profesional" className="mt-12">
      <h2 id="para-tu-profesional" className={TITULO}>Para tu entrenador o profesional</h2>
      <Subtitulo>Preguntas para llevar</Subtitulo>
      <ol className="mt-2 list-decimal space-y-2 pl-5 text-sm leading-relaxed">
        {profesional.preguntas.map((p, i) => (
          <li key={i}>{p}</li>
        ))}
      </ol>
      <div className="mt-5">
        <BotonDescargarPdf />
      </div>
      <Subtitulo>Cuánto se puede confiar en cada medición</Subtitulo>
      <ul className="mt-2 list-disc space-y-2 pl-5 text-sm leading-relaxed">
        {profesional.confianza.map((c, i) => (
          <li key={i}>
            <Linea item={c} />
          </li>
        ))}
      </ul>
      <p role="note" className="mt-6 rounded-2xl border border-border bg-card px-5 py-4 text-sm leading-relaxed">
        {profesional.aviso}
      </p>
    </section>
  );
}

/** El detalle técnico, cerrado: los mismos datos, cada uno con su explicación en una línea. */
export function DetalleTecnico({ resumen = "Detalle técnico", children }: { resumen?: string; children: ReactNode }) {
  return (
    <details className="group mt-12 rounded-2xl border border-border bg-card print:hidden">
      <summary className="flex min-h-14 cursor-pointer list-none items-center justify-between px-5 font-display text-lg font-bold">
        {resumen}
        <ChevronDown className="h-5 w-5 transition-transform group-open:rotate-180" aria-hidden="true" />
      </summary>
      <div className="space-y-8 border-t border-border p-5">{children}</div>
    </details>
  );
}

export function GruposDeDetalle({ grupos }: { grupos: GrupoDetalle[] }) {
  return (
    <>
      {grupos.map((g) => (
        <div key={g.titulo}>
          <h3 className="font-mono text-xs uppercase tracking-widest text-muted-foreground">{g.titulo}</h3>
          <dl className="mt-3 divide-y divide-border text-sm">
            {g.filas.map((f) => (
              <div key={f.dato} className="grid gap-x-4 gap-y-1 py-2.5 md:grid-cols-[14rem_14rem_1fr]">
                <dt className="font-semibold">{f.dato}</dt>
                <dd className="font-mono">{f.valor}</dd>
                <dd className="text-muted-foreground">{f.significa}</dd>
              </div>
            ))}
          </dl>
        </div>
      ))}
    </>
  );
}

export function PieDeTextos() {
  return <p className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">Textos v{VERSION_TEXTOS}</p>;
}
