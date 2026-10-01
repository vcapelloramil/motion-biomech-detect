-- Esquema inicial de KinetiQ — Etapa 4.5, tarea 4.5.1.
--
-- Nueve tablas (no siete: ver docs/decisiones/018-esquema-datos-etapa-4.5.md). El apartado 4.4.6
-- de la tesis documenta el razonamiento original de siete tablas; este archivo y la decisión 018
-- son la fuente de verdad actual sobre la estructura real.
--
-- Convención del proyecto: archivos de migración numerados, nunca editados retroactivamente
-- (docs/tesis/capitulo-4-marco-tecnologico.md, apartado 4.4.6, "Migraciones"). Un cambio de
-- esquema futuro es un archivo nuevo.

create extension if not exists pgcrypto;

-- =============================================================================================
-- usuarios
-- =============================================================================================
-- El id NO es un uuid independiente: es el mismo id que auth.users, para que la tabla ya quede
-- lista para la Etapa 7 (autenticación) sin otra migración. La fila se crea sola al registrarse,
-- con el trigger de más abajo (ajuste 3 de la decisión 018) — no la crea la aplicación a mano.
create table public.usuarios (
    id uuid primary key references auth.users (id) on delete cascade,
    email text not null unique,
    nombre text not null,
    rol text not null
        check (rol in ('jugador', 'entrenador', 'profesional_salud')),
    -- Decide qué vista abre un reporte por defecto (especificación de frontend §4).
    -- No determina el contenido: las dos vistas muestran los mismos datos.
    vista_por_defecto text not null default 'simple'
        check (vista_por_defecto in ('simple', 'detallada')),
    creado_en timestamptz not null default now()
);

comment on table public.usuarios is
    'Un usuario por cuenta. id = auth.users.id (ver decisión 018).';

-- --- Trigger de alta: crea la fila de usuarios sola al registrarse (decisión 018, ajuste 3) ---
--
-- security definer: corre con los permisos de quien es DUEÑO de la función (quien aplica esta
-- migración), no de quien dispara el alta. Es necesario porque usuarios tiene RLS habilitada y
-- el registro lo puede iniciar cualquiera (incluso sin estar autenticado todavía). El dueño de la
-- función es también dueño de la tabla, así que no necesita un GRANT aparte: a un dueño de tabla
-- no lo frena su propia RLS salvo que se declare FORCE ROW LEVEL SECURITY (no se declaró).
--
-- rol sale de los metadatos del registro (auth.users.raw_user_meta_data ->> 'rol') si vienen, o
-- 'jugador' si no. Si el valor que llega no está en el vocabulario cerrado de usuarios.rol, la
-- restricción CHECK de la tabla lo rechaza — y como el trigger corre en la MISMA transacción que
-- el INSERT en auth.users, el alta completa falla en vez de guardar un dato inconsistente (mismo
-- principio que el apartado 4.4.6: "un dato inconsistente no debe poder escribirse"). Probado en
-- tests/integration/test_trigger_alta_usuario.py.
create function public.manejar_alta_usuario()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
begin
    insert into public.usuarios (id, email, nombre, rol)
    values (
        new.id,
        new.email,
        coalesce(new.raw_user_meta_data ->> 'nombre', split_part(new.email, '@', 1)),
        coalesce(new.raw_user_meta_data ->> 'rol', 'jugador')
    );
    return new;
end;
$$;

create trigger al_registrarse
    after insert on auth.users
    for each row
    execute function public.manejar_alta_usuario();

-- =============================================================================================
-- atletas
-- =============================================================================================
create table public.atletas (
    id uuid primary key default gen_random_uuid(),
    usuario_id uuid not null references public.usuarios (id) on delete cascade,
    nombre text not null,
    mano_dominante text not null
        check (mano_dominante in ('derecha', 'izquierda')),
    edad integer
        check (edad is null or (edad > 0 and edad < 120)),
    nivel text not null
        check (nivel in ('recreativo', 'intermedio', 'avanzado')),
    creado_en timestamptz not null default now()
);

