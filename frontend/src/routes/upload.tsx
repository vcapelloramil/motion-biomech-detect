import { useEffect, useRef, useState, type FormEvent } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { AlertTriangle, CheckCircle2, Info, Loader2, UploadCloud } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { useSesion } from "@/lib/sesion";
import {
  ENCUADRES,
  GESTOS,
  LADOS_CAMARA,
  MANOS,
  MODOS_CAPTURA,
  NIVELES,
  DURACION_AVISO_S,
  type Mano,
  type Nivel,
  esValor,
  problemaDelArchivo,
  rutaDelVideo,
  tipoDeContenido,
} from "@/lib/carga";
import {
  crearAtleta,
  crearSesion,
  crearVideo,
  descartarCarga,
  listarAtletas,
  pedirAnalisis,
  subirVideo,
  type Atleta,
} from "@/lib/cargar-video";

export const Route = createFileRoute("/upload")({
  head: () => ({
    meta: [
      { title: "Cargar video — KinetiQ" },
      {
        name: "description",
        content: "Subí el video de un golpe y obtené el orden en que la cadera, el tronco y el brazo alcanzan su velocidad máxima.",
      },
    ],
  }),
  // Requiere sesión (especificación §3). La barrera real son RLS y la API.
  component: () => (
    <RutaProtegida>
      <CargarPage />
    </RutaProtegida>
  ),
});

const CAMPO =
  "mt-1 w-full rounded-md border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-2 focus-visible:ring-ring";

