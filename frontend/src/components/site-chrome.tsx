import { Link, useLocation } from "@tanstack/react-router";
import { Activity, Library, Menu, Upload, User } from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useSesion } from "@/lib/sesion";

type Destino = "/" | "/videos" | "/upload" | "/profile" | "/tecnologia";

/** Pestañas del producto con sesión (especificación §3 y §8). En el celular van abajo, con ícono y texto. */
const PESTANAS: { to: Destino; label: string; Icono: typeof Library; rutas: string[] }[] = [
  { to: "/videos", label: "Biblioteca", Icono: Library, rutas: ["/videos", "/reporte", "/sesion", "/procesando"] },
  { to: "/upload", label: "Cargar", Icono: Upload, rutas: ["/upload"] },
  { to: "/profile", label: "Perfil", Icono: User, rutas: ["/profile"] },
];

function Logo() {
  return (
    <Link to="/" className="flex items-center gap-2" aria-label="KinetiQ, inicio">
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-neon shadow-neon">
        <Activity className="h-5 w-5 text-neon-foreground" strokeWidth={2.5} />
      </div>
      <div className="leading-tight">
        <div className="font-display text-lg font-bold">KinetiQ</div>
        <div className="hidden font-mono text-[10px] uppercase tracking-widest text-muted-foreground sm:block">tennis · vision · ai</div>
      </div>
    </Link>
  );
}

export function Header() {
  const { sesion, cargando, nombre, cerrarSesion } = useSesion();
  const inicial = (nombre ?? "?").trim().charAt(0) || "?";
  // Escritorio (sin cambios): sin sesión, Inicio y Tecnología; con sesión, Biblioteca · Cargar · Perfil.
  const links = (
    sesion
      ? PESTANAS.map(({ to, label }) => ({ to, label }))
      : [
          { to: "/", label: "Inicio" },
          { to: "/tecnologia", label: "Tecnología" },
        ]
  ) as { to: Destino; label: string }[];

  return (
    <>
      <header className="relative z-50 glass md:sticky md:top-0 print:hidden">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-3 px-4 py-2 md:px-6 md:py-4">
          <Logo />

          {/* Escritorio */}
          <nav className="hidden items-center justify-center gap-1 md:flex" aria-label="Principal">
            {links.map((l) => (
              <Link
                key={l.to}
                to={l.to}
                activeOptions={{ exact: l.to === "/" }}
                className="rounded-md px-3 py-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
                activeProps={{ className: "rounded-md px-3 py-2 text-sm text-foreground bg-secondary" }}
              >
                {l.label}
              </Link>
            ))}
          </nav>
          <div className="hidden items-center gap-3 md:flex">
            {cargando ? null : sesion ? (
              <>
                <Link to="/upload" className="rounded-md bg-gradient-neon px-4 py-2 text-sm font-semibold text-neon-foreground shadow-neon transition-transform hover:scale-105">
                  Subir video
                </Link>
                <Link to="/profile" className="flex items-center gap-2 rounded-full border border-border p-1 pr-3 transition-colors hover:border-neon/50" aria-label={`Perfil de ${nombre ?? "tu cuenta"}`}>
                  <span aria-hidden="true" className="flex h-7 w-7 items-center justify-center rounded-full bg-secondary font-mono text-[11px] font-semibold uppercase">{inicial}</span>
                  <span className="font-mono text-xs text-muted-foreground">{nombre}</span>
                </Link>
                <button
                  type="button"
                  onClick={() => void cerrarSesion()}
                  className="rounded-md px-3 py-2 text-sm text-muted-foreground hover:text-foreground"
                >
                  Salir
                </button>
              </>
            ) : (
              <>
                <Link to="/ingreso" className="rounded-md px-3 py-2 text-sm text-muted-foreground hover:text-foreground">
                  Ingresar
                </Link>
                <Link to="/registro" className="rounded-md bg-gradient-neon px-4 py-2 text-sm font-semibold text-neon-foreground shadow-neon transition-transform hover:scale-105">
                  Crear cuenta
                </Link>
              </>
            )}
          </div>

          {/* Celular (especificación §8; el ☰ se oculta bajo 360 px por falta de lugar: Tecnología queda en el pie): con sesión, solo la inicial (con «Salir» adentro) y las pestañas abajo; sin sesión, Ingresar y Crear cuenta. */}
          <div className="flex items-center gap-0.5 md:hidden">
            {cargando ? null : sesion ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button
                    type="button"
                    className="flex h-11 w-11 items-center justify-center rounded-full border border-border transition-colors hover:border-neon/50"
                    aria-label={`Menú de ${nombre ?? "tu cuenta"}`}
                  >
                    <span aria-hidden="true" className="flex h-8 w-8 items-center justify-center rounded-full bg-secondary font-mono text-xs font-semibold uppercase">{inicial}</span>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="min-w-44">
                  {nombre ? <DropdownMenuLabel className="truncate font-mono text-xs font-normal text-muted-foreground">{nombre}</DropdownMenuLabel> : null}
                  {nombre ? <DropdownMenuSeparator /> : null}
                  <DropdownMenuItem className="min-h-11 text-sm" onSelect={() => void cerrarSesion()}>
                    Salir
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <button type="button" className="hidden h-11 w-11 items-center justify-center rounded-md text-muted-foreground hover:text-foreground min-[360px]:flex" aria-label="Menú">
                      <Menu className="h-5 w-5" aria-hidden="true" />
                    </button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end" className="min-w-40">
                    <DropdownMenuItem asChild className="min-h-11 text-sm">
                      <Link to="/tecnologia">Tecnología</Link>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
                <Link to="/ingreso" className="flex min-h-11 items-center whitespace-nowrap rounded-md px-1.5 text-[13px] text-muted-foreground hover:text-foreground">
                  Ingresar
                </Link>
                <Link to="/registro" className="flex min-h-11 items-center whitespace-nowrap rounded-md bg-gradient-neon px-2.5 text-[13px] font-semibold text-neon-foreground shadow-neon">
                  Crear cuenta
                </Link>
              </>
            )}
          </div>
        </div>
      </header>
      {!cargando && sesion ? <BarraInferior /> : null}
    </>
  );
}

