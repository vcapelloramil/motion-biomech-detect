import { useEffect, useState } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { AlertTriangle, CheckCircle2, Download, Loader2, Trash2 } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { useSesion } from "@/lib/sesion";
import { ROLES } from "@/lib/auth-errores";
import { MANOS, NIVELES } from "@/lib/carga";
import {
  CONFIRMACION_ELIMINAR,
  confirmacionValida,
  nombreArchivoExportacion,
  problemaDelJugador,
  problemaDelPerfil,
} from "@/lib/perfil";
import {
  eliminarMiCuenta,
  guardarJugador,
  guardarPerfil,
  leerActividad,
  leerJugadores,
  leerMisDatos,
  leerPerfil,
  type JugadorLeido,
  type PerfilLeido,
} from "@/lib/perfil-data";
import type { ActividadDelUsuario } from "@/lib/perfil";

export const Route = createFileRoute("/profile")({
  head: () => ({
    meta: [
      { title: "Mi perfil — KinetiQ" },
      { name: "description", content: "Tus datos, tus jugadores, descargar tus datos y eliminar tu cuenta." },
      { name: "robots", content: "noindex" },
    ],
  }),
  // Requiere sesión (especificación §3). La barrera real son RLS y la API.
  component: () => (
    <RutaProtegida>
      <PerfilPage />
    </RutaProtegida>
  ),
});

const CAMPO =
  "mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring";
const TARJETA = "rounded-3xl border border-border bg-card p-6 md:p-8";

function PerfilPage() {
  const { sesion, cargando, cerrarSesion } = useSesion();
  const [perfil, setPerfil] = useState<PerfilLeido | null | undefined>(undefined);
  const [jugadores, setJugadores] = useState<JugadorLeido[]>([]);
  const [errorLectura, setErrorLectura] = useState(false);
  const [actividad, setActividad] = useState<ActividadDelUsuario | null>(null);

  useEffect(() => {
    if (cargando) return;
    let activo = true;
    Promise.all([leerPerfil(), leerJugadores(), leerActividad().catch(() => null)])
      .then(([p, j, a]) => {
        if (!activo) return;
        setPerfil(p);
        setJugadores(j);
        setActividad(a);
      })
      .catch(() => {
        if (!activo) return;
        setErrorLectura(true);
        setPerfil(null);
      });
    return () => {
      activo = false;
    };
  }, [cargando]);

  if (perfil === undefined) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-16">
        <p role="status" className="flex items-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando tu perfil…
        </p>
      </main>
    );
  }
  if (perfil === null) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-16">
        <h1 className="font-display text-3xl font-bold">No pudimos leer tu perfil</h1>
        <p className="mt-3 text-muted-foreground">
          {errorLectura ? "Revisá tu conexión y recargá la página." : "Tu cuenta todavía no tiene un perfil."}
        </p>
      </main>
    );
  }

  const desde = new Date(perfil.creado_en).toLocaleDateString("es-AR", { month: "long", year: "numeric" });

  return (
    <main className="mx-auto max-w-3xl px-6 py-12 md:py-16">
      <div className="font-mono text-xs uppercase tracking-widest text-neon">/ Perfil</div>
      <h1 className="mt-3 font-display text-4xl font-extrabold md:text-5xl">Tu cuenta</h1>
      <p className="mt-2 text-muted-foreground">
        {perfil.email} · miembro desde {desde}
      </p>

      <div className="mt-10 space-y-8">
        <DatosPersonales perfil={perfil} alGuardar={setPerfil} />
        <Actividad actividad={actividad} />
        <Jugadores jugadores={jugadores} alCambiar={setJugadores} />
        <MisDatos />
        <Eliminar
          correo={perfil.email}
          accessToken={sesion?.access_token ?? null}
          alEliminada={async () => {
            try {
              await cerrarSesion();
            } catch {
              /* la cuenta ya no existe: si cerrar la sesión falla, la sesión local se limpia sola al vencer */
            }
          }}
        />
      </div>
    </main>
  );
}