create index atletas_usuario_id_idx on public.atletas (usuario_id);

-- =============================================================================================
-- sesiones  — NUEVA (decisión 018). Agrupa los videos de un mismo golpe, atleta, encuadre y
-- lado de cámara (especificación de frontend §5: "una sesión = un grupo de videos").
-- =============================================================================================
create table public.sesiones (
    id uuid primary key default gen_random_uuid(),
    usuario_id uuid not null references public.usuarios (id) on delete cascade,
    atleta_id uuid not null references public.atletas (id) on delete cascade,
    gesto text not null
        check (gesto in ('saque', 'drive', 'reves')),
    encuadre text not null
        check (encuadre in ('perfil', 'tres_cuartos')),
    lado_camara text not null
        check (lado_camara in ('derecha', 'izquierda')),
    -- Fecha de grabación, editable por el usuario; distinta de creado_en (fecha de carga).
    fecha date not null default current_date,
    creado_en timestamptz not null default now()
);

create index sesiones_usuario_id_idx on public.sesiones (usuario_id);
create index sesiones_atleta_id_idx on public.sesiones (atleta_id);

-- =============================================================================================
-- versiones_motor — antes que reportes_biomecanicos, que la referencia.
-- =============================================================================================
create table public.versiones_motor (
    id uuid primary key default gen_random_uuid(),
    version_motor text not null,
    backend_pose text not null,
    version_modelo text,
    parametros_dsp jsonb,
    publicada_en timestamptz not null default now()
);