/** Barra fija de pestañas del celular: tres destinos con ícono y texto, de 56 px de alto (objetivo táctil mínimo de 44 px). */
function BarraInferior() {
  const { pathname } = useLocation();
  return (
    <nav
      aria-label="Principal"
      className="fixed inset-x-0 bottom-0 z-50 border-t border-border bg-background/95 backdrop-blur md:hidden print:hidden"
      style={{ paddingBottom: "env(safe-area-inset-bottom)" }}
    >
      <ul className="mx-auto grid h-14 max-w-xl grid-cols-3">
        {PESTANAS.map(({ to, label, Icono, rutas }) => {
          const activa = rutas.some((r) => pathname === r || pathname.startsWith(r + "/"));
          return (
            <li key={to} className="contents">
              <Link
                to={to}
                aria-current={activa ? "page" : undefined}
                className={
                  "flex min-h-11 flex-col items-center justify-center gap-0.5 text-[11px] font-medium transition-colors " +
                  (activa ? "text-neon" : "text-muted-foreground hover:text-foreground")
                }
              >
                <Icono className="h-5 w-5" aria-hidden="true" />
                {label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

export function Footer() {
  return (
    <footer className="mt-32 border-t border-border print:hidden">
      <div className="mx-auto grid max-w-7xl gap-8 px-6 py-12 md:grid-cols-3">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-neon">
              <Activity className="h-4 w-4 text-neon-foreground" strokeWidth={2.5} />
            </div>
            <span className="font-display text-lg font-bold">KinetiQ</span>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">Medí cómo gira tu cuerpo en cada golpe.</p>
        </div>
        <div>
          <div className="font-display text-sm font-semibold">Producto</div>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li><Link to="/tecnologia" className="hover:text-foreground">Tecnología</Link></li>
            <li><Link to="/" hash="alcance" className="hover:text-foreground">Alcance del sistema</Link></li>
          </ul>
        </div>
        <div>
          <div className="font-display text-sm font-semibold">Legal</div>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li><Link to="/privacidad" className="hover:text-foreground">Privacidad</Link></li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border py-5 text-center font-mono text-xs text-muted-foreground">
        KinetiQ documenta el movimiento. No diagnostica ni reemplaza la evaluación de un profesional.
      </div>
    </footer>
  );
}
