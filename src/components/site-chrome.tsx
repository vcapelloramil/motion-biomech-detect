import { Link } from "@tanstack/react-router";
import { Activity } from "lucide-react";
import avatar from "@/assets/profile-avatar.jpg";

export function Header() {
  const links = [
    { to: "/", label: "Inicio" },
    { to: "/upload", label: "Subir" },
    { to: "/videos", label: "Videos" },
    { to: "/performance", label: "Performance" },
    { to: "/clinica", label: "Clínico" },
    { to: "/tecnologia", label: "Tecnología" },
  ] as const;

  return (
    <header className="sticky top-0 z-50 glass">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-neon shadow-neon">
            <Activity className="h-5 w-5 text-neon-foreground" strokeWidth={2.5} />
          </div>
          <div className="leading-tight">
            <div className="font-display text-lg font-bold">KinetiQ</div>
            <div className="font-mono text-[10px] uppercase tracking-widest text-muted-foreground">tennis · vision · ai</div>
          </div>
        </Link>
        <nav className="hidden items-center gap-1 lg:flex">
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
          <Link to="/upload" className="hidden rounded-md bg-gradient-neon px-4 py-2 text-sm font-semibold text-neon-foreground shadow-neon transition-transform hover:scale-105 md:block">
            Subir video
          </Link>
          <Link to="/profile" className="flex items-center gap-2 rounded-full border border-border p-1 pr-3 transition-colors hover:border-neon/50">
            <img src={avatar} alt="Perfil" className="h-7 w-7 rounded-full object-cover" />
            <span className="hidden font-mono text-xs text-muted-foreground sm:inline">Marco R.</span>
          </Link>
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
          <p className="mt-3 text-sm text-muted-foreground">Visión artificial al servicio del tenis y la salud del jugador.</p>
        </div>
        <div>
          <div className="font-display text-sm font-semibold">Producto</div>
          <ul className="mt-3 space-y-2 text-sm text-muted-foreground">
            <li>Performance</li><li>Análisis clínico</li><li>API YOLO</li>
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
            <li>Privacidad</li><li>Términos</li><li>Datos médicos</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-border py-5 text-center font-mono text-xs text-muted-foreground">
        © 2026 KinetiQ Sports Vision · Todos los derechos reservados
      </div>
    </footer>
  );
}