function Actividad({ actividad }: { actividad: ActividadDelUsuario | null }) {
  const datos: { etiqueta: string; valor: number }[] = actividad
    ? [
        { etiqueta: "Sesiones", valor: actividad.sesiones },
        { etiqueta: "Golpes cargados", valor: actividad.golpes },
        { etiqueta: "Golpes medidos", valor: actividad.medidos },
      ]
    : [];
  return (
    <section aria-labelledby="actividad" className={TARJETA}>
      <h2 id="actividad" className="font-display text-xl font-bold">Tu actividad</h2>
      {!actividad ? (
        <p className="mt-2 text-sm text-muted-foreground">No pudimos leer tu actividad ahora.</p>
      ) : actividad.sesiones === 0 ? (
        <p className="mt-2 text-sm text-muted-foreground">
          Todavía no cargaste ninguna sesión. <Link to="/upload" className="underline underline-offset-4">Cargar golpes</Link>
        </p>
      ) : (
        <>
          <dl className="mt-4 grid grid-cols-3 gap-4">
            {datos.map((d) => (
              <div key={d.etiqueta} className="rounded-2xl border border-border p-4">
                <dd className="font-display text-3xl font-extrabold">{d.valor}</dd>
                <dt className="mt-1 text-xs text-muted-foreground">{d.etiqueta}</dt>
              </div>
            ))}
          </dl>
          {(actividad.no_medibles > 0 || actividad.en_analisis > 0) && (
            <p className="mt-3 text-xs text-muted-foreground">
              {actividad.no_medibles > 0 && `${actividad.no_medibles} no se pudieron medir. `}
              {actividad.en_analisis > 0 && `${actividad.en_analisis} siguen en análisis.`}
            </p>
          )}
        </>
      )}
    </section>
  );
}

function DatosPersonales({ perfil, alGuardar }: { perfil: PerfilLeido; alGuardar: (p: PerfilLeido) => void }) {
  const [nombre, setNombre] = useState(perfil.nombre);
  const [rol, setRol] = useState(perfil.rol);
  const [estado, setEstado] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);
  const [guardando, setGuardando] = useState(false);
  const cambio = nombre.trim() !== perfil.nombre || rol !== perfil.rol;

  async function guardar() {
    const problema = problemaDelPerfil(nombre, rol);
    if (problema) return setEstado({ tipo: "error", texto: problema });
    setGuardando(true);
    setEstado(null);
    try {
      await guardarPerfil(perfil.id, nombre, rol);
      alGuardar({ ...perfil, nombre: nombre.trim(), rol });
      setEstado({ tipo: "ok", texto: "Guardado." });
    } catch {
      setEstado({ tipo: "error", texto: "No pudimos guardar los cambios ahora. Probá de nuevo." });
    } finally {
      setGuardando(false);
    }
  }

  return (
    <section aria-labelledby="datos" className={TARJETA}>
      <h2 id="datos" className="font-display text-xl font-bold">Tus datos</h2>
      <div className="mt-5 grid gap-5 sm:grid-cols-2">
        <div>
          <label htmlFor="nombre" className="text-sm font-medium">Nombre</label>
          <input id="nombre" className={CAMPO} value={nombre} onChange={(e) => setNombre(e.target.value)} />
        </div>
        <div>
          <label htmlFor="rol" className="text-sm font-medium">¿Cómo usás KinetiQ?</label>
          <select id="rol" className={CAMPO} value={rol} onChange={(e) => setRol(e.target.value)} aria-describedby="ayuda-rol">
            {ROLES.map((r) => (
              <option key={r.valor} value={r.valor}>{r.etiqueta}</option>
            ))}
          </select>
          <p id="ayuda-rol" className="mt-1 text-xs text-muted-foreground">Hoy no cambia lo que ves en los reportes.</p>
        </div>
      </div>
      <div className="mt-5 flex flex-wrap items-center gap-4">
        <button
          type="button"
          disabled={!cambio || guardando}
          onClick={() => void guardar()}
          className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-gradient-neon px-5 text-sm font-semibold text-neon-foreground disabled:opacity-50"
        >
          {guardando && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />} Guardar
        </button>
        {estado && (
          <p role="status" className={"flex items-center gap-1.5 text-sm " + (estado.tipo === "error" ? "text-destructive" : "text-muted-foreground")}>
            {estado.tipo === "ok" ? <CheckCircle2 className="h-4 w-4" aria-hidden="true" /> : <AlertTriangle className="h-4 w-4" aria-hidden="true" />}
            {estado.texto}
          </p>
        )}
      </div>
    </section>
  );
}

