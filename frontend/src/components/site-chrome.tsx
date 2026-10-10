import { Link } from "@tanstack/react-router";
import { Activity } from "lucide-react";
import avatar from "@/assets/profile-avatar.jpg";
import { useSesion } from "@/lib/sesion";

export function Header() {
  const { sesion, cargando, nombre, cerrarSesion } = useSesion();
  // Especificación §3: sin sesión, Landing y Tecnología; con sesión, Biblioteca · Cargar · Perfil.
  const links = (
    sesion
      ? [
          { to: "/videos", label: "Biblioteca" },
          { to: "/upload", label: "Cargar" },
          { to: "/profile", label: "Perfil" },
        ]
      : [
          { to: "/", label: "Inicio" },
          { to: "/tecnologia", label: "Tecnología" },
        ]
  ) as { to: "/" | "/videos" | "/upload" | "/profile" | "/tecnologia"; label: string }[];

  return (
    <header className="sticky top-0 z-50 glass">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-y-2 px-4 py-3 md:px-6 md:py-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-neon shadow-neon">
            <Activity className="h-5 w-5 text-neon-foreground" strokeWidth={2.5} />
          </div>
          <div className="leading-tight">
            <div className="font-display text-lg font-bold">KinetiQ</div>
            <div className="hidden font-mono text-[10px] uppercase tracking-widest text-muted-foreground sm:block">tennis · vision · ai</div>
          </div>
        </Link>
        <nav className="order-3 flex w-full items-center justify-center gap-1 md:order-none md:w-auto" aria-label="Principal">
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
        <div className="flex items-center gap-3">
          {cargando ? null : sesion ? (
            <>
              <Link to="/upload" className="hidden rounded-md bg-gradient-neon px-4 py-2 text-sm font-semibold text-neon-foreground shadow-neon transition-transform hover:scale-105 md:block">
                Subir video
              </Link>
              <Link to="/profile" className="flex items-center gap-2 rounded-full border border-border p-1 sm:pr-3 transition-colors hover:border-neon/50" aria-label={`Perfil de ${nombre ?? "tu cuenta"}`}>
                <img src={avatar} alt="" className="h-7 w-7 rounded-full object-cover" />
                <span className="hidden font-mono text-xs text-muted-foreground sm:inline">{nombre}</span>
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
      </div>
    </header>
  );
}

export function Footer() {
  return (
    <footer className="mt-32 border-t border-border">
      <div className="mx-auto grid max-w-7xl gap-8 px-6 py-12 md:grid-cols-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-neon">
              <Activity className="h-4 w-4 text-neon-foreground" strokeWidth={2.5} />
            </div>
            <span className="font-display text-lg font-bold">KinetiQ</span>
          </div>
          <p className="mt-3 text-sm text-muted-foreground">Visión artificial aplicada a la secuenciación de la cadena cinética en tenis.</p>
        </div>
        <div>
          <div className="font-display text-sm font-semibold">Producto</div>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li>Carga y verificación</li><li>Reporte</li><li>Evolución del atleta</li>
          </ul>
        </div>
        <div>
          <div className="font-display text-sm font-semibold">Compañía</div>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li>Sobre nosotros</li><li>Investigación</li><li>Contacto</li>
          </ul>
        </div>
        <div>
          <div className="font-display text-sm font-semibold">Legal</div>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li>Privacidad</li><li>Términos</li><li>Alcance del sistema</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border py-5 text-center font-mono text-xs text-muted-foreground">
        © 2026 KinetiQ Sports Vision · Todos los derechos reservados
      </div>
    </footer>
  );
}