-- =============================================================================================
-- videos (= un golpe). sesion_id es nuevo; gesto y atleta_id se leen por la sesión, ya no se
-- duplican acá (decisión 018).
-- =============================================================================================
create table public.videos (
    id uuid primary key default gen_random_uuid(),
    sesion_id uuid not null references public.sesiones (id) on delete cascade,
    usuario_id uuid not null references public.usuarios (id) on delete cascade,
    ruta_almacenamiento text not null,
    fps_real numeric
        check (fps_real is null or fps_real > 0),
    total_fotogramas integer
        check (total_fotogramas is null or total_fotogramas >= 0),
    duracion_s numeric
        check (duracion_s is null or duracion_s >= 0),
    resolucion text,
    apto_fase_rapida boolean,
    estado text not null default 'pendiente'
        check (estado in ('pendiente', 'encolado', 'procesando', 'completado', 'parcial', 'fallido')),
    ruta_miniatura text,
    -- Los tres fotogramas clave de la vista simple (especificación de frontend §6, "tres momentos
    -- del golpe": pico de cadera, de tronco y de brazo).
    ruta_fotograma_pelvis text,
    ruta_fotograma_torso text,
    ruta_fotograma_brazo text,
    creado_en timestamptz not null default now(),
    -- Minimización de datos (apartado 4.5.2 de la tesis): el video original se borra a los 7 días.
    eliminado_en timestamptz
);

create index videos_sesion_id_idx on public.videos (sesion_id);
create index videos_usuario_id_idx on public.videos (usuario_id);

-- Estado agregado de la sesión: vista, no columna (decisión 018, punto 1). Evita un trigger de
-- sincronización que el volumen actual no justifica. Va acá (no junto a la tabla sesiones) porque
-- depende de que exista la tabla videos.
--
-- security_invoker = true es OBLIGATORIO: sin esto, Postgres ejecuta la vista con los permisos de
-- quien la creó (ignora RLS de quien consulta). Con esto, la vista respeta la RLS de sesiones y
-- videos del usuario que consulta, igual que si consultara las tablas directamente.
create view public.sesiones_resumen
    with (security_invoker = true)
as
select
    s.id as sesion_id,
    count(v.id) as total_videos,
    count(*) filter (where v.estado = 'completado') as videos_completados,
    count(*) filter (where v.estado = 'parcial') as videos_parciales,
    count(*) filter (where v.estado = 'fallido') as videos_fallidos,
    count(*) filter (where v.estado in ('pendiente', 'encolado', 'procesando')) as videos_en_curso,
    case
        when count(v.id) = 0 then 'sin_videos'
        when count(*) filter (where v.estado in ('pendiente', 'encolado', 'procesando')) > 0
            then 'procesando'
        when count(*) filter (where v.estado = 'fallido') = count(v.id) then 'fallido'
        when count(*) filter (where v.estado in ('parcial', 'fallido')) > 0 then 'parcial'
        else 'completado'
    end as estado_agregado
from public.sesiones s
left join public.videos v on v.sesion_id = s.id
group by s.id;

comment on view public.sesiones_resumen is
    'estado_agregado calculado, no almacenado (decisión 018). RLS de la vista hereda la de sesiones y videos.';

-- =============================================================================================
-- reportes_biomecanicos (por golpe, 1:1 con video). ruta_pdf se fue a reportes_sesion: el PDF es
-- siempre de la sesión completa, no por golpe (confirmado en la maqueta ReporteDetallado).
-- =============================================================================================
create table public.reportes_biomecanicos (
    id uuid primary key default gen_random_uuid(),
    video_id uuid not null unique references public.videos (id) on delete cascade,
    version_motor_id uuid not null references public.versiones_motor (id),
    -- Lista ordenada de segmentos, p.ej. ["pelvis", "torso", "brazo"]. jsonb en vez de texto
    -- suelto para que quede explícitamente ordenado y validable.
    orden_picos_observado jsonb,
    orden_picos_esperado jsonb,
    -- bool | null a propósito: la decisión 015 dejó abierto para la Etapa 5 cómo representar un
    -- orden auditable Y ordenable pero sin referencia bibliográfica para juzgarlo correcto o
    -- incorrecto (caso "perfil invertido"). No se inventa un tercer valor acá.
    secuencia_correcta boolean,
    separacion_cadera_hombro_max numeric,
    corte_filtro_hz numeric
        check (corte_filtro_hz is null or corte_filtro_hz > 0),
    cobertura_auditable_pct numeric
        check (cobertura_auditable_pct is null or (cobertura_auditable_pct >= 0 and cobertura_auditable_pct <= 100)),
    -- Video con esqueleto superpuesto: se reutiliza en la biblioteca y en el Nivel 2 del reporte.
    ruta_overlay text,
    creado_en timestamptz not null default now()
);

create index reportes_biomecanicos_video_id_idx on public.reportes_biomecanicos (video_id);

-- =============================================================================================
-- metricas (por reporte de golpe)
-- =============================================================================================
create table public.metricas (
    id uuid primary key default gen_random_uuid(),
    reporte_id uuid not null references public.reportes_biomecanicos (id) on delete cascade,
    segmento text not null
        check (segmento in ('pelvis', 'torso', 'brazo', 'rodilla', 'codo')),
    tipo text not null
        check (tipo in ('angulo_max', 'velocidad_pico', 'instante_pico')),
    -- null cuando auditable = false. Nunca se estima (R3).
    valor numeric,
    unidad text not null,
    confianza_media numeric
        check (confianza_media is null or (confianza_media >= 0 and confianza_media <= 1)),
    auditable boolean not null,
    constraint metricas_valor_coherente_con_auditable check (
        (auditable and valor is not null) or (not auditable and valor is null)
    )
);

create index metricas_reporte_id_idx on public.metricas (reporte_id);

-- =============================================================================================
-- alertas (por reporte de golpe)
-- =============================================================================================
create table public.alertas (
    id uuid primary key default gen_random_uuid(),
    reporte_id uuid not null references public.reportes_biomecanicos (id) on delete cascade,
    codigo text not null,
    -- Los CUATRO estados de R3 (CLAUDE.md), no los tres de reporte.py todavía congelado en la
    -- Etapa 0, ni el "info|atencion|riesgo|no_auditable" desactualizado del apartado 4.4.6.
    -- Desalineación conocida y deliberada: ver docs/decisiones/018-esquema-datos-etapa-4.5.md,
    -- punto 2. Se resuelve en reporte.py al arrancar la Etapa 5, antes de generar JSON real.
    severidad text not null
        check (severidad in ('correcto', 'desvio_leve', 'alerta_de_carga', 'no_auditable')),
    mensaje_usuario text not null,
    -- R4: toda alerta responde qué magnitud la disparó (fundamento_tecnico) y qué fuente la
    -- respalda (referencia_bibliografica).
    fundamento_tecnico text,
    referencia_bibliografica text,
    instante_s numeric
        check (instante_s is null or instante_s >= 0)
);

create index alertas_reporte_id_idx on public.alertas (reporte_id);

-- =============================================================================================
-- reportes_sesion — NUEVA (decisión 018). Agrega el puntaje de rendimiento y las observaciones
-- de nivel 1 a través de los golpes de la sesión (especificación de frontend §6, §7, §9).
-- =============================================================================================
create table public.reportes_sesion (
    id uuid primary key default gen_random_uuid(),
    sesion_id uuid not null unique references public.sesiones (id) on delete cascade,
    -- Puntaje total en columna tipada (no solo en el jsonb de abajo): la pantalla de Evolución lo
    -- consulta a través de varias sesiones, y version_formula es trazabilidad exigida por R4.
    puntaje numeric
        check (puntaje is null or (puntaje >= 0 and puntaje <= 100)),
    -- Por qué puntaje es null, con el detalle que un booleano no distingue (especificación de
    -- frontend §7): 'no_auditable' = menos de dos componentes auditables; 'sin_referencia' = al
    -- jugador todavía le falta una sesión previa comparable de este golpe ("Desde tu 2.ª sesión de
    -- este golpe", sin número, no es lo mismo que "no auditable"). Reemplaza al booleano
    -- puntaje_auditable que tenía la primera versión de esta migración (decisión 018, ajuste 1).
    estado_puntaje text not null
        check (estado_puntaje in ('calculado', 'no_auditable', 'sin_referencia')),
    version_formula text,
    -- Forma todavía no congelada (especificación de frontend §7: "la fórmula exacta se congela en
    -- una decisión de la Etapa 5"). jsonb a propósito, ver decisión 018, para no adivinar una
    -- estructura tipada que puede cambiar; se normaliza después con una migración nueva si hace
    -- falta.
    componentes jsonb,
    observaciones jsonb,
    -- Igual que ruta_almacenamiento/ruta_overlay/ruta_miniatura/ruta_fotograma_* de otras tablas:
    -- es una ruta a un objeto de Storage, no el archivo en sí. El ON DELETE CASCADE de más abajo
    -- (y el de usuarios -> ... -> sesiones) borra la FILA cuando se borra la sesión o el usuario,
    -- pero NO borra el objeto correspondiente en Storage — Postgres no puede tocar storage.objects
    -- desde una cascada sobre estas tablas. Pendiente para la Etapa 7 ("eliminar mi cuenta y mis
    -- datos", Ley 25.326, decisión 018 ajuste 2): el flujo de borrado de cuenta tiene que borrar
    -- también los archivos de Storage, aparte de dejar que la base cascadee sola.
    ruta_pdf text,
    -- Sesión anterior comparable del mismo gesto y encuadre (especificación de frontend §6,
    -- "Comparado con vos mismo"). on delete set null: si se borra el reporte anterior, este no
    -- se borra en cascada, solo pierde la referencia.
    sesion_anterior_comparable_id uuid references public.reportes_sesion (id) on delete set null,
    creado_en timestamptz not null default now(),
    constraint reportes_sesion_puntaje_coherente_con_estado check (
        (estado_puntaje = 'calculado' and puntaje is not null)
        or (estado_puntaje <> 'calculado' and puntaje is null)
    )
);

create index reportes_sesion_sesion_id_idx on public.reportes_sesion (sesion_id);
create index reportes_sesion_anterior_idx on public.reportes_sesion (sesion_anterior_comparable_id);