function hoy(): string {
  const d = new Date();
  const dos = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${dos(d.getMonth() + 1)}-${dos(d.getDate())}`;
}

type Fase = "formulario" | "enviando" | "listo";
type Fallo = { texto: string; reenviar: boolean } | null;

function CargarPage() {
  const { sesion } = useSesion();
  const navegar = useNavigate();
  const usuarioId = sesion?.user.id ?? "";

  const [atletas, setAtletas] = useState<Atleta[] | null>(null);
  const [errorAtletas, setErrorAtletas] = useState(false);
  const [atletaId, setAtletaId] = useState<string>("");
  const [nombreAtleta, setNombreAtleta] = useState("");
  const [mano, setMano] = useState("");
  const [nivel, setNivel] = useState("");

  const [gesto, setGesto] = useState("");
  const [encuadre, setEncuadre] = useState("");
  const [lado, setLado] = useState("");
  const [modo, setModo] = useState("");
  const [fecha, setFecha] = useState(hoy());

  const [archivo, setArchivo] = useState<File | null>(null);
  const [problema, setProblema] = useState<string | null>(null);
  const [duracion, setDuracion] = useState<number | null>(null);

  const [fase, setFase] = useState<Fase>("formulario");
  const [paso, setPaso] = useState("");
  const [progreso, setProgreso] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [fallo, setFallo] = useState<Fallo>(null);
  // Lo ya hecho cuando falla solo el envío: el video está guardado y se reintenta únicamente la orden de analizar.
  const guardado = useRef<{ videoId: string } | null>(null);

  useEffect(() => {
    let activo = true;
    listarAtletas()
      .then((lista) => {
        if (!activo) return;
        setAtletas(lista);
        setAtletaId(lista.length > 0 ? lista[0].id : "nuevo");
      })
      .catch(() => {
        if (!activo) return;
        setErrorAtletas(true);
        setAtletas([]);
        setAtletaId("nuevo");
      });
    return () => {
      activo = false;
    };
  }, []);

  function elegirArchivo(f: File | null) {
    setArchivo(null);
    setProblema(null);
    setDuracion(null);
    if (!f) return;
    const p = problemaDelArchivo(f);
    if (p) return setProblema(p.texto);
    setArchivo(f);
    // La duración solo avisa (un golpe dura pocos segundos). Si el navegador no puede leerla, se omite.
    const url = URL.createObjectURL(f);
    const v = document.createElement("video");
    v.preload = "metadata";
    v.onloadedmetadata = () => {
      if (Number.isFinite(v.duration)) setDuracion(v.duration);
      URL.revokeObjectURL(url);
    };
    v.onerror = () => URL.revokeObjectURL(url);
    v.src = url;
  }

  async function enviarAnalisis(videoId: string) {
    setPaso("Enviando a analizar…");
    const token = sesion?.access_token;
    if (!token) {
      setFallo({ texto: "Tu sesión venció. Ingresá de nuevo y volvé a intentar.", reenviar: false });
      return setFase("formulario");
    }
    const r = await pedirAnalisis(videoId, token);
    if (r.ok) {
      guardado.current = null;
      // El análisis ya está en cola: se sigue desde la pantalla Procesando.
      void navegar({ to: "/procesando/$videoId", params: { videoId } });
      return setFase("listo");
    }
    setFallo({ texto: r.texto, reenviar: r.reintentable });
    setFase("formulario");
  }

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setFallo(null);

    if (!usuarioId || !sesion) return setError("Tu sesión venció. Ingresá de nuevo.");
    const creaAtleta = atletaId === "nuevo";
    if (creaAtleta) {
      if (!nombreAtleta.trim()) return setError("Escribí el nombre del jugador.");
      if (!esValor(MANOS, mano)) return setError("Elegí la mano dominante del jugador.");
      if (!esValor(NIVELES, nivel)) return setError("Elegí el nivel del jugador.");
    }
    if (!esValor(GESTOS, gesto)) return setError("Elegí el golpe.");
    if (!esValor(ENCUADRES, encuadre)) return setError("Elegí el encuadre de la cámara.");
    if (!esValor(LADOS_CAMARA, lado)) return setError("Elegí de qué lado del jugador estaba la cámara.");
    if (!esValor(MODOS_CAPTURA, modo)) return setError("Elegí cómo grabaste el video.");
    if (!fecha) return setError("Elegí la fecha de la grabación.");
    if (!archivo) return setError("Elegí el video del golpe.");
    const tipo = tipoDeContenido(archivo.name, archivo.type);
    if (!tipo) return setError("Subí un video MP4 o MOV.");

    setFase("enviando");
    setProgreso(0);
    let sesionId: string | null = null;
    let ruta: string | null = null;
    try {
      let idAtleta = atletaId;
      if (creaAtleta) {
        setPaso("Guardando al jugador…");
        const nuevo = await crearAtleta(usuarioId, { nombre: nombreAtleta.trim(), mano_dominante: mano as Mano, nivel: nivel as Nivel });
        idAtleta = nuevo.id;
        setAtletas((prev) => [...(prev ?? []), nuevo]);
        setAtletaId(nuevo.id);
      }
      setPaso("Creando la sesión…");
      sesionId = await crearSesion(usuarioId, {
        atleta_id: idAtleta,
        gesto,
        encuadre,
        lado_camara: lado,
        modo_captura: modo,
        fecha,
      });

      const videoId = crypto.randomUUID();
      ruta = rutaDelVideo(usuarioId, videoId, archivo.name);
      setPaso("Subiendo el video…");
      await subirVideo({ ruta, archivo, tipo, accessToken: sesion.access_token, alProgresar: setProgreso });

      setPaso("Registrando el video…");
      await crearVideo({ id: videoId, sesion_id: sesionId, usuario_id: usuarioId, ruta_almacenamiento: ruta });
      guardado.current = { videoId };
    } catch (err) {
      await descartarCarga(sesionId, ruta);
      const estado = (err as { estado?: number }).estado;
      setFallo({
        texto:
          estado === 413
            ? "El archivo es demasiado grande (máximo 50 MB). Recortalo y volvé a elegirlo."
            : estado === 401 || estado === 403
              ? "Tu sesión venció. Ingresá de nuevo y volvé a intentar."
              : "No pudimos guardar el video. Revisá tu conexión y volvé a probar.",
        reenviar: false,
      });
      return setFase("formulario");
    }
    await enviarAnalisis(guardado.current!.videoId);
  }

  function otraCarga() {
    setFase("formulario");
    setArchivo(null);
    setDuracion(null);
    setProgreso(0);
    setFallo(null);
    guardado.current = null;
  }

  if (fase === "listo") {
    return (
      <main className="mx-auto max-w-xl px-6 py-16">
        <div className="rounded-xl border border-border bg-card p-6">
          <CheckCircle2 className="h-8 w-8 text-neon" aria-hidden="true" />
          <h1 className="mt-4 font-display text-2xl font-bold">Tu video se está analizando</h1>
          <p className="mt-3 text-sm text-muted-foreground">
            Puede tardar varios minutos. <strong className="text-foreground">Podés cerrar esta página:</strong> el análisis sigue
            en el servidor y el resultado va a estar en tus sesiones.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button type="button" onClick={otraCarga} className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:border-neon/50">
              Cargar otro video
            </button>
            <button type="button" onClick={() => navegar({ to: "/videos" })} className="rounded-md px-4 py-2 text-sm text-muted-foreground underline underline-offset-4 hover:text-foreground">
              Ver mis sesiones
            </button>
          </div>
        </div>
      </main>
    );
  }

  const enCurso = fase === "enviando";
  const listaAtletas = atletas ?? [];

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="font-display text-3xl font-bold">Cargar un golpe</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Un video es un golpe. El sistema documenta el orden en que la cadera, el tronco y el brazo alcanzan su velocidad máxima.
      </p>

      {/* La instrucción va ANTES de elegir el archivo (decisiones 029 y 030): si el teléfono convierte el video, no hay arreglo posterior. */}
      <section aria-labelledby="como-subir" className="mt-8 rounded-xl border border-neon/40 bg-neon/5 p-5">
        <h2 id="como-subir" className="flex items-center gap-2 font-display text-base font-semibold">
          <Info className="h-4 w-4 text-neon" aria-hidden="true" />
          Antes de elegir el archivo (iPhone)
        </h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm">
          <li>
            En el selector de Fotos tocá <strong>Opciones</strong> (abajo a la izquierda) y activá <strong>Formato: Actual</strong>.
          </li>
          <li>
            O guardá el video en la app <strong>Archivos</strong> y elegilo desde ahí.
          </li>
        </ol>
        <p className="mt-3 text-sm text-muted-foreground">
          Con el formato por defecto el teléfono convierte el video al subirlo y descarta fotogramas: queda por debajo de los
          120 fps que hacen falta y no se puede analizar. Un video sin recortar de más de 50 MB tampoco entra: dejá solo el golpe
          (unos 2 a 5 segundos).
        </p>
      </section>

      <form onSubmit={enviar} className="mt-8 space-y-8" noValidate>
        <fieldset disabled={enCurso} className="space-y-5">
          <legend className="font-display text-lg font-semibold">Jugador</legend>
          {atletas === null ? (
            <p className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> Cargando…
            </p>
          ) : (
            <>
              {errorAtletas && (
                <p className="text-sm text-muted-foreground">No pudimos leer tus jugadores guardados. Podés cargar uno nuevo.</p>
              )}
              {listaAtletas.length > 0 && (
                <div>
                  <label htmlFor="atleta" className="text-sm font-medium">¿Quién es?</label>
                  <select id="atleta" className={CAMPO} value={atletaId} onChange={(e) => setAtletaId(e.target.value)}>
                    {listaAtletas.map((a) => (
                      <option key={a.id} value={a.id}>{a.nombre}</option>
                    ))}
                    <option value="nuevo">Otro jugador…</option>
                  </select>
                </div>
              )}
              {atletaId === "nuevo" && (
                <div className="grid gap-5 sm:grid-cols-3">
                  <div className="sm:col-span-3">
                    <label htmlFor="nombre-atleta" className="text-sm font-medium">Nombre del jugador</label>
                    <input id="nombre-atleta" className={CAMPO} value={nombreAtleta} onChange={(e) => setNombreAtleta(e.target.value)} />
                  </div>
                  <div className="sm:col-span-3 grid gap-5 sm:grid-cols-2">
                    <div>
                      <label htmlFor="mano" className="text-sm font-medium">Mano dominante</label>
                      <select id="mano" className={CAMPO} value={mano} onChange={(e) => setMano(e.target.value)}>
                        <option value="" disabled>Elegí una opción</option>
                        {MANOS.map((m) => <option key={m.valor} value={m.valor}>{m.etiqueta}</option>)}
                      </select>
                    </div>
                    <div>
                      <label htmlFor="nivel" className="text-sm font-medium">Nivel</label>
                      <select id="nivel" className={CAMPO} value={nivel} onChange={(e) => setNivel(e.target.value)}>
                        <option value="" disabled>Elegí una opción</option>
                        {NIVELES.map((n) => <option key={n.valor} value={n.valor}>{n.etiqueta}</option>)}
                      </select>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </fieldset>

        <fieldset disabled={enCurso} className="space-y-5">
          <legend className="font-display text-lg font-semibold">El golpe</legend>
          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <label htmlFor="gesto" className="text-sm font-medium">Golpe</label>
              <select id="gesto" className={CAMPO} value={gesto} onChange={(e) => setGesto(e.target.value)}>
                <option value="" disabled>Elegí una opción</option>
                {GESTOS.map((g) => <option key={g.valor} value={g.valor}>{g.etiqueta}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="fecha" className="text-sm font-medium">Fecha de la grabación</label>
              <input id="fecha" type="date" className={CAMPO} value={fecha} max={hoy()} onChange={(e) => setFecha(e.target.value)} />
            </div>
            <div>
              <label htmlFor="encuadre" className="text-sm font-medium">Encuadre de la cámara</label>
              <select id="encuadre" className={CAMPO} value={encuadre} onChange={(e) => setEncuadre(e.target.value)}>
                <option value="" disabled>Elegí una opción</option>
                {ENCUADRES.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}
              </select>
            </div>
            <div>
              <label htmlFor="lado" className="text-sm font-medium">Lado de la cámara</label>
              <select id="lado" className={CAMPO} value={lado} onChange={(e) => setLado(e.target.value)}>
                <option value="" disabled>Elegí una opción</option>
                {LADOS_CAMARA.map((x) => <option key={x.valor} value={x.valor}>{x.etiqueta}</option>)}
              </select>
            </div>
          </div>

          <div>
            <label htmlFor="modo" className="text-sm font-medium">¿Cómo lo grabaste?</label>
            <select id="modo" className={CAMPO} value={modo} onChange={(e) => setModo(e.target.value)} aria-describedby="ayuda-modo">
              <option value="" disabled>Elegí una opción</option>
              {MODOS_CAPTURA.map((m) => <option key={m.valor} value={m.valor}>{m.etiqueta}</option>)}
            </select>
            <p id="ayuda-modo" className="mt-1 text-xs text-muted-foreground">
              Elegí cómo grabaste, no cómo se ve el video. En el iPhone es el modo que elegiste en la app Cámara antes de grabar:
              no se puede saber mirando el archivo.
            </p>
          </div>

          {modo === "normal" && (
            <p role="note" className="flex items-start gap-2 rounded-md border border-border px-3 py-2 text-sm">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-state-warn" aria-hidden="true" />
              <span>
                <strong>¿Lo grabaste en cámara lenta?</strong> Un video en modo normal suele tener 30 o 60 fps: solo se va a poder
                analizar la fase de preparación (hacen falta 120 fps o más). Si usaste cámara lenta,{" "}
                <button type="button" onClick={() => setModo("")} className="underline underline-offset-4">
                  cambiá la respuesta
                </button>
                .
              </span>
            </p>
          )}
        </fieldset>

        <fieldset disabled={enCurso} className="space-y-3">
          <legend className="font-display text-lg font-semibold">El video</legend>
          <label
            htmlFor="archivo"
            className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-dashed border-border px-4 py-8 text-center hover:border-neon/50"
          >
            <UploadCloud className="h-7 w-7 text-neon" aria-hidden="true" />
            <span className="text-sm font-medium">{archivo ? archivo.name : "Elegir el video (MP4 o MOV, hasta 50 MB)"}</span>
            {archivo && (
              <span className="text-xs text-muted-foreground">
                {(archivo.size / (1024 * 1024)).toFixed(1)} MB{duracion !== null ? ` · ${duracion.toFixed(1)} s` : ""}
              </span>
            )}
          </label>
          <input
            id="archivo"
            type="file"
            accept="video/mp4,video/quicktime,.mp4,.mov"
            className="sr-only"
            onChange={(e) => elegirArchivo(e.target.files?.[0] ?? null)}
          />
          {problema && (
            <p role="alert" className="flex items-start gap-2 text-sm text-destructive">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              {problema}
            </p>
          )}
          {duracion !== null && duracion > DURACION_AVISO_S && (
            <p role="note" className="flex items-start gap-2 text-sm text-muted-foreground">
              <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              Este video dura {duracion.toFixed(0)} s: probablemente tenga varios golpes. El sistema analiza un golpe por video;
              conviene recortarlo para dejar solo uno.
            </p>
          )}
        </fieldset>

        {error && (
          <p role="alert" className="flex items-start gap-2 rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            {error}
          </p>
        )}

        {fallo && (
          <div role="alert" className="rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
            <p className="flex items-start gap-2">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              {fallo.texto}
            </p>
            {fallo.reenviar && guardado.current && (
              <button
                type="button"
                onClick={() => {
                  setFallo(null);
                  setFase("enviando");
                  void enviarAnalisis(guardado.current!.videoId);
                }}
                className="mt-2 text-foreground underline underline-offset-4"
              >
                Enviar a analizar de nuevo
              </button>
            )}
            {!sesion && (
              <Link to="/ingreso" className="mt-2 inline-block text-foreground underline underline-offset-4">Ingresar</Link>
            )}
          </div>
        )}

        {enCurso ? (
          <div role="status" aria-live="polite" className="rounded-xl border border-border bg-card p-4">
            <p className="flex items-center gap-2 text-sm font-medium">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              {paso}
              {paso.startsWith("Subiendo") && <span className="font-mono text-muted-foreground">{Math.round(progreso * 100)} %</span>}
            </p>
            {paso.startsWith("Subiendo") && (
              <progress className="mt-3 h-2 w-full" value={progreso} max={1} aria-label="Progreso de la subida" />
            )}
          </div>
        ) : (
          <button
            type="submit"
            className="flex w-full items-center justify-center gap-2 rounded-md bg-gradient-neon px-4 py-2.5 text-sm font-semibold text-neon-foreground shadow-neon"
          >
            Subir y analizar
          </button>
        )}
      </form>
    </main>
  );
}
