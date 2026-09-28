import { useState } from "react";
import { AlertCircle, GraduationCap, ShieldCheck, Users } from "lucide-react";

import { api, csrf, type Identity, type Role } from "../api";

function explain(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

export function Login({ onLogin }: { onLogin: (identity: Identity) => void }) {
  const [mode, setMode] = useState<"login" | "forgot" | "reset" | "activate">(
    "login",
  );
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [code, setCode] = useState("");
  const [studentCode, setStudentCode] = useState("");
  const [fullName, setFullName] = useState("");
  const [message, setMessage] = useState("");
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

  async function auxiliarySubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setMessage("");
    setBusy(true);
    try {
      if (mode === "forgot") {
        const result = await api<{ detail: string; reset_code?: string }>(
          "/auth/password-reset/",
          "POST",
          { email },
        );
        setMessage(result.detail);
        if (result.reset_code) setCode(result.reset_code);
        setMode("reset");
      } else if (mode === "reset") {
        await api("/auth/password-reset/confirm/", "POST", { code, password });
        setMessage("Contraseña restablecida. Ya puedes iniciar sesión.");
        setMode("login");
      } else {
        await api("/auth/activate/", "POST", {
          student_code: studentCode,
          email,
          full_name: fullName,
          password,
        });
        setMessage("Cuenta activada. Ya puedes iniciar sesión.");
        setMode("login");
      }
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
          <h2>
            {mode === "login"
              ? "Ingresar al portal"
              : mode === "forgot"
                ? "Recuperar acceso"
                : mode === "reset"
                  ? "Nueva contraseña"
                  : "Activar cuenta de alumno"}
          </h2>
          <p>
            {mode === "login"
              ? "Usa tu correo institucional o código universitario."
              : "Completa los datos solicitados para proteger tu cuenta."}
          </p>
          <form onSubmit={mode === "login" ? submit : auxiliarySubmit}>
            {mode === "activate" && (
              <>
                <label>
                  Código universitario
                  <input
                    required
                    value={studentCode}
                    onChange={(e) => setStudentCode(e.target.value)}
                  />
                </label>
                <label>
                  Nombres y apellidos
                  <input
                    required
                    minLength={5}
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </label>
              </>
            )}
            {mode !== "reset" && (
              <label>
                {mode === "login"
                  ? "Correo institucional o código"
                  : "Correo institucional"}
                <input
                  type={mode === "login" ? "text" : "email"}
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  required
                  placeholder="codigo@unfv.edu.pe"
                  autoComplete="username"
                />
              </label>
            )}
            {mode === "reset" && (
              <label>
                Código de recuperación
                <input
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                />
              </label>
            )}
            {mode !== "forgot" && (
              <label>
                {mode === "login" ? "Contraseña" : "Nueva contraseña"}
                <input
                  type="password"
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  required
                  minLength={mode === "login" ? undefined : 12}
                  placeholder="Ingresa tu contraseña"
                  autoComplete="current-password"
                />
              </label>
            )}
            {error && (
              <div className="alert error">
                <AlertCircle size={16} />
                {error}
              </div>
            )}
            {message && <div className="alert good">{message}</div>}
            <button className="btn primary wide" disabled={busy}>
              {busy
                ? "Procesando..."
                : mode === "login"
                  ? "Ingresar al portal"
                  : mode === "forgot"
                    ? "Enviar instrucciones"
                    : mode === "reset"
                      ? "Guardar contraseña"
                      : "Activar cuenta"}{" "}
              <span>→</span>
            </button>
          </form>
          <div className="login-actions">
            {mode === "login" ? (
              <>
                <button type="button" onClick={() => setMode("forgot")}>
                  Olvidé mi contraseña
                </button>
                <button type="button" onClick={() => setMode("activate")}>
                  Activar cuenta de alumno
                </button>
              </>
            ) : (
              <button type="button" onClick={() => setMode("login")}>
                Volver al inicio de sesión
              </button>
            )}
          </div>
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
