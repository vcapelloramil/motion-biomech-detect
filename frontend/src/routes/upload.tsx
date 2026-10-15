import { useEffect, useRef, useState, type DragEvent, type FormEvent } from "react";
import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { AlertTriangle, CheckCircle2, CircleDashed, Film, Info, Loader2, UploadCloud, X } from "lucide-react";
import { RutaProtegida } from "@/components/ruta-protegida";
import { EsquemaEncuadre } from "@/components/esquema-encuadre";
import { esLadoDeLaMano, ladoRecomendado, type LadoCamara as LadoEsquema } from "@/lib/esquema-encuadre";
import { useSesion } from "@/lib/sesion";
import {
  ENCUADRES,
  GESTOS,
  LADOS_CAMARA,
  MANOS,
  MAX_GOLPES,
  MODOS_CAPTURA,
  NIVELES,
  DURACION_AVISO_S,
  type EstadoArchivoCarga,
  type Mano,
  type Nivel,
  claveDeArchivo,
  cuantosCaben,
  esValor,
  problemaDelArchivo,
  resumenDeCarga,
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
import { fmt } from "@/lib/formato";

export const Route = createFileRoute("/upload")({
  head: () => ({
    meta: [
      { title: "Cargar golpes — KinetiQ" },
      {
        name: "description",
        content: "Subí los videos de tus golpes y obtené el orden en que la cadera, el tronco y el brazo alcanzan su velocidad máxima.",
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

/** Un video elegido. Cada video es un golpe de la misma sesión. */
type Item = {
  clave: string;
  archivo: File;
  duracion: number | null;
  /** Por qué no se va a subir (formato, tamaño); `null` si se sube. */
  problema: string | null;
  estado: EstadoArchivoCarga;
  progreso: number;
  /** Ya guardado en Storage y en la base: si falla el envío a analizar, se reintenta solo eso. */
  videoId: string | null;
  error: string | null;
};

const ETIQUETA_ESTADO: Record<EstadoArchivoCarga, string> = {
  pendiente: "Listo para subir",
  subiendo: "Subiendo",
  enviando: "Enviando a analizar",
  enviado: "En análisis",
  error: "No se pudo",
};

const DESCRIPCION_ENCUADRE: Record<string, string> = {
  perfil: "La cámara está a un costado del jugador, a 90° de la dirección del golpe: se ve su lado completo.",
  tres_cuartos: "La cámara está por delante del jugador, en diagonal, a unos 45° de la dirección del golpe: lo ves un poco de frente.",
};

function textoDeError(err: unknown): string {
  const estado = (err as { estado?: number }).estado;
  if (estado === 413) return "El archivo es demasiado grande (máximo 50 MB). Recortalo y volvé a elegirlo.";
  if (estado === 401 || estado === 403) return "Tu sesión venció. Ingresá de nuevo y volvé a intentar.";
  return "No pudimos guardar el video. Revisá tu conexión y volvé a probar.";
}

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

  const [items, setItems] = useState<Item[]>([]);
  const [aviso, setAviso] = useState<string | null>(null);

  const [fase, setFase] = useState<Fase>("formulario");
  const [paso, setPaso] = useState("");
  const [error, setError] = useState<string | null>(null);
  // La sesión ya creada: un reintento agrega los golpes que faltaron a la MISMA sesión y los datos quedan fijos.
  const sesionRef = useRef<string | null>(null);
  const [sesionCreada, setSesionCreada] = useState(false);

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

  function cambiar(clave: string, parche: Partial<Item>) {
    setItems((prev) => prev.map((it) => (it.clave === clave ? { ...it, ...parche } : it)));
  }

  function agregarArchivos(lista: FileList | File[] | null) {
    if (!lista) return;
    setAviso(null);
    setError(null);
    const existentes = new Set(items.map((p) => p.clave));
    const distintos = Array.from(lista).filter((f) => !existentes.has(claveDeArchivo(f)));
    const { aceptados, descartados } = cuantosCaben(items.length, distintos.length);
    if (descartados > 0) setAviso(`Una sesión admite hasta ${MAX_GOLPES} golpes: quedaron afuera ${descartados}.`);
    const agregados: Item[] = distintos.slice(0, aceptados).map((f) => ({
      clave: claveDeArchivo(f),
      archivo: f,
      duracion: null,
      problema: problemaDelArchivo(f)?.texto ?? null,
      estado: "pendiente",
      progreso: 0,
      videoId: null,
      error: null,
    }));
    setItems((prev) => [...prev, ...agregados]);
    for (const it of agregados) if (!it.problema) leerDuracion(it);
  }

  /** La duración solo avisa (un golpe dura pocos segundos). Si el navegador no puede leerla, se omite. */
  function leerDuracion(it: Item) {
    const url = URL.createObjectURL(it.archivo);
    const v = document.createElement("video");
    v.preload = "metadata";
    v.onloadedmetadata = () => {
      if (Number.isFinite(v.duration)) cambiar(it.clave, { duracion: v.duration });
      URL.revokeObjectURL(url);
    };
    v.onerror = () => URL.revokeObjectURL(url);
    v.src = url;
  }

  function quitar(clave: string) {
    setItems((prev) => prev.filter((it) => it.clave !== clave));
  }

  function alSoltar(e: DragEvent<HTMLLabelElement>) {
    e.preventDefault();
    agregarArchivos(e.dataTransfer.files);
  }

  async function enviar(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setAviso(null);

    if (!usuarioId || !sesion) return setError("Tu sesión venció. Ingresá de nuevo.");
    const creaAtleta = atletaId === "nuevo";
    if (!sesionRef.current) {
      if (creaAtleta) {
        if (!nombreAtleta.trim()) return setError("Escribí el nombre del jugador.");
        if (!esValor(MANOS, mano)) return setError("Elegí la mano dominante del jugador.");
        if (!esValor(NIVELES, nivel)) return setError("Elegí el nivel del jugador.");
      }
      if (!esValor(GESTOS, gesto)) return setError("Elegí el golpe.");
      if (!esValor(ENCUADRES, encuadre)) return setError("Elegí el encuadre de la cámara.");
      if (!esValor(LADOS_CAMARA, lado)) return setError("Elegí de qué lado del jugador estaba la cámara.");
      if (!esValor(MODOS_CAPTURA, modo)) return setError("Elegí cómo grabaste los videos.");
      if (!fecha) return setError("Elegí la fecha de la grabación.");
    }
    const aSubir = items.filter((it) => !it.problema && it.estado !== "enviado");
    if (aSubir.length === 0) return setError("Elegí al menos un video de un golpe.");
    for (const it of aSubir) {
      if (!tipoDeContenido(it.archivo.name, it.archivo.type)) return setError("Subí videos MP4 o MOV.");
    }

    setFase("enviando");
    let sesionNueva: string | null = null;
    let guardados = 0;
    try {
      if (!sesionRef.current) {
        let idAtleta = atletaId;
        if (creaAtleta) {
          setPaso("Guardando al jugador…");
          const nuevo = await crearAtleta(usuarioId, { nombre: nombreAtleta.trim(), mano_dominante: mano as Mano, nivel: nivel as Nivel });
          idAtleta = nuevo.id;
          setAtletas((prev) => [...(prev ?? []), nuevo]);
          setAtletaId(nuevo.id);
        }
        setPaso("Creando la sesión…");
        sesionNueva = await crearSesion(usuarioId, {
          atleta_id: idAtleta,
          gesto,
          encuadre,
          lado_camara: lado,
          modo_captura: modo,
          fecha,
        } as Parameters<typeof crearSesion>[1]);
        sesionRef.current = sesionNueva;
        setSesionCreada(true);
      }
    } catch {
      setFase("formulario");
      return setError("No pudimos crear la sesión. Revisá tu conexión y volvé a probar.");
    }
    const sesionId = sesionRef.current as string;

    // Un golpe por vez: se sube, se registra y se manda a analizar. El servidor los procesa de a uno, en cola.
    const resultado = new Map<string, EstadoArchivoCarga>();
    const idsEnviados: string[] = [];
    for (const [i, it] of aSubir.entries()) {
      setPaso(`Golpe ${i + 1} de ${aSubir.length}`);
      let videoId = it.videoId;
      if (!videoId) {
        const nuevoId = crypto.randomUUID();
        const ruta = rutaDelVideo(usuarioId, nuevoId, it.archivo.name);
        const tipo = tipoDeContenido(it.archivo.name, it.archivo.type) as string;
        cambiar(it.clave, { estado: "subiendo", progreso: 0, error: null });
        try {
          await subirVideo({
            ruta,
            archivo: it.archivo,
            tipo,
            accessToken: sesion.access_token,
            alProgresar: (f) => cambiar(it.clave, { progreso: f }),
          });
          await crearVideo({ id: nuevoId, sesion_id: sesionId, usuario_id: usuarioId, ruta_almacenamiento: ruta });
        } catch (err) {
          await descartarCarga(null, ruta);
          cambiar(it.clave, { estado: "error", error: textoDeError(err) });
          resultado.set(it.clave, "error");
          continue;
        }
        videoId = nuevoId;
        guardados += 1;
        cambiar(it.clave, { videoId });
      }
      cambiar(it.clave, { estado: "enviando", progreso: 1 });
      const r = await pedirAnalisis(videoId, sesion.access_token);
      if (r.ok) {
        cambiar(it.clave, { estado: "enviado" });
        resultado.set(it.clave, "enviado");
        idsEnviados.push(videoId);
      } else {
        cambiar(it.clave, { estado: "error", error: r.texto });
        resultado.set(it.clave, "error");
      }
    }

    // Si no se guardó ningún golpe, la sesión recién creada no tiene nada: se descarta para no dejarla vacía.
    if (sesionNueva && guardados === 0) {
      await descartarCarga(sesionNueva, null);
      sesionRef.current = null;
      setSesionCreada(false);
    }

    const estados = [...resultado.values()];
    const resumen = resumenDeCarga(estados);
    if (resumen.completo) {
      // Un solo golpe en toda la sesión: se sigue directo desde su pantalla de progreso (como antes de cargar varios).
      const yaEnviados = items.filter((it) => it.estado === "enviado").length;
      if (yaEnviados + idsEnviados.length === 1 && idsEnviados.length === 1) {
        void navegar({ to: "/procesando/$videoId", params: { videoId: idsEnviados[0] } });
      }
      return setFase("listo");
    }
    setFase("formulario");
    setError(
      resumen.con_error > 0
        ? `${resumen.con_error === 1 ? "1 golpe no se pudo" : `${resumen.con_error} golpes no se pudieron`} enviar. Los demás ya están en análisis: podés reintentar solo los que fallaron.`
        : null,
    );
  }

  function otraSesion() {
    sesionRef.current = null;
    setSesionCreada(false);
    setItems([]);
    setError(null);
    setAviso(null);
    setPaso("");
    setFase("formulario");
  }

  const enCurso = fase === "enviando";
  const bloqueado = enCurso || sesionCreada;
  const listaAtletas = atletas ?? [];
  // La mano del jugador elegido (o de la que se está cargando) define de qué lado se recomienda la cámara: el contrario a la mano
  // dominante, como en las grabaciones de referencia (decisión 013). El esquema se espeja para un zurdo.
  const manoJugador = atletaId === "nuevo" ? mano : (listaAtletas.find((a) => a.id === atletaId)?.mano_dominante ?? "");
  const recomendado = ladoRecomendado(manoJugador);
  const ladoDibujado: LadoEsquema = lado === "derecha" || lado === "izquierda" ? lado : (recomendado ?? "izquierda");
  const validos = items.filter((it) => !it.problema);
  const pendientes = validos.filter((it) => it.estado !== "enviado");
  const resumen = resumenDeCarga(validos.map((it) => it.estado));

  if (fase === "listo") {
    return (
      <main className="mx-auto max-w-xl px-6 py-16">
        <div className="rounded-xl border border-border bg-card p-6">
          <CheckCircle2 className="h-8 w-8 text-neon" aria-hidden="true" />
          <h1 className="mt-4 font-display text-2xl font-bold">
            {resumen.enviados === 1 ? "Tu golpe se está analizando" : `Tus ${resumen.enviados} golpes se están analizando`}
          </h1>
          <p className="mt-3 text-sm text-muted-foreground">
            Cada golpe tarda unos minutos y se analizan de a uno.{" "}
            <strong className="text-foreground">Podés cerrar esta página:</strong> el análisis sigue en el servidor y los resultados van a
            estar en tus sesiones.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => navegar({ to: "/videos" })}
              className="rounded-md bg-gradient-neon px-4 py-2 text-sm font-semibold text-neon-foreground shadow-neon"
            >
              Ver mis sesiones
            </button>
            <button type="button" onClick={otraSesion} className="rounded-md border border-border px-4 py-2 text-sm font-medium hover:border-neon/50">
              Cargar otra sesión
            </button>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <h1 className="font-display text-3xl font-bold">Cargar tus golpes</h1>
      <p className="mt-2 text-sm text-muted-foreground">
        Un video es un golpe. Podés elegir varios videos a la vez: forman una sesión (hasta {MAX_GOLPES}). Para ver cuánto variás entre
        golpes conviene cargar al menos 6.
      </p>

      {/* La instrucción va ANTES de elegir el archivo (decisiones 029 y 030): si el teléfono convierte el video, no hay arreglo posterior. */}
      <section aria-labelledby="como-subir" className="mt-8 rounded-xl border border-neon/40 bg-neon/5 p-5">
        <h2 id="como-subir" className="flex items-center gap-2 font-display text-base font-semibold">
          <Info className="h-4 w-4 text-neon" aria-hidden="true" />
          Antes de elegir los archivos (iPhone)
        </h2>
        <ol className="mt-3 list-decimal space-y-2 pl-5 text-sm">
          <li>
            En <strong>Fotos</strong>, abrí el video y tocá <strong>Editar</strong>. <strong>Recortá</strong> cada golpe: dejá solo el
            golpe (unos 2 a 5 segundos) y guardalo como un clip aparte.
          </li>
          <li>
            Sacale la cámara lenta: en la <strong>barra de rayitas</strong> de abajo, dejá <strong>todo el tramo a velocidad normal</strong>.
          </li>
          <li>
            Al subirlos, en el selector tocá <strong>Opciones</strong> (abajo a la izquierda) y elegí <strong>Formato: Actual</strong>.
          </li>
        </ol>
        <p className="mt-3 text-sm text-muted-foreground">
          Lo que grabaste a 240 fps se conserva aunque se vea a velocidad normal. Si el recorte mantiene parte en cámara lenta, el
          teléfono lo convierte al subirlo (llega a unos 50 fps) aunque elijas «Actual», y no se puede analizar. Con el formato por
          defecto también convierte el video y descarta fotogramas: queda por debajo de los 120 fps que hacen falta. Otra opción:
          guardalos en la app <strong>Archivos</strong> y elegilos desde ahí. Un video sin recortar de más de 50 MB tampoco entra.
        </p>
      </section>

      <form onSubmit={enviar} className="mt-8 space-y-8" noValidate>
        {sesionCreada && (
          <p role="note" className="flex items-start gap-2 rounded-md border border-border px-3 py-2 text-sm text-muted-foreground">
            <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            La sesión ya se creó: sus datos no se pueden cambiar. Si querés otros datos, cargá una sesión nueva.
          </p>
        )}

        <fieldset disabled={bloqueado} className="space-y-5">
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

        <fieldset disabled={bloqueado} className="space-y-5">
          <legend className="font-display text-lg font-semibold">La sesión</legend>
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
          </div>

          {/* El encuadre se elige mirando dónde estaba la cámara: un esquema por opción (el sesgo de la medición es fijo por encuadre). */}
          <div role="radiogroup" aria-labelledby="titulo-encuadre" aria-describedby="ayuda-encuadre">
            <div id="titulo-encuadre" className="text-sm font-medium">Encuadre de la cámara</div>
            <div className="mt-2 grid gap-3 sm:grid-cols-2">
              {ENCUADRES.map((x) => {
                const activo = encuadre === x.valor;
                return (
                  <label
                    key={x.valor}
                    className={
                      "flex cursor-pointer flex-col gap-2 rounded-xl border p-3 transition-colors " +
                      (activo ? "border-neon bg-neon/5" : "border-border hover:border-neon/50")
                    }
                  >
                    <input
                      type="radio"
                      name="encuadre"
                      value={x.valor}
                      checked={activo}
                      onChange={() => setEncuadre(x.valor)}
                      className="sr-only"
                    />
                    <EsquemaEncuadre encuadre={x.valor} lado={ladoDibujado} className="h-24 w-full" />
                    <span className="flex items-center gap-2 text-sm font-semibold">
                      {activo ? <CheckCircle2 className="h-4 w-4 text-neon" aria-hidden="true" /> : <CircleDashed className="h-4 w-4 text-muted-foreground" aria-hidden="true" />}
                      {x.etiqueta}
                    </span>
                    <span className="text-xs text-muted-foreground">{DESCRIPCION_ENCUADRE[x.valor]}</span>
                  </label>
                );
              })}
            </div>
            <p id="ayuda-encuadre" className="mt-2 text-xs text-muted-foreground">
              Elegí el que corresponde a donde estaba la cámara, y mantenelo en todas tus sesiones: tus resultados solo se pueden comparar
              entre sesiones grabadas desde el mismo lugar.
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              <span className="font-semibold text-foreground">Recomendado:</span> la cámara del lado contrario a la mano dominante
              {recomendado ? ` (a la ${recomendado} del jugador)` : " (a la izquierda de un jugador diestro)"}. Es la condición con la que
              se calibró y validó el sistema. También se puede grabar del otro lado.
            </p>
          </div>

          <div>
            <label htmlFor="lado" className="text-sm font-medium">Lado de la cámara</label>
            <select id="lado" className={CAMPO} value={lado} onChange={(e) => setLado(e.target.value)} aria-describedby="ayuda-lado">
              <option value="" disabled>Elegí una opción</option>
              {LADOS_CAMARA.map((x) => (
                <option key={x.valor} value={x.valor}>
                  {x.etiqueta}
                  {x.valor === recomendado ? " (recomendado)" : ""}
                </option>
              ))}
            </select>
            <p id="ayuda-lado" className="mt-1 text-xs text-muted-foreground">
              Es el lado del jugador, no el tuyo: «a la derecha del jugador» es del lado de su mano derecha.
              {recomendado
                ? ` Recomendado: a la ${recomendado} del jugador (el lado contrario a su mano dominante), que es el validado. Usá siempre el mismo lado para poder comparar tus sesiones.`
                : " Recomendado: el lado contrario a la mano dominante del jugador, que es el validado. Usá siempre el mismo lado para poder comparar tus sesiones."}
            </p>
            {esLadoDeLaMano(lado, manoJugador) && (
              <p role="status" className="mt-2 flex items-start gap-2 text-xs text-muted-foreground">
                <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
                Podés grabar de este lado. Este lado de cámara todavía no está validado: el brazo puede verse mejor, pero cadera, tronco y
                encuadre se calibraron con el otro lado. El reporte lo indica, y estas sesiones no se comparan con las grabadas del otro lado.
              </p>
            )}
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
          <legend className="font-display text-lg font-semibold">Tus golpes</legend>
          <label
            htmlFor="archivos"
            onDragOver={(e) => e.preventDefault()}
            onDrop={alSoltar}
            className="flex cursor-pointer flex-col items-center gap-2 rounded-xl border border-dashed border-border px-4 py-8 text-center hover:border-neon/50"
          >
            <UploadCloud className="h-7 w-7 text-neon" aria-hidden="true" />
            <span className="text-sm font-medium">
              {items.length === 0 ? "Elegí los videos (MP4 o MOV, hasta 50 MB cada uno)" : "Agregar más videos"}
            </span>
            <span className="text-xs text-muted-foreground">Cada video es un golpe. Podés elegir varios a la vez o arrastrarlos acá.</span>
          </label>
          <input
            id="archivos"
            type="file"
            multiple
            accept="video/mp4,video/quicktime,.mp4,.mov"
            className="sr-only"
            onChange={(e) => {
              agregarArchivos(e.target.files);
              e.target.value = "";
            }}
          />

          {aviso && (
            <p role="note" className="flex items-start gap-2 text-sm text-muted-foreground">
              <Info className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              {aviso}
            </p>
          )}

          {items.length > 0 && (
            <ul className="space-y-2" aria-label="Videos elegidos">
              {items.map((it, i) => (
                <li
                  key={it.clave}
                  className={
                    "rounded-xl border px-4 py-3 text-sm " +
                    (it.problema || it.estado === "error" ? "border-destructive/50" : "border-border")
                  }
                >
                  <div className="flex items-center gap-3">
                    <Film className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden="true" />
                    <div className="min-w-0 flex-1">
                      <div className="truncate font-medium">
                        <span className="font-mono text-xs text-muted-foreground">Golpe {i + 1} · </span>
                        {it.archivo.name}
                      </div>
                      <div className="font-mono text-xs text-muted-foreground">
                        {(it.archivo.size / (1024 * 1024)).toFixed(1)} MB{it.duracion !== null ? ` · ${fmt(it.duracion, 1)} s` : ""}
                      </div>
                    </div>
                    <span
                      className={
                        "flex shrink-0 items-center gap-1.5 font-mono text-[11px] uppercase tracking-widest " +
                        (it.problema || it.estado === "error"
                          ? "text-destructive"
                          : it.estado === "enviado"
                            ? "text-state-ok"
                            : "text-muted-foreground")
                      }
                    >
                      {it.problema ? (
                        <>
                          <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" /> No se va a subir
                        </>
                      ) : it.estado === "subiendo" || it.estado === "enviando" ? (
                        <>
                          <Loader2 className="h-3.5 w-3.5 animate-spin" aria-hidden="true" />
                          {ETIQUETA_ESTADO[it.estado]}
                          {it.estado === "subiendo" ? ` ${Math.round(it.progreso * 100)} %` : ""}
                        </>
                      ) : it.estado === "enviado" ? (
                        <>
                          <CheckCircle2 className="h-3.5 w-3.5" aria-hidden="true" /> {ETIQUETA_ESTADO.enviado}
                        </>
                      ) : it.estado === "error" ? (
                        <>
                          <AlertTriangle className="h-3.5 w-3.5" aria-hidden="true" /> {ETIQUETA_ESTADO.error}
                        </>
                      ) : (
                        ETIQUETA_ESTADO.pendiente
                      )}
                    </span>
                    {!enCurso && it.estado !== "enviado" && (
                      <button
                        type="button"
                        onClick={() => quitar(it.clave)}
                        aria-label={`Quitar ${it.archivo.name}`}
                        className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-border text-muted-foreground hover:text-foreground"
                      >
                        <X className="h-4 w-4" aria-hidden="true" />
                      </button>
                    )}
                  </div>
                  {it.estado === "subiendo" && (
                    <progress className="mt-2 h-1.5 w-full" value={it.progreso} max={1} aria-label={`Progreso de ${it.archivo.name}`} />
                  )}
                  {it.problema && <p className="mt-2 text-sm text-destructive">{it.problema}</p>}
                  {it.error && <p className="mt-2 text-sm text-destructive">{it.error}</p>}
                  {!it.problema && it.duracion !== null && it.duracion > DURACION_AVISO_S && (
                    <p className="mt-2 text-xs text-muted-foreground">
                      Dura {fmt(it.duracion, 0)} s: probablemente tenga varios golpes. El sistema analiza un golpe por video; conviene
                      recortarlo para dejar solo uno.
                    </p>
                  )}
                </li>
              ))}
            </ul>
          )}

          {validos.length > 0 && validos.length < 6 && !enCurso && (
            <p role="note" className="flex items-start gap-2 text-xs text-muted-foreground">
              <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" aria-hidden="true" />
              Con menos de 6 golpes el reporte de la sesión no puede decir cuánto variás entre golpes. Se puede cargar igual.
            </p>
          )}
        </fieldset>

        {error && (
          <p role="alert" className="flex items-start gap-2 rounded-md border border-destructive/50 px-3 py-2 text-sm text-destructive">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
            {error}
          </p>
        )}

        {enCurso ? (
          <div role="status" aria-live="polite" className="rounded-xl border border-border bg-card p-4">
            <p className="flex items-center gap-2 text-sm font-medium">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
              {paso || "Preparando…"}
            </p>
            <p className="mt-2 text-xs text-muted-foreground">
              Se suben de a uno. No cierres esta página hasta que termine de subir: después el análisis sigue solo.
            </p>
          </div>
        ) : (
          <div className="sticky bottom-0 -mx-2 border-t border-border bg-background/95 px-2 py-3 backdrop-blur">
            <button
              type="submit"
              className="flex w-full items-center justify-center gap-2 rounded-md bg-gradient-neon px-4 py-2.5 text-sm font-semibold text-neon-foreground shadow-neon"
            >
              {pendientes.length <= 1 ? "Subir y analizar" : `Subir y analizar ${pendientes.length} golpes`}
            </button>
            {!sesion && (
              <Link to="/ingreso" className="mt-2 block text-center text-sm text-foreground underline underline-offset-4">Ingresar</Link>
            )}
          </div>
        )}
      </form>
    </main>
  );
}