function Jugadores({ jugadores, alCambiar }: { jugadores: JugadorLeido[]; alCambiar: (j: JugadorLeido[]) => void }) {
  return (
    <section aria-labelledby="jugadores" className={TARJETA}>
      <h2 id="jugadores" className="font-display text-xl font-bold">Jugadores</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Los jugadores que cargaste con tus sesiones. La mano dominante define qué brazo se analiza: si la cambiás, vale para los análisis nuevos;
        los reportes ya hechos no se recalculan.
      </p>
      {jugadores.length === 0 ? (
        <p className="mt-5 rounded-2xl border border-dashed border-border p-5 text-sm text-muted-foreground">
          Todavía no cargaste ningún jugador. Se crea al cargar la primera sesión.{" "}
          <Link to="/upload" className="underline underline-offset-4">Cargar golpes</Link>
        </p>
      ) : (
        <ul className="mt-5 space-y-4">
          {jugadores.map((j) => (
            <FilaJugador key={j.id} jugador={j} alGuardar={(n) => alCambiar(jugadores.map((x) => (x.id === n.id ? n : x)))} />
          ))}
        </ul>
      )}
    </section>
  );
}

function FilaJugador({ jugador, alGuardar }: { jugador: JugadorLeido; alGuardar: (j: JugadorLeido) => void }) {
  const [d, setD] = useState({ nombre: jugador.nombre, mano_dominante: jugador.mano_dominante, nivel: jugador.nivel });
  const [estado, setEstado] = useState<{ tipo: "ok" | "error"; texto: string } | null>(null);
  const [guardando, setGuardando] = useState(false);
  const cambio = d.nombre.trim() !== jugador.nombre || d.mano_dominante !== jugador.mano_dominante || d.nivel !== jugador.nivel;
  const id = jugador.id;

  async function guardar() {
    const problema = problemaDelJugador(d);
    if (problema) return setEstado({ tipo: "error", texto: problema });
    setGuardando(true);
    setEstado(null);
    try {
      await guardarJugador(id, d);
      alGuardar({ ...jugador, ...d, nombre: d.nombre.trim() });
      setEstado({ tipo: "ok", texto: "Guardado." });
    } catch {
      setEstado({ tipo: "error", texto: "No pudimos guardar los cambios ahora. Probá de nuevo." });
    } finally {
      setGuardando(false);
    }
  }

  return (
    <li className="rounded-2xl border border-border p-4">
      <div className="grid gap-4 sm:grid-cols-3">
        <div>
          <label htmlFor={`nombre-${id}`} className="text-sm font-medium">Nombre</label>
          <input id={`nombre-${id}`} className={CAMPO} value={d.nombre} onChange={(e) => setD({ ...d, nombre: e.target.value })} />
        </div>
        <div>
          <label htmlFor={`mano-${id}`} className="text-sm font-medium">Mano dominante</label>
          <select id={`mano-${id}`} className={CAMPO} value={d.mano_dominante} onChange={(e) => setD({ ...d, mano_dominante: e.target.value })}>
            {MANOS.map((m) => (
              <option key={m.valor} value={m.valor}>{m.etiqueta}</option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor={`nivel-${id}`} className="text-sm font-medium">Nivel</label>
          <select id={`nivel-${id}`} className={CAMPO} value={d.nivel} onChange={(e) => setD({ ...d, nivel: e.target.value })}>
            {NIVELES.map((n) => (
              <option key={n.valor} value={n.valor}>{n.etiqueta}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="mt-4 flex flex-wrap items-center gap-4">
        <button
          type="button"
          disabled={!cambio || guardando}
          onClick={() => void guardar()}
          className="inline-flex min-h-10 items-center gap-2 rounded-lg border border-border px-4 text-sm font-semibold hover:border-neon/50 disabled:opacity-50"
        >
          {guardando && <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />} Guardar
        </button>
        {estado && (
          <p role="status" className={"text-sm " + (estado.tipo === "error" ? "text-destructive" : "text-muted-foreground")}>{estado.texto}</p>
        )}
      </div>
    </li>
  );
}

function MisDatos() {
  const [trabajando, setTrabajando] = useState(false);
  const [error, setError] = useState(false);

  async function descargar() {
    setTrabajando(true);
    setError(false);
    try {
      const datos = await leerMisDatos();
      const blob = new Blob([JSON.stringify(datos, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = nombreArchivoExportacion(datos.generado_en);
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError(true);
    } finally {
      setTrabajando(false);
    }
  }

  return (
    <section aria-labelledby="mis-datos" className={TARJETA}>
      <h2 id="mis-datos" className="font-display text-xl font-bold">Una copia de tus datos</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Descargá una copia de lo que KinetiQ guarda de vos: tu cuenta, tus jugadores y tus sesiones con el reporte de cada golpe, en un archivo JSON.
        No incluye los archivos de video ni las imágenes.
      </p>
      <button
        type="button"
        disabled={trabajando}
        onClick={() => void descargar()}
        className="mt-5 inline-flex min-h-11 items-center gap-2 rounded-xl border border-border px-5 text-sm font-semibold hover:border-neon/50 disabled:opacity-60"
      >
        {trabajando ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Download className="h-4 w-4" aria-hidden="true" />}
        Descargar mis datos
      </button>
      {error && <p role="alert" className="mt-3 text-sm text-destructive">No pudimos armar la descarga ahora. Probá de nuevo.</p>}
    </section>
  );
}

function Eliminar({
  correo,
  accessToken,
  alEliminada,
}: {
  correo: string;
  accessToken: string | null;
  alEliminada: () => Promise<void>;
}) {
  const navegar = useNavigate();
  const [abierto, setAbierto] = useState(false);
  const [texto, setTexto] = useState("");
  const [trabajando, setTrabajando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hecho, setHecho] = useState(false);

  async function eliminar() {
    if (!accessToken) return setError("Tu sesión venció. Ingresá de nuevo y volvé a intentar.");
    setTrabajando(true);
    setError(null);
    const r = await eliminarMiCuenta(accessToken);
    if (r.ok) {
      setHecho(true);
      await alEliminada();
      return;
    }
    setError(r.texto);
    setTrabajando(false);
  }

  if (hecho) {
    return (
      <section aria-labelledby="eliminada" className={TARJETA}>
        <CheckCircle2 className="h-8 w-8 text-neon" aria-hidden="true" />
        <h2 id="eliminada" className="mt-3 font-display text-xl font-bold">Tu cuenta y tus datos se eliminaron</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Se borraron tu cuenta, tus jugadores, tus sesiones, tus reportes y los archivos de video e imágenes. Cerramos tu sesión.
        </p>
        <button
          type="button"
          onClick={() => void navegar({ to: "/" })}
          className="mt-5 inline-flex min-h-11 items-center rounded-xl border border-border px-5 text-sm font-semibold"
        >
          Ir al inicio
        </button>
      </section>
    );
  }

  return (
    <section aria-labelledby="eliminar" className={TARJETA + " border-destructive/40"}>
      <h2 id="eliminar" className="font-display text-xl font-bold">Eliminar mi cuenta</h2>
      <p className="mt-2 text-sm text-muted-foreground">
        Se borran tu cuenta ({correo}), tus jugadores, tus sesiones, los reportes y los archivos de video e imágenes de todos tus golpes.{" "}
        <strong className="text-foreground">No se puede deshacer.</strong> Si querés conservar algo, descargá tus datos antes.
      </p>
      {!abierto ? (
        <button
          type="button"
          onClick={() => setAbierto(true)}
          className="mt-5 inline-flex min-h-11 items-center gap-2 rounded-xl border border-destructive/60 px-5 text-sm font-semibold text-destructive"
        >
          <Trash2 className="h-4 w-4" aria-hidden="true" /> Eliminar mi cuenta y mis datos
        </button>
      ) : (
        <div role="alert" className="mt-5 rounded-2xl border border-destructive/50 p-4">
          <label htmlFor="confirmar" className="text-sm font-medium">
            Para confirmar, escribí <span className="font-mono">{CONFIRMACION_ELIMINAR}</span>
          </label>
          <input
            id="confirmar"
            className={CAMPO}
            value={texto}
            autoComplete="off"
            onChange={(e) => setTexto(e.target.value)}
            disabled={trabajando}
          />
          {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
          <div className="mt-4 flex flex-wrap gap-3">
            <button
              type="button"
              disabled={!confirmacionValida(texto) || trabajando}
              onClick={() => void eliminar()}
              className="inline-flex min-h-11 items-center gap-2 rounded-xl bg-destructive px-5 text-sm font-semibold text-white disabled:opacity-50"
            >
              {trabajando ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : <Trash2 className="h-4 w-4" aria-hidden="true" />}
              {trabajando ? "Eliminando…" : "Eliminar para siempre"}
            </button>
            <button
              type="button"
              disabled={trabajando}
              onClick={() => {
                setAbierto(false);
                setTexto("");
                setError(null);
              }}
              className="inline-flex min-h-11 items-center rounded-xl border border-border px-5 text-sm font-semibold"
            >
              Cancelar
            </button>
          </div>
        </div>
      )}
    </section>
  );
}
