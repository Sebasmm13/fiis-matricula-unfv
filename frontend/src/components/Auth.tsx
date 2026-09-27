import { useState } from "react";
import { AlertCircle, GraduationCap, ShieldCheck, Users } from "lucide-react";

import { api, csrf, type Identity, type Role } from "../api";

function explain(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

export function Login({ onLogin }: { onLogin: (identity: Identity) => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      await csrf();
      onLogin(await api<Identity>("/auth/login/", "POST", { email, password }));
    } catch (requestError) {
      setError(explain(requestError));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-screen">
      <div className="login-aside">
        <div className="brand white">
          <img className="faculty-logo" src="/fiis-logo.png" alt="Logo FIIS" />
          <span>
            FIIS<span className="brand-dot">.</span>
          </span>
        </div>
        <div className="login-copy">
          <div className="eyebrow light">
            UNIVERSIDAD NACIONAL FEDERICO VILLARREAL
          </div>
          <h1>
            Tu camino académico,
            <br />
            <em>más claro.</em>
          </h1>
          <p>
            Planifica tus cursos, elige tu sección y consulta tu avance
            académico desde un solo lugar.
          </p>
          <div className="login-feature">
            <GraduationCap size={20} />
            <span>Escuela Profesional de Ingeniería de Sistemas</span>
          </div>
        </div>
        <div className="login-bottom">
          PORTAL DE MATRÍCULA · SISTEMA ACADÉMICO
        </div>
      </div>
      <div className="login-form-zone">
        <div className="login-card">
          <span className="eyebrow">BIENVENIDO DE NUEVO</span>
          <h2>Ingresar al portal</h2>
          <p>
            Usa tu correo institucional. El sistema identificará automáticamente
            tus permisos.
          </p>
          <form onSubmit={submit}>
            <label>
              Correo institucional o usuario
              <input
                type="text"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                placeholder="codigo@unfv.edu.pe o demo"
                autoComplete="username"
              />
            </label>
            <label>
              Contraseña
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                required
                placeholder="Ingresa tu contraseña"
                autoComplete="current-password"
              />
            </label>
            {error && (
              <div className="alert error">
                <AlertCircle size={16} />
                {error}
              </div>
            )}
            <button className="btn primary wide" disabled={busy}>
              {busy ? "Ingresando..." : "Ingresar al portal"} <span>→</span>
            </button>
          </form>
          <p className="login-note">
            Tus opciones de acceso dependen de los perfiles asociados a tu
            correo.
          </p>
        </div>
      </div>
    </div>
  );
}

const roleInfo: Record<
  Role,
  { label: string; description: string; icon: React.ReactNode }
> = {
  student: {
    label: "Portal del alumno",
    description: "Prematrícula, matrícula, notas y constancias.",
    icon: <GraduationCap />,
  },
  teacher: {
    label: "Portal docente",
    description: "Horarios, secciones y alumnos matriculados.",
    icon: <Users />,
  },
  admin: {
    label: "Administración",
    description: "Oferta, demanda, alumnos y configuración académica.",
    icon: <ShieldCheck />,
  },
};

export function RoleSelector({
  me,
  onSelect,
  onLogout,
}: {
  me: Identity;
  onSelect: (identity: Identity) => void;
  onLogout: () => void;
}) {
  const [busy, setBusy] = useState<Role | null>(null);
  const [error, setError] = useState("");

  async function choose(role: Role) {
    setBusy(role);
    setError("");
    try {
      onSelect(await api<Identity>("/auth/role/", "POST", { role }));
    } catch (requestError) {
      setError(explain(requestError));
      setBusy(null);
    }
  }

  return (
    <div className="role-screen">
      <div className="role-panel">
        <div className="brand role-brand">
          <img className="faculty-logo" src="/fiis-logo.png" alt="Logo FIIS" />
          <span>
            FIIS<span className="brand-dot">.</span>
          </span>
        </div>
        <span className="eyebrow">PERFILES VINCULADOS</span>
        <h1>¿Cómo deseas ingresar?</h1>
        <p>
          Tu correo <strong>{me.email}</strong> tiene más de un perfil. Cada
          acceso muestra herramientas y permisos diferentes.
        </p>
        <div className="role-grid">
          {me.roles.map((role) => {
            const info = roleInfo[role];
            return (
              <button
                key={role}
                onClick={() => void choose(role)}
                disabled={Boolean(busy)}
              >
                <span className="role-icon">{info.icon}</span>
                <strong>{info.label}</strong>
                <small>{info.description}</small>
                <b>{busy === role ? "Ingresando..." : "Continuar →"}</b>
              </button>
            );
          })}
        </div>
        {error && <div className="alert error">{error}</div>}
        <button className="btn outline" onClick={onLogout}>
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}
