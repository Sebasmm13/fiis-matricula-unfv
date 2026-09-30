import { useEffect, useMemo, useState } from "react";
import {
  BookOpen,
  CalendarDays,
  ClipboardList,
  Download,
  GraduationCap,
  LayoutDashboard,
  LogOut,
  ShieldCheck,
  Users,
  BarChart3,
  Settings2,
  Search,
  Check,
  AlertCircle,
  Clock3,
  UserRound,
  Camera,
} from "lucide-react";
import {
  api,
  csrf,
  downloadReceipt,
  changePhoto,
  downloadTeacherReport,
  type Identity,
  type Catalog,
  type Course,
  type Section,
  type Enrollment,
  type Grade,
  type AdminData,
  type Demand,
  type TeacherData,
} from "./api";
import { Login, RoleSelector } from "./components/Auth";

type Page =
  | "inicio"
  | "matricula"
  | "historial"
  | "malla"
  | "admin"
  | "oferta"
  | "demanda"
  | "alumnos"
  | "auditoria"
  | "docencia"
  | "perfil";
const days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
function explain(e: unknown) {
  return e instanceof Error ? e.message : String(e);
}
function fmt(t: string) {
  return new Date(t).toLocaleDateString("es-PE", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}
function overlap(a: Section, b: Section) {
  return a.meetings.some((x) =>
    b.meetings.some(
      (y) => x.day === y.day && x.start < y.end && y.start < x.end,
    ),
  );
}
function Badge({
  children,
  kind = "neutral",
}: {
  children: React.ReactNode;
  kind?: "neutral" | "good" | "warn" | "blue";
}) {
  return <span className={`badge ${kind}`}>{children}</span>;
}

export default function App() {
  const [me, setMe] = useState<Identity | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState<Page>("inicio");
  const [notice, setNotice] = useState("");
  useEffect(() => {
    csrf()
      .then(() => api<Identity>("/me/"))
      .then(setMe)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);
  async function out() {
    await api("/auth/logout/", "POST");
    setMe(null);
    setPage("inicio");
  }
  if (loading)
    return (
      <div className="center">
        <div className="spinner" /> Cargando portal...
      </div>
    );
  if (!me)
    return (
      <Login
        onLogin={(v) => {
          setMe(v);
          setPage("inicio");
          void api<Identity>("/me/").then(setMe);
        }}
      />
    );
  if (me.must_change_password)
    return <PasswordChange onChanged={setMe} onLogout={() => void out()} />;
  if (!me.role)
    return (
      <RoleSelector
        me={me}
        onSelect={(v) => {
          setMe(v);
          setPage("inicio");
        }}
        onLogout={() => void out()}
      />
    );
  const admin = me.role === "admin";
  const teacher = me.role === "teacher";
  const nav: { id: Page; label: string; icon: React.ReactNode }[] = admin
    ? [
        { id: "inicio", label: "Resumen", icon: <LayoutDashboard size={18} /> },
        { id: "admin", label: "Configuración", icon: <Settings2 size={18} /> },
        {
          id: "oferta",
          label: "Oferta académica",
          icon: <CalendarDays size={18} />,
        },
        {
          id: "demanda",
          label: "Demanda y prematrícula",
          icon: <BarChart3 size={18} />,
        },
        { id: "alumnos", label: "Alumnos y notas", icon: <Users size={18} /> },
        {
          id: "auditoria",
          label: "Auditoría",
          icon: <ShieldCheck size={18} />,
        },
        { id: "perfil", label: "Mi perfil", icon: <UserRound size={18} /> },
      ]
    : teacher
      ? [
          {
            id: "inicio",
            label: "Resumen",
            icon: <LayoutDashboard size={18} />,
          },
          {
            id: "docencia",
            label: "Mis cursos y alumnos",
            icon: <Users size={18} />,
          },
          { id: "perfil", label: "Mi perfil", icon: <UserRound size={18} /> },
        ]
      : [
          {
            id: "inicio",
            label: "Inicio",
            icon: <LayoutDashboard size={18} />,
          },
          {
            id: "matricula",
            label: "Matrícula",
            icon: <ClipboardList size={18} />,
          },
          {
            id: "historial",
            label: "Notas e historial",
            icon: <BookOpen size={18} />,
          },
          {
            id: "malla",
            label: "Mi malla curricular",
            icon: <GraduationCap size={18} />,
          },
          { id: "perfil", label: "Mi perfil", icon: <UserRound size={18} /> },
        ];
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <img className="faculty-logo" src="/fiis-logo.png" alt="Logo FIIS" />
          <span>
            FIIS<span className="brand-dot">.</span>
          </span>
        </div>
        <div className="portal-label">PORTAL ACADÉMICO</div>
        <div className="nav-title">MENÚ PRINCIPAL</div>
        <nav>
          {nav.map((n) => (
            <button
              key={n.id}
              onClick={() => {
                setPage(n.id);
                setNotice("");
              }}
              className={page === n.id ? "selected" : ""}
            >
              {n.icon}
              <span>{n.label}</span>
            </button>
          ))}
        </nav>
        <div className="sidebar-end">
          <div className="school-mini">
            <GraduationCap size={19} /> Ingeniería de Sistemas
          </div>
          {me.roles.length > 1 && (
            <button
              className="logout"
              onClick={() => {
                setMe({ ...me, role: null });
                setPage("inicio");
              }}
            >
              <Users size={17} /> Cambiar perfil
            </button>
          )}
          <button className="logout" onClick={() => void out()}>
            <LogOut size={17} /> Cerrar sesión
          </button>
        </div>
      </aside>
      <main className="workspace">
        <header className="topbar">
          <div className="crumb">
            FIIS <span>/</span> {nav.find((x) => x.id === page)?.label}
          </div>
          <div className="top-right">
            <Badge kind="blue">{me.period?.code || "Sin período"}</Badge>
            <span className="avatar">
              {me.has_photo ? (
                <img
                  src={`/api/profile/photo/?v=${encodeURIComponent(me.photo_version || "")}`}
                  alt="Foto de perfil"
                />
              ) : (
                me.name.slice(0, 1)
              )}
            </span>
            <div className="account">
              <strong>{me.name}</strong>
              <small>
                {admin ? "Administrador" : teacher ? "Docente" : "Alumno"} ·{" "}
                {me.email}
              </small>
            </div>
          </div>
        </header>
        <div className="mobile-nav">
          {nav.map((n) => (
            <button
              className={page === n.id ? "selected" : ""}
              key={n.id}
              onClick={() => setPage(n.id)}
            >
              {n.label}
            </button>
          ))}
          {me.roles.length > 1 && (
            <button onClick={() => setMe({ ...me, role: null })}>
              Cambiar perfil
            </button>
          )}
          <button onClick={() => void out()}>Salir</button>
        </div>
        <div className="content">
          {notice && (
            <div className="alert good" role="status">
              <Check size={18} />
              {notice}
              <button onClick={() => setNotice("")}>×</button>
            </div>
          )}
          {page === "perfil" ? (
            <ProfilePage
              me={me}
              inform={setNotice}
              reloadMe={() => api<Identity>("/me/").then(setMe)}
            />
          ) : teacher ? (
            <TeacherPage page={page} period={me.period?.code || ""} />
          ) : admin ? (
            <AdminPage
              page={page}
              inform={setNotice}
              reloadMe={() => api<Identity>("/me/").then(setMe)}
            />
          ) : (
            <StudentPage page={page} me={me} inform={setNotice} />
          )}
        </div>
      </main>
    </div>
  );
}

function PasswordChange({
  onChanged,
  onLogout,
}: {
  onChanged: (me: Identity) => void;
  onLogout: () => void;
}) {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <div className="login-screen account-security-screen">
      <div className="login-form-zone">
        <div className="login-card">
          <span className="eyebrow">SEGURIDAD DE LA CUENTA</span>
          <h2>Crea una contraseña personal</h2>
          <p>
            La contraseña inicial es temporal. Debes reemplazarla antes de
            continuar.
          </p>
          <form
            onSubmit={async (e) => {
              e.preventDefault();
              if (newPassword !== confirm) {
                setError("Las contraseñas nuevas no coinciden.");
                return;
              }
              setBusy(true);
              setError("");
              try {
                onChanged(
                  await api<Identity>("/auth/change-password/", "POST", {
                    current_password: currentPassword,
                    new_password: newPassword,
                  }),
                );
              } catch (requestError) {
                setError(explain(requestError));
              } finally {
                setBusy(false);
              }
            }}
          >
            <label>
              Contraseña inicial
              <input
                type="password"
                required
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
              />
            </label>
            <label>
              Nueva contraseña
              <input
                type="password"
                required
                minLength={12}
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
            </label>
            <label>
              Confirmar contraseña
              <input
                type="password"
                required
                minLength={12}
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
              />
            </label>
            {error && <div className="alert error">{error}</div>}
            <button className="btn primary wide" disabled={busy}>
              {busy ? "Guardando..." : "Cambiar contraseña"}
            </button>
          </form>
          <button className="text-button" onClick={onLogout}>
            Cerrar sesión
          </button>
        </div>
      </div>
    </div>
  );
}

interface Convalidation { active: boolean; done: boolean; matches?: any[]; unmatched?: any[]; }

function StudentPage({
  page,
  me,
  inform,
}: {
  page: Page;
  me: Identity;
  inform: (s: string) => void;
}) {
  const [catalog, setCatalog] = useState<Catalog | null>(null);
  const [grades, setGrades] = useState<Grade[]>([]);
  const [enrollments, setEnrollments] = useState<Enrollment[]>([]);
  const [pre, setPre] = useState<{ course_id: number; section_id: number }[]>(
    [],
  );
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [filter, setFilter] = useState("");
  const [selected, setSelected] = useState<Record<number, number>>({});
  const [selectedSemester, setSelectedSemester] = useState<number | null>(null);
  const [convalidation, setConvalidation] = useState<Convalidation | null>(null);
  async function refresh() {
    try {
            const [c, g, e, p, conv] = await Promise.all([
        api<Catalog>("/catalog/"),
        api<Grade[]>("/grades/"),
        api<Enrollment[]>("/enrollments/"),
        api<{ course_id: number; section_id: number }[]>("/preselection/"),
        api<Convalidation>("/me/convalidation/").catch(() => null),
      ]);
      setCatalog(c);
      setGrades(g);
      setEnrollments(e);
      setPre(p);
      setConvalidation(conv);
      setSelected(
        Object.fromEntries(p.map((x) => [x.course_id, x.section_id])),
      );
    } catch (e) {
      setError(explain(e));
    }
  }
  useEffect(() => {
    void refresh();
  }, []);
  const sections = catalog?.sections || [];
  const courses = catalog?.courses || [];
  
  const activeElectiveTrack = useMemo(() => {
    const passed = courses.find((c) => c.passed && c.elective_track);
    if (passed) return passed.elective_track;
    const selecting = courses.find((c) => selected[c.id] && c.elective_track);
    return selecting?.elective_track || null;
  }, [courses, selected]);

  const available = useMemo(
    () => courses.filter((c) => sections.some((s) => s.course_id === c.id)),
    [courses, sections],
  );
  const picked = Object.values(selected)
    .map((id) => sections.find((x) => x.id === id))
    .filter((x): x is Section => !!x);
  const credits = picked.reduce(
    (a, s) => a + (courses.find((c) => c.id === s.course_id)?.credits || 0),
    0,
  );
  const conflicts = picked.flatMap((a, i) =>
    picked
      .slice(i + 1)
      .filter((b) => overlap(a, b))
      .map(
        (b) =>
          `${a.course_name} (${a.section}) y ${b.course_name} (${b.section})`,
      ),
  );
  const prerequisites = (c: Course) =>
    c.prerequisites.filter((p) => !courses.find((x) => x.id === p.id)?.passed);
  async function action(kind: "pre" | "enroll") {
    setBusy(true);
    setError("");
    try {
      const ids = picked.map((s) => s.id);
      if (!ids.length) throw Error("Selecciona al menos una sección.");
      if (kind === "enroll" && conflicts.length)
        throw Error("Hay cruces de horario en la selección.");
      if (kind === "pre") {
        await api("/preselection/", "POST", { section_ids: ids });
        inform(
          "Prematrícula guardada. Tus preferencias ayudan a estimar la demanda y no ocupan vacantes.",
        );
      } else {
        const confirmed = await api<{ id: number }>("/enrollments/", "POST", {
          section_ids: ids,
        });
        inform(
          "Matrícula confirmada. La constancia PDF se descargará ahora y seguirá disponible en Inicio.",
        );
        await refresh();
        try {
          await downloadReceipt(confirmed.id, catalog!.period.code);
        } catch {
          setError(
            "Tu matrícula quedó confirmada. Puedes volver a descargar el PDF desde Inicio.",
          );
        }
        return;
      }
      await refresh();
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  if (error && !catalog) return <div className="alert error">{error}</div>;
  if (!catalog)
    return (
      <div className="center">
        <div className="spinner" /> Cargando información...
      </div>
    );
  if (page === "inicio")
    return (
      <>
        <div className="page-head">
          <span className="eyebrow">TU ESPACIO ACADÉMICO</span>
          <h1>
            Hola, {me.name.split(" ")[0]}
          </h1>
          <p>Organiza tu siguiente paso en Ingeniería de Sistemas.</p>
        </div>
        <div className="stat-grid">
          <Stat
            label="PERÍODO ACTUAL"
            value={catalog.period.code}
            note={
              catalog.period.status === "pre"
                ? "Prematrícula abierta"
                : catalog.period.status === "enroll"
                  ? "Matrícula abierta"
                  : "Consulta disponible"
            }
            icon={<CalendarDays />}
          />
          <Stat
            label="CURSOS APROBADOS"
            value={String(courses.filter((c) => c.passed).length)}
            note={`de ${courses.length} cursos en el plan`}
            icon={<BookOpen />}
          />
          <Stat
            label="CRÉDITOS APROBADOS"
            value={String(
              courses
                .filter((c) => c.passed)
                .reduce((a, c) => a + (c.credits || 0), 0),
            )}
            note="Según notas registradas"
            icon={<GraduationCap />}
          />
        </div>
        <div className="columns">
          <div className="panel">
            <div className="panel-head">
              <div>
                <span className="eyebrow">ESTADO ACTUAL</span>
                <h2>Tu matrícula</h2>
              </div>
              <ClipboardList size={23} />
            </div>
            {enrollments.length ? (
              enrollments.map((e) => (
                <div className="enrollment-card" key={e.id}>
                  <div>
                    <strong>Período {e.period}</strong>
                    <p>
                      {e.sections.length} cursos · Confirmada el{" "}
                      {fmt(e.confirmed_at)}
                    </p>
                  </div>
                  <button
                    className="btn outline"
                    onClick={() =>
                      downloadReceipt(e.id, e.period).catch((x) =>
                        setError(explain(x)),
                      )
                    }
                  >
                    <Download size={16} /> Constancia PDF
                  </button>
                </div>
              ))
            ) : (
              <div className="empty">
                <CalendarDays size={35} />
                <strong>Aún no hay matrícula confirmada</strong>
                <p>Explora los cursos disponibles y prepara tu horario.</p>
                <button
                  className="btn primary"
                  onClick={() =>
                    document
                      .querySelector<HTMLButtonElement>(
                        ".sidebar nav button:nth-child(2)",
                      )
                      ?.click()
                  }
                >
                  Explorar matrícula →
                </button>
              </div>
            )}
          </div>
          <div className="panel">
            <div className="panel-head">
              <div>
                <span className="eyebrow">PLANIFICA CON TIEMPO</span>
                <h2>Prematrícula</h2>
              </div>
              <BarChart3 size={23} />
            </div>
            <div className="info-box">
              <strong>{pre.length} preferencias registradas</strong>
              <p>
                Ayudan a estimar cuántas secciones abrir. No reservan vacantes
                ni sustituyen la matrícula.
              </p>
            </div>
            <div className="small-caption">CÓDIGO DE ALUMNO</div>
            <div className="key-value">{me.student_code}</div>
            <div className="small-caption">PLAN DE ESTUDIOS</div>
            <div className="key-value">{me.plan}</div>
          </div>
        </div>
        {enrollments.length > 0 && (
          <Timetable sections={enrollments[0].sections} />
        )}{" "}
        {error && <div className="alert error">{error}</div>}
      </>
    );
  if (page === "matricula" && convalidation && convalidation.active && !convalidation.done) {
    return (
      <div className="center" style={{padding: '40px 20px', alignItems: 'flex-start'}}>
        <div className="panel" style={{maxWidth: '800px', margin: '0 auto', textAlign: 'left', width: '100%'}}>
          <span className="eyebrow" style={{color: '#d32f2f'}}>ACCIN REQUERIDA</span>
          <h1 style={{marginTop: '0.5rem'}}>Proceso de Convalidacin Pendiente</h1>
          <p style={{marginBottom: '2rem'}}>El administrador ha activado tu proceso de convalidacin automtica de cursos (Malla 2010 &#10140; Malla 2019). Por favor revisa la siguiente tabla de equivalencias y confirma para poder continuar con tu matrcula regular.</p>
          
          <h3 style={{marginBottom: '1rem'}}>Cursos Convalidados Exactos (1 a 1)</h3>
          <table className="table" style={{width: '100%', marginBottom: '2rem'}}>
            <thead>
              <tr>
                <th>Curso Aprobado (2010)</th>
                <th>Nota</th>
                <th>Equivalencia (2019)</th>
              </tr>
            </thead>
            <tbody>
              {(convalidation.matches || []).map((m: any, i: number) => (
                <tr key={i}>
                  <td>{m.old_code} - {m.old_name}</td>
                  <td><Badge kind="good">{m.old_grade}</Badge></td>
                  <td><strong>{m.new_code} - {m.new_name}</strong></td>
                </tr>
              ))}
              {(!convalidation.matches || convalidation.matches.length === 0) && (
                <tr><td colSpan={3} style={{textAlign: 'center', padding: '2rem'}}>No tienes cursos exactos aprobados para convalidar.</td></tr>
              )}
            </tbody>
          </table>

          <h3 style={{marginBottom: '1rem'}}>Cursos sin equivalencia exacta</h3>
          <p style={{fontSize: '0.9rem', color: '#666', marginBottom: '1rem'}}>Estos cursos no tienen un par exacto en la malla 2019 y se mantendrn en tu historial sin convalidar.</p>
          <table className="table" style={{width: '100%', marginBottom: '2rem'}}>
            <thead>
              <tr>
                <th>Curso Aprobado (2010)</th>
                <th>Nota</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              {(convalidation.unmatched || []).map((m: any, i: number) => (
                <tr key={i}>
                  <td>{m.old_code} - {m.old_name}</td>
                  <td><Badge kind="good">{m.old_grade}</Badge></td>
                  <td><Badge kind="neutral">Histrico</Badge></td>
                </tr>
              ))}
              {(!convalidation.unmatched || convalidation.unmatched.length === 0) && (
                <tr><td colSpan={3} style={{textAlign: 'center', padding: '2rem'}}>No hay cursos sin equivalencia.</td></tr>
              )}
            </tbody>
          </table>

          <div style={{borderTop: '1px solid #eee', paddingTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem'}}>
             <button disabled={busy} className="btn primary" onClick={async () => {
                 if (confirm("Ests seguro de aceptar esta convalidacin y migrar a la Malla 2019?")) {
                     setBusy(true);
                     try {
                         await api("/me/convalidation/", "POST");
                         inform("Convalidacin exitosa y migracin a Malla 2019 completada.");
                         window.location.reload();
                     } catch (e: any) {
                         alert("Error: " + e.message);
                     } finally {
                         setBusy(false);
                     }
                 }
             }}>{busy ? "Procesando..." : "Confirmar y Migrar a Malla 2019"}</button>
          </div>
        </div>
      </div>
    );
  }

  if (page === "matricula")
    return (
      <>
        {me.plan_active === false && (
          <div className="alert error" style={{ marginBottom: "2rem" }}>
            <strong>⚠️ Acceso Restringido:</strong> Tu plan de estudios actual (Malla 2010) se encuentra inactivo. No puedes participar en el proceso de matrícula hasta que realices tu proceso de convalidación de cursos hacia el plan vigente.
          </div>
        )}
        <div className={`page-head ${me.plan_active === false ? 'disabled-plan' : ''}`}>
          <span className="eyebrow">PERÍODO {catalog.period.code}</span>
          <h1>Planifica tu matrícula</h1>
          <p>
            Compara secciones, docentes, vacantes y horarios antes de enviar tu
            elección.
          </p>
        </div>
        <div className="phase">
          <div className="phase-icon">
            <Clock3 size={20} />
          </div>
          <div>
            <strong>
              {catalog.period.status === "pre"
                ? "Etapa de prematrícula"
                : catalog.period.status === "enroll"
                  ? "Etapa de matrícula"
                  : "Período cerrado"}
            </strong>
            <span>
              {catalog.period.status === "pre"
                ? "Guarda tus preferencias para la planificación de salones. Aún no se reservan vacantes."
                : catalog.period.status === "enroll"
                  ? "Confirma tu elección para reservar las vacantes disponibles."
                  : "El administrador habilitará el siguiente proceso."}
            </span>
          </div>
          <Badge kind={catalog.period.status === "enroll" ? "good" : "blue"}>
            {catalog.period.code}
          </Badge>
        </div>
        <div className="search">
          <Search size={18} />
          <input
            placeholder="Buscar curso o código..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
        <div className="enrollment-layout">
          <div className="course-list">
            {available
              .filter((c) =>
                `${c.name} ${c.code}`
                  .toLocaleLowerCase()
                  .includes(filter.toLocaleLowerCase()),
              )
              .map((c) => {
                const opts = sections.filter((s) => s.course_id === c.id);
                const missing = prerequisites(c);
                const blockedTrack = c.elective_track && activeElectiveTrack && c.elective_track !== activeElectiveTrack;
                return (
                  <div className="course-card" key={c.id}>
                    <div className="course-heading">
                      <div>
                        <span className="code">
                          CICLO MALLA {c.semester} · OFERTA{" "}
                          {Array.from(new Set(opts.map((s) => s.cycle))).join(
                            ", ",
                          )}{" "}
                          · CÓDIGO MALLA {c.code}
                        </span>
                        <h3>{c.name}</h3>
                        <div className="course-meta">
                          <span>{c.credits ?? "?"} créditos</span>
                          <span>
                            Teoría: {c.theory_hours ?? "por validar"} h
                            académicas
                          </span>
                          <span>
                            Práctica: {c.practice_hours ?? "por validar"} h
                            académicas
                          </span>
                        </div>
                      </div>
                      {blockedTrack ? (
                        <Badge kind="warn">Otra mención</Badge>
                      ) : missing.length ? (
                        <Badge kind="warn">Requisito pendiente</Badge>
                      ) : (
                        <Badge kind="good">Disponible</Badge>
                      )}
                    </div>
                    {missing.length > 0 && (
                      <p className="prereq">
                        Requisitos: {missing.map((x) => x.name).join(", ")}
                      </p>
                    )}
                    <div className="options">
                      {opts.map((s) => (
                        <button
                          className={`option ${selected[c.id] === s.id ? "chosen" : ""}`}
                          key={s.id}
                          onClick={() =>
                            setSelected((old) => ({
                              ...old,
                              [c.id]: old[c.id] === s.id ? 0 : s.id,
                            }))
                          }
                          disabled={
                            c.passed ||
                            !!missing.length ||
                            !!blockedTrack ||
                            (catalog.period.status === "enroll" &&
                              s.available === 0)
                          }
                        >
                          <span className="option-radio">
                            {selected[c.id] === s.id ? "✓" : ""}
                          </span>
                          <span className="option-body">
                            <strong>
                              Sección {s.section}{" "}
                              <small>· Salón {s.classroom}</small>
                            </strong>
                            <span>{s.teacher}</span>
                            <span className="meet">
                              {s.meetings
                                .map((m) => `${m.day_name} ${m.start}–${m.end}`)
                                .join(" · ")}
                            </span>
                            <span className="minute">
                              {s.scheduled_minutes} min programados/semana ·
                              Cód. {s.official_code || "pendiente"}
                            </span>
                          </span>
                          <Badge kind={s.available === 0 ? "warn" : "neutral"}>
                            {s.available}/{s.capacity} vacantes
                          </Badge>
                        </button>
                      ))}
                    </div>
                    {opts.length < 2 && (
                      <div className="small-warning">
                        Por ahora hay una opción en el archivo recibido. El
                        administrador puede abrir otra sección.
                      </div>
                    )}
                  </div>
                );
              })}
            {!available.length && (
              <div className="empty">
                No hay secciones publicadas para este período.
              </div>
            )}
          </div>
          <div className="selection">
            <div className="panel sticky">
              <span className="eyebrow">TU SELECCIÓN</span>
              <h2>Horario elegido</h2>
              <p className="muted">
                {picked.length} cursos · {credits} /{" "}
                {catalog.period.max_credits} créditos
              </p>
              {picked.length ? (
                picked.map((s) => (
                  <div className="picked" key={s.id}>
                    <strong>{s.course_name}</strong>
                    <span>
                      {s.section} · {s.teacher}
                    </span>
                    <button
                      aria-label="Quitar sección"
                      onClick={() =>
                        setSelected((old) => ({ ...old, [s.course_id!]: 0 }))
                      }
                    >
                      ×
                    </button>
                  </div>
                ))
              ) : (
                <p className="selection-empty">
                  Selecciona una sección de cada curso para verla aquí.
                </p>
              )}
              {conflicts.length > 0 && (
                <div className="alert error">Cruce: {conflicts.join("; ")}</div>
              )}
              {credits > catalog.period.max_credits && (
                <div className="alert error">
                  Se excede el límite de créditos.
                </div>
              )}
              {error && <div className="alert error">{error}</div>}
              {catalog.period.status === "pre" && (
                <button
                  className="btn primary wide"
                  disabled={busy || !picked.length}
                  onClick={() => void action("pre")}
                >
                  {busy ? "Guardando..." : "Guardar prematrícula →"}
                </button>
              )}
              {catalog.period.status === "enroll" && (
                <button
                  className="btn primary wide"
                  disabled={
                    busy ||
                    !picked.length ||
                    !!conflicts.length ||
                    credits > catalog.period.max_credits ||
                    !!enrollments.find((x) => x.period === catalog.period.code)
                  }
                  onClick={() => void action("enroll")}
                >
                  {busy ? "Confirmando..." : "Confirmar matrícula →"}
                </button>
              )}
              <p className="hint">
                La selección del navegador se guarda en el servidor solo al
                pulsar el botón.
              </p>
            </div>
          </div>
        </div>
      </>
    );
  if (page === "historial")
    return (
      <>
        <div className="page-head">
          <span className="eyebrow">TU TRAYECTORIA</span>
          <h1>Notas e historial académico</h1>
          <p>
            Resultados registrados por período, con sus créditos y condición de
            aprobación.
          </p>
        </div>
        <div className="historial-list" style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          {grades.length > 0 && (() => {
            const semesters = Array.from(new Set(grades.map((g) => g.semester))).sort((a, b) => a - b);
            const activeSem = selectedSemester || Math.max(...semesters);
            const semGrades = grades.filter((g) => g.semester === activeSem);
            return (
              <>
                <div style={{ display: 'flex', gap: '10px', overflowX: 'auto', paddingBottom: '10px' }}>
                  {semesters.map((sem) => (
                    <button
                      key={sem}
                      className={`btn ${activeSem === sem ? 'primary' : 'outline'}`}
                      onClick={() => setSelectedSemester(sem)}
                      style={{ borderRadius: '20px', whiteSpace: 'nowrap' }}
                    >
                      Ciclo {sem}
                    </button>
                  ))}
                </div>
                <div className="panel table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Código malla</th>
                        <th>Curso</th>
                        <th>Período</th>
                        <th>Créditos</th>
                        <th>Nota final</th>
                        <th>Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      {semGrades.map((g, i) => (
                        <tr key={i}>
                          <td className="code">{g.code}</td>
                          <td>
                            <strong>{g.course}</strong>
                          </td>
                          <td>{g.period === "HISTORICO" ? `Ciclo ${["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"][g.semester - 1] || g.semester}` : g.period}</td>
                          <td>{g.credits ?? "—"}</td>
                          <td>
                            <strong>{g.score.toFixed(1)}</strong>
                          </td>
                          <td>
                            <Badge kind={g.passed ? "good" : "warn"}>
                              {g.passed ? "Aprobado" : "No aprobado"}
                            </Badge>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            );
          })()}
          {!grades.length && (
            <div className="empty panel">Todavía no hay notas registradas.</div>
          )}
        </div>
      </>
    );
  return (
    <>
      <div className="page-head">
        <span className="eyebrow">PLAN DE ESTUDIOS</span>
        <h1>Mi malla curricular</h1>
        <p>Consulta asignaturas, créditos y prerrequisitos de tu plan.</p>
      </div>

      {me.plan_active === false && (
        <div className="alert error">
          <strong>⚠️ Malla Inactiva:</strong> Tu plan de estudios ya no se encuentra vigente. Por favor, realiza el proceso de convalidación para reactivar tu matrícula.
        </div>
      )}

      <div className={`semester-grid ${me.plan_active === false ? 'disabled-plan' : ''}`}>
        {Array.from(new Set(courses.map((c) => c.semester))).map((sem) => (
          <section className="panel semester" key={sem}>
            <div className="semester-top">
              <span className="eyebrow">CICLO {sem}</span>
              <strong>
                {courses
                  .filter((c) => c.semester === sem)
                  .reduce((a, c) => a + (c.credits || 0), 0)}{" "}
                créditos conocidos
              </strong>
            </div>
            {courses
              .filter((c) => c.semester === sem)
              .map((c) => (
                <div className="semester-course" key={c.id}>
                  <div>
                    <span className="code">{c.code}</span>
                    <strong>{c.name}</strong>
                    {c.prerequisites.length > 0 && (
                      <small>
                        Requiere {c.prerequisites.map((p) => p.code).join(", ")}
                      </small>
                    )}
                  </div>
                  {c.passed ? (
                    <span className="check">✓</span>
                  ) : (
                    <span className="pending">○</span>
                  )}
                </div>
              ))}
          </section>
        ))}
      </div>
    </>
  );
}

function Stat({
  label,
  value,
  note,
  icon,
}: {
  label: string;
  value: string;
  note: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="stat">
      <span className="stat-icon">{icon}</span>
      <div className="eyebrow">{label}</div>
      <strong>{value}</strong>
      <small>{note}</small>
    </div>
  );
}

function ProfilePage({
  me,
  inform,
  reloadMe,
}: {
  me: Identity;
  inform: (s: string) => void;
  reloadMe: () => Promise<unknown>;
}) {
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  async function upload(file: File) {
    setError("");
    setBusy(true);
    try {
      await changePhoto(file);
      await reloadMe();
      inform("Foto de perfil actualizada.");
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  async function remove() {
    setError("");
    setBusy(true);
    try {
      await changePhoto();
      await reloadMe();
      inform("Foto de perfil eliminada.");
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="page-head">
        <span className="eyebrow">CUENTA PERSONAL</span>
        <h1>Mi perfil</h1>
        <p>
          Personaliza la foto que aparece junto a tu nombre. Solo tú puedes
          consultar y cambiar tu imagen.
        </p>
      </div>
      <div className="panel profile-card">
        <span className="avatar profile-avatar">
          {me.has_photo ? (
            <img
              src={`/api/profile/photo/?v=${encodeURIComponent(me.photo_version || "")}`}
              alt="Mi foto"
            />
          ) : (
            me.name.slice(0, 1)
          )}
        </span>
        <div>
          <h2>{me.name}</h2>
          <p>
            {me.role === "teacher"
              ? "Docente"
              : me.role === "admin"
                ? "Personal administrativo"
                : "Alumno"}{" "}
            · Usuario {me.username}
          </p>
          {me.student_code && <p>Código: {me.student_code}</p>}
          <label className="btn primary photo-input">
            <Camera size={16} />
            {busy ? "Guardando..." : "Subir foto"}
            <input
              type="file"
              accept="image/jpeg,image/png,image/webp"
              disabled={busy}
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) void upload(file);
                e.target.value = "";
              }}
            />
          </label>
          {me.has_photo && (
            <button
              className="btn outline"
              disabled={busy}
              onClick={() => void remove()}
            >
              Eliminar foto
            </button>
          )}
          <p className="hint">
            JPEG, PNG o WebP · máximo 2 MB · el servidor adapta la imagen a 512
            px.
          </p>
        </div>
      </div>
      {error && <div className="alert error">{error}</div>}
    </>
  );
}

function TeacherPage({ page, period }: { page: Page; period: string }) {
  const [data, setData] = useState<TeacherData | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    if (!period) return;
    setData(null);
    api<TeacherData>(`/teacher/sections/?period=${encodeURIComponent(period)}`)
      .then(setData)
      .catch((e) => setError(explain(e)));
  }, [period]);
  async function download(sectionId?: number) {
    setBusy(true);
    setError("");
    try {
      await downloadTeacherReport(period, sectionId);
    } catch (e) {
      setError(explain(e));
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <div className="page-head">
        <span className="eyebrow">
          DOCENCIA · PERÍODO {period || "SIN PERÍODO"}
        </span>
        <h1>
          {page === "inicio" ? "Mi actividad docente" : "Mis cursos y alumnos"}
        </h1>
        <p>
          Consulta las secciones asignadas, las sesiones y únicamente los
          alumnos que confirmaron su matrícula.
        </p>
      </div>
      {data && (
        <>
          <div className="stat-grid">
            <Stat
              label="SECCIONES"
              value={String(data.sections.length)}
              note="Asignadas en este período"
              icon={<BookOpen />}
            />
            <Stat
              label="ALUMNOS"
              value={String(
                data.sections.reduce((n, s) => n + s.students.length, 0),
              )}
              note="Matrículas en mis secciones"
              icon={<Users />}
            />
            <Stat
              label="PERÍODO"
              value={data.period}
              note="Carga horaria"
              icon={<CalendarDays />}
            />
          </div>
          <div className="teacher-actions">
            <button
              className="btn primary"
              disabled={busy}
              onClick={() => void download()}
            >
              <Download size={16} /> Exportar horario y alumnos en PDF
            </button>
          </div>
          {data.sections.map((s) => (
            <section className="panel teacher-section" key={s.id}>
              <div className="row-between">
                <div>
                  <span className="eyebrow">
                    {s.official_code || "CÓDIGO PENDIENTE"} · SECCIÓN{" "}
                    {s.section}
                  </span>
                  <h2>{s.course_name}</h2>
                  <p>
                    Salón {s.classroom} · {s.students.length} alumnos
                    matriculados
                  </p>
                </div>
                <button
                  className="btn outline"
                  disabled={busy}
                  onClick={() => void download(s.id)}
                >
                  <Download size={15} /> PDF
                </button>
              </div>
              <div className="teacher-meetings">
                {s.meetings.map((m, i) => (
                  <Badge key={i} kind="blue">
                    {m.day_name} {m.start}–{m.end}
                  </Badge>
                ))}
              </div>
              <div className="table-wrap inner">
                <table>
                  <thead>
                    <tr>
                      <th>Código del alumno</th>
                      <th>Nombre</th>
                    </tr>
                  </thead>
                  <tbody>
                    {s.students.map((student) => (
                      <tr key={student.code}>
                        <td>{student.code}</td>
                        <td>
                          <strong>{student.name}</strong>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {!s.students.length && (
                  <div className="empty">
                    Todavía no hay matrículas confirmadas en esta sección.
                  </div>
                )}
              </div>
            </section>
          ))}
          {!data.sections.length && (
            <div className="panel empty">
              No hay cursos asignados para el período actual.
            </div>
          )}
        </>
      )}
      {!data && !error && (
        <div className="center">Cargando clases y alumnos...</div>
      )}
      {error && <div className="alert error">{error}</div>}
    </>
  );
}

function AdminPage({
  page,
  inform,
  reloadMe,
}: {
  page: Page;
  inform: (s: string) => void;
  reloadMe: () => Promise<unknown>;
}) {
  const [data, setData] = useState<AdminData | null>(null);
  const [demand, setDemand] = useState<Demand | null>(null);
  const [audit, setAudit] = useState<
    {
      actor: string;
      action: string;
      target: string;
      created_at: string;
      detail: unknown;
    }[]
  >([]);
  const [error, setError] = useState("");
  const [courseSearch, setCourseSearch] = useState("");
  const [sectionSearch, setSectionSearch] = useState("");
  const [link, setLink] = useState<Record<number, number>>({});
  async function refresh() {
    try {
      const d = await api<AdminData>("/admin/data/");
      setData(d);
      const [dm, logs] = await Promise.all([
        api<Demand>("/admin/demand/").catch(() => null),
        api<typeof audit>("/admin/audit/"),
      ]);
      setDemand(dm);
      setAudit(logs);
    } catch (e) {
      setError(explain(e));
    }
  }
  useEffect(() => {
    void refresh();
  }, []);
  async function submit(
    path: string,
    method: string,
    body: unknown,
    success: string,
  ) {
    setError("");
    try {
      await api(path, method, body);
      inform(success);
      await refresh();
      await reloadMe();
    } catch (e) {
      setError(explain(e));
    }
  }
  if (!data)
    return error ? (
      <div className="alert error">{error}</div>
    ) : (
      <div className="center">
        <div className="spinner" /> Cargando administración...
      </div>
    );
  const current = data.periods.find((p) => p.is_current);
  return (
    <>
      <div className="page-head">
        <span className="eyebrow">GESTIÓN FIIS</span>
        <h1>
          {(
            {
              inicio: "Panel de administración",
              admin: "Configuración académica",
              oferta: "Oferta académica",
              demanda: "Demanda de prematrícula",
              alumnos: "Alumnos y notas",
              auditoria: "Registro de auditoría",
            } as Record<string, string>
          )[page] || "Administración"}
        </h1>
        <p>
          Gestiona la oferta, el plan curricular y las etapas de matrícula de
          Ingeniería de Sistemas.
        </p>
      </div>
      {error && (
        <div className="alert error">
          <AlertCircle size={17} />
          {error}
          <button onClick={() => setError("")}>×</button>
        </div>
      )}
      {page === "inicio" && (
        <>

          <div className="stat-grid">
            <Stat
              label="PERÍODO ACTUAL"
              value={current?.code || "—"}
              note={`Estado: ${current?.status || "sin configurar"}`}
              icon={<CalendarDays />}
            />
            <Stat
              label="ESTUDIANTES"
              value={String(data.students.length)}
              note="Registrados en el sistema"
              icon={<Users />}
            />
            <Stat
              label="SECCIONES PUBLICADAS"
              value={String(
                data.sections.filter(
                  (s) => s.period === current?.code && s.published,
                ).length,
              )}
              note="Oferta del período actual"
              icon={<BookOpen />}
            />
          </div>
          <div className="columns">
            <div className="panel">
              <span className="eyebrow">ESTADO MATRÍCULA</span>
              <h2>Alumnos matriculados</h2>
              <p>
                Total de alumnos que han concretado su matrícula anual 2027-I y II.
              </p>
              <div className="big-metric">
                {data.students.length}
                <span> alumnos matriculados</span>
              </div>
            </div>
            <div className="panel">
              <span className="eyebrow">DATOS ACADÉMICOS</span>
              <h2>Revisión de importación</h2>
              <p>
                Revisa créditos y equivalencias antes de publicar las secciones
                pendientes.
              </p>
              <div className="big-metric">
                {data.sections.filter((s) => s.review_required).length}
                <span> secciones por revisar</span>
              </div>
            </div>
          </div>
        </>
      )}
      {page === "admin" && (() => {
        const currentPeriod = data.periods.find(p => p.is_current);
        return (
        <div className="panel spaced">
          <span className="eyebrow">CENTRO DE CONTROL DE MATRÍCULA</span>
          <h2>Apertura Anual 2027</h2>
          <p>
            Desde aquí podrás habilitar la fase previa de revisión de horarios y la matrícula oficial anual para los ciclos 2027-I y 2027-II.
          </p>
          
          <div style={{ display: 'flex', gap: '20px', marginTop: '20px', flexWrap: 'wrap' }}>
            
            <div className="panel" style={{ flex: 1, minWidth: '300px', border: '1px solid var(--border)', background: 'var(--surface)' }}>
              <h3>Fase 0: Migración y Convalidación</h3>
              <p style={{marginBottom: '15px', color: 'var(--text-soft)'}}>Activa el proceso de convalidación obligatoria para los alumnos rezagados de la Malla 2010.</p>
              {currentPeriod && (
                <label style={{display: 'flex', alignItems: 'center', gap: '10px', fontWeight: 'bold', cursor: 'pointer', padding: '10px', background: 'var(--surface-hover)', borderRadius: '8px'}}>
                  <input
                    type="checkbox"
                    style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                    checked={currentPeriod.convalidation_active || false}
                    onChange={(e) =>
                      void submit(
                        `/admin/periods/${currentPeriod.id}/`,
                        "PATCH",
                        { convalidation_active: e.target.checked },
                        "Convalidación " + (e.target.checked ? "activada" : "desactivada"),
                      )
                    }
                  />
                  Habilitar Convalidación 2010
                </label>
              )}
            </div>

            <div className="panel" style={{ flex: 1, minWidth: '300px', border: '1px solid var(--border)', background: 'var(--surface)' }}>
              <h3>Fase 1: Pre-Matrícula</h3>
              <p style={{marginBottom: '15px', color: 'var(--text-soft)'}}>Habilita la vista de cursos y horarios. Los alumnos podrán armar su horario sin poder matricularse aún.</p>
              <button 
                className="btn outline"
                onClick={() => alert("Función en desarrollo: Esto activará la pestaña de horarios y cruces para los alumnos.")}
              >
                Habilitar Vista de Horarios
              </button>
            </div>
            
            <div className="panel" style={{ flex: 1, minWidth: '300px', border: '1px solid var(--border)', background: 'var(--surface)' }}>
              <h3>Fase 2: Matrícula Oficial</h3>
              <p style={{marginBottom: '15px', color: 'var(--text-soft)'}}>Abre la matrícula oficial 2027-I y II. Los alumnos podrán confirmar su selección según su orden de mérito.</p>
              <button 
                className="btn primary"
                onClick={() => alert("Función en desarrollo: Esto cambiará el estado de la plataforma a ENROLL para ambos ciclos.")}
              >
                Aperturar Matrícula 2027-I y II
              </button>
            </div>
          </div>

          <div style={{ marginTop: '40px' }} className="panel">
            <span className="eyebrow">PREPARATIVOS FUTUROS</span>
            <h2>Adjuntar nueva malla curricular</h2>
            <p style={{ color: 'var(--text-soft)', marginBottom: '15px' }}>
              Utiliza esta opción únicamente cuando se apruebe y publique oficialmente un nuevo plan de estudios (ej. Malla 2030).
            </p>
            
            <label style={{ display: 'inline-block', padding: '30px 20px', background: 'var(--surface)', border: '2px dashed var(--border)', borderRadius: '12px', cursor: 'not-allowed', color: 'var(--text-soft)', textAlign: 'center', width: '100%', maxWidth: '400px', opacity: 0.7 }}>
              <span style={{ display: 'block', fontSize: '1.5rem', marginBottom: '8px' }}>📁</span>
              <strong style={{ display: 'block', fontSize: '1.1rem', marginBottom: '4px' }}>Seleccionar archivo JSON</strong>
              <small>Arrastra tu archivo aquí o haz clic para explorar</small>
              <input type="file" disabled style={{ display: 'none' }} />
            </label>
            
            <br />
            <button className="btn outline" disabled style={{ marginTop: '15px' }}>
              Subir y Procesar Malla
            </button>
          </div>
        </div>
        );
      })()}
      {page === "oferta" && (
        <>
          <div className="panel spaced">
            <span className="eyebrow">PROGRAMACIÓN</span>
            <h2>Abrir una nueva sección</h2>
            <p>
              Agrega una alternativa de profesor, horario y salón para un curso.
            </p>
            <NewSection data={data} submit={submit} />
            <NewTeacher teachers={data.teachers} submit={submit} />
          </div>
          <div className="panel">
            <div className="row-between">
              <div>
                <span className="eyebrow">SECCIONES CARGADAS</span>
                <h2>Oferta y equivalencias</h2>
              </div>
              <input
                className="search-short"
                placeholder="Buscar curso, docente..."
                value={sectionSearch}
                onChange={(e) => setSectionSearch(e.target.value)}
              />
            </div>
            <div className="table-wrap inner">
              <table>
                <thead>
                  <tr>
                    <th>Curso y período</th>
                    <th>Sección / salón</th>
                    <th>Docente y sesiones</th>
                    <th>Vacantes</th>
                    <th>Estado / acción</th>
                  </tr>
                </thead>
                <tbody>
                  {data.sections
                    .filter((s) =>
                      `${s.course_name} ${s.teacher} ${s.period}`
                        .toLowerCase()
                        .includes(sectionSearch.toLowerCase()),
                    )
                    .slice(0, 80)
                    .map((s) => (
                      <tr key={s.id}>
                        <td>
                          <strong>{s.course_name}</strong>
                          <small>
                            {s.period} · {s.official_code || "Código pendiente"}
                          </small>
                        </td>
                        <td>
                          {s.section} / {s.classroom}
                        </td>
                        <td>
                          <select
                            aria-label={`Docente de ${s.course_name}`}
                            value={s.teacher_id || ""}
                            onChange={(e) =>
                              void submit(
                                `/admin/sections/${s.id}/`,
                                "PATCH",
                                { teacher_id: Number(e.target.value) },
                                "Docente asignado; el horario fue validado",
                              )
                            }
                          >
                            <option value="" disabled>
                              Asignar docente...
                            </option>
                            {data.teachers
                              .filter((t) => t.active)
                              .map((t) => (
                                <option key={t.id} value={t.id}>
                                  {t.name}
                                </option>
                              ))}
                          </select>
                          <small>
                            {s.meetings
                              .map((m) => `${m.day_name} ${m.start}-${m.end}`)
                              .join(" · ")}
                          </small>
                        </td>
                        <td>
                          {s.available}/{s.capacity}
                          <div className="capacity-edit">
                            <input
                              type="number"
                              min="1"
                              defaultValue={s.capacity}
                              id={`capacity-${s.id}`}
                            />
                            <button
                              onClick={() =>
                                void submit(
                                  `/admin/sections/${s.id}/`,
                                  "PATCH",
                                  {
                                    capacity: Number(
                                      (
                                        document.getElementById(
                                          `capacity-${s.id}`,
                                        ) as HTMLInputElement
                                      ).value,
                                    ),
                                  },
                                  "Vacantes actualizadas",
                                )
                              }
                            >
                              Guardar
                            </button>
                          </div>
                        </td>
                        <td>
                          {s.review_required ? (
                            <>
                              <Badge kind="warn">Revisar vínculo</Badge>
                              <div className="inline-edit">
                                <select
                                  value={link[s.id] || ""}
                                  onChange={(e) =>
                                    setLink({
                                      ...link,
                                      [s.id]: Number(e.target.value),
                                    })
                                  }
                                >
                                  <option value="">Vincular curso...</option>
                                  {data.courses
                                    .filter(
                                      (c) =>
                                        !s.cycle ||
                                        String(c.semester) ===
                                          String(
                                            (
                                              {
                                                I: 1,
                                                II: 2,
                                                III: 3,
                                                IV: 4,
                                                V: 5,
                                                VI: 6,
                                                VII: 7,
                                                VIII: 8,
                                                IX: 9,
                                                X: 10,
                                              } as Record<string, number>
                                            )[s.cycle],
                                          ),
                                    )
                                    .map((c) => (
                                      <option key={c.id} value={c.id}>
                                        {c.code} · {c.name}
                                      </option>
                                    ))}
                                </select>
                                <button
                                  onClick={() =>
                                    void submit(
                                      `/admin/sections/${s.id}/`,
                                      "PATCH",
                                      { course_id: link[s.id] },
                                      "Sección vinculada; revisa créditos y publícala",
                                    )
                                  }
                                >
                                  Vincular
                                </button>
                              </div>
                            </>
                          ) : (
                            <button
                              className="btn small"
                              onClick={() =>
                                void submit(
                                  `/admin/sections/${s.id}/`,
                                  "PATCH",
                                  { published: !s.published },
                                  "Publicación actualizada",
                                )
                              }
                            >
                              {s.published ? "Publicada ✓" : "Publicar"}
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
            <p className="hint">
              Se muestran hasta 80 filas por búsqueda. Puedes filtrar por
              período, curso o docente.
            </p>
          </div>
        </>
      )}
      {page === "demanda" && (
        <>
          <div className="panel">
            <div className="row-between">
              <div>
                <span className="eyebrow">PLANIFICACIÓN DE SECCIONES</span>
                <h2>Reporte de demanda · {demand?.period || "—"}</h2>
              </div>
              <Badge kind="blue">{demand?.total_students || 0} alumnos</Badge>
            </div>
            <p>
              Secciones sugeridas = alumnos interesados ÷ capacidad supuesta (
              {demand?.capacity_assumption || 35}), redondeado hacia arriba.
              Cada alumno cuenta una sola vez por curso.
            </p>
            <div className="table-wrap inner">
              <table>
                <thead>
                  <tr>
                    <th>Curso</th>
                    <th>Alumnos interesados</th>
                    <th>Secciones sugeridas</th>
                    <th>Preferencias de horario</th>
                  </tr>
                </thead>
                <tbody>
                  {demand?.courses.map((c) => (
                    <tr key={c.course_id}>
                      <td>
                        <strong>{c.course}</strong>
                        <small>Malla {c.code}</small>
                      </td>
                      <td>{c.students}</td>
                      <td>
                        <Badge kind="blue">{c.suggested_sections}</Badge>
                      </td>
                      <td>
                        {c.preferences
                          .map((p) => `${p.section}: ${p.students}`)
                          .join(" · ")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {!demand?.courses.length && (
                <div className="empty">
                  Aún no se registraron preferencias de prematrícula.
                </div>
              )}
            </div>
          </div>
        </>
      )}
      {page === "alumnos" && (
        <>
          <div className="columns">
            <div className="panel">
              <span className="eyebrow">ALTA</span>
              <h2>Nuevo alumno</h2>
              <NewStudent plans={data.plans} submit={submit} />
            </div>
            <div className="panel">
              <span className="eyebrow">CALIFICACIONES</span>
              <h2>Registrar o rectificar nota</h2>
              <p>
                La nota final se registra por alumno, curso y período; cada
                cambio queda auditado.
              </p>
              <NewGrade data={data} submit={submit} />
            </div>
          </div>
          <div className="panel spaced">
            <h2>Alumnos registrados</h2>
            <div className="table-wrap inner">
              <table>
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Nombre</th>
                    <th>Plan</th>
                    <th>Estado</th>
                    <th>Administrar cuenta</th>
                  </tr>
                </thead>
                <tbody>
                  {data.students.map((s) => (
                    <tr key={s.id}>
                      <td>{s.student_code}</td>
                      <td>{s.full_name}</td>
                      <td>{s.plan__name}</td>
                      <td>
                        <Badge kind={s.active ? "good" : "warn"}>
                          {s.active ? "Activo" : "Inactivo"}
                        </Badge>
                      </td>
                      <td>
                        <small>{s.email}</small>
                        {s.activation_pending && (
                          <Badge kind="warn">Pendiente de activación</Badge>
                        )}
                        <div className="account-actions">
                          <button
                            onClick={() => {
                              const name = window.prompt(
                                "Nombre completo",
                                s.full_name,
                              );
                              if (name)
                                void submit(
                                  `/admin/students/${s.id}/`,
                                  "PATCH",
                                  { full_name: name },
                                  "Nombre actualizado",
                                );
                            }}
                          >
                            Editar
                          </button>
                          <button
                            onClick={() =>
                              void submit(
                                `/admin/students/${s.id}/`,
                                "PATCH",
                                { active: !s.active },
                                s.active
                                  ? "Cuenta suspendida"
                                  : "Cuenta reactivada",
                              )
                            }
                          >
                            {s.active ? "Suspender" : "Reactivar"}
                          </button>
                          <button
                            onClick={() => {
                              const password = window.prompt(
                                "Contraseña temporal (mínimo 12 caracteres)",
                              );
                              if (password)
                                void submit(
                                  `/admin/students/${s.id}/`,
                                  "PATCH",
                                  { temporary_password: password },
                                  "Contraseña temporal creada",
                                );
                            }}
                          >
                            Restablecer clave
                          </button>
                          <button
                            disabled={s.activation_pending}
                            onClick={() => {
                              if (
                                window.confirm(
                                  `¿Habilitar la activación para ${s.full_name}? Su contraseña actual dejará de funcionar.`,
                                )
                              )
                                void submit(
                                  `/admin/students/${s.id}/`,
                                  "PATCH",
                                  { enable_activation: true },
                                  "Activación habilitada; el alumno ya puede crear su cuenta",
                                );
                            }}
                          >
                            {s.activation_pending
                              ? "Activación pendiente"
                              : "Habilitar activación"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
      {page === "auditoria" && (
        <div className="panel">
          <p>Últimos 100 cambios efectuados desde el portal.</p>
          <div className="table-wrap inner">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Usuario</th>
                  <th>Acción</th>
                  <th>Registro</th>
                </tr>
              </thead>
              <tbody>
                {audit.map((a, i) => (
                  <tr key={i}>
                    <td>{new Date(a.created_at).toLocaleString("es-PE")}</td>
                    <td>{a.actor}</td>
                    <td>{a.action}</td>
                    <td>{a.target}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </>
  );
}

function NewPeriod({
  submit,
}: {
  submit: (p: string, m: string, b: unknown, s: string) => Promise<void>;
}) {
  const [code, setCode] = useState("");
  return (
    <form
      className="simple-form"
      onSubmit={(e) => {
        e.preventDefault();
        void submit("/admin/periods/", "POST", { code }, "Período creado");
        setCode("");
      }}
    >
      <input
        value={code}
        onChange={(e) => setCode(e.target.value)}
        placeholder="Ej.: 2027-1"
        required
      />
      <button className="btn primary">Crear período</button>
    </form>
  );
}
function CourseEditor({
  course,
  courses,
  onSave,
}: {
  course: Course;
  courses: Course[];
  onSave: (b: unknown) => Promise<void>;
}) {
  const [theory, setTheory] = useState(course.theory_hours?.toString() || "");
  const [practice, setPractice] = useState(
    course.practice_hours?.toString() || "",
  );
  const [credits, setCredits] = useState(course.credits?.toString() || "");
  const [req, setReq] = useState(
    course.prerequisites.map((p) => p.code).join(", "),
  );
  const [name, setName] = useState(course.name);
  return (
    <div className="editor">
      <div>
        <strong>
          {course.code} · {course.name}
        </strong>
        <small>
          {course.plan_name} · Ciclo {course.semester} · Requisitos:{" "}
          {course.prerequisites.map((p) => p.code).join(", ") || "ninguno"}
        </small>
        <Badge kind={course.academic_data_verified ? "good" : "warn"}>
          {course.academic_data_verified
            ? "Datos verificados"
            : "Pendiente de validación académica"}
        </Badge>
      </div>
      <div className="editor-fields">
        <label>
          Nombre
          <input value={name} onChange={(e) => setName(e.target.value)} />
        </label>
        <label>
          Créditos
          <input
            type="number"
            min="1"
            value={credits}
            onChange={(e) => setCredits(e.target.value)}
          />
        </label>
        <label>
          Teoría
          <input
            type="number"
            min="0"
            value={theory}
            onChange={(e) => setTheory(e.target.value)}
          />
        </label>
        <label>
          Práctica
          <input
            type="number"
            min="0"
            value={practice}
            onChange={(e) => setPractice(e.target.value)}
          />
        </label>
        <button
          onClick={() => {
            const codes = req
              .split(",")
              .map((x) => x.trim())
              .filter(Boolean);
            const found = codes.map((code) =>
              courses.find(
                (x) => x.code === code && x.plan_id === course.plan_id,
              ),
            );
            if (found.some((x) => !x)) {
              alert("Revisa los códigos de prerrequisitos");
              return;
            }
            void onSave({
              name,
              credits: credits ? Number(credits) : null,
              theory_hours: theory ? Number(theory) : null,
              practice_hours: practice ? Number(practice) : null,
              prerequisite_ids: found.map((x) => x!.id),
              academic_data_verified: Boolean(
                credits && theory !== "" && practice !== "",
              ),
            });
          }}
        >
          Guardar
        </button>
      </div>
      <label className="req-field">
        Prerrequisitos (códigos separados por coma)
        <input
          value={req}
          onChange={(e) => setReq(e.target.value)}
          placeholder="Ej.: 01, 08"
        />
      </label>
    </div>
  );
}
function NewCourse({
  plans,
  submit,
}: {
  plans: AdminData["plans"];
  submit: (p: string, m: string, b: unknown, s: string) => Promise<void>;
}) {
  const [plan, setPlan] = useState(plans[0]?.id || 0);
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [semester, setSemester] = useState(1);
  const [credits, setCredits] = useState(3);
  return (
    <form
      className="grid-form"
      onSubmit={(e) => {
        e.preventDefault();
        void submit(
          "/admin/courses/",
          "POST",
          { plan_id: plan, curricular_code: code, name, semester, credits },
          "Curso creado",
        );
        setCode("");
        setName("");
      }}
    >
      <label>
        Plan
        <select value={plan} onChange={(e) => setPlan(Number(e.target.value))}>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Código
        <input
          required
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
      </label>
      <label>
        Nombre
        <input
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </label>
      <label>
        Ciclo
        <input
          type="number"
          min="1"
          max="10"
          value={semester}
          onChange={(e) => setSemester(Number(e.target.value))}
        />
      </label>
      <label>
        Créditos
        <input
          type="number"
          min="1"
          value={credits}
          onChange={(e) => setCredits(Number(e.target.value))}
        />
      </label>
      <button className="btn primary">Crear curso</button>
    </form>
  );
}
function NewSection({
  data,
  submit,
}: {
  data: AdminData;
  submit: (p: string, m: string, b: unknown, s: string) => Promise<void>;
}) {
  const [period, setPeriod] = useState(
    data.periods.find((p) => p.is_current)?.id || 0,
  );
  const [course, setCourse] = useState(data.courses[0]?.id || 0);
  const [section, setSection] = useState("");
  const [teacher, setTeacher] = useState(0);
  const [classroom, setClassroom] = useState("");
  const [official, setOfficial] = useState("");
  const [capacity, setCapacity] = useState(35);
  const [meetings, setMeetings] = useState([
    { day: 0, start: "08:00", end: "09:40" },
  ]);
  function update(i: number, key: "day" | "start" | "end", value: string) {
    setMeetings((old) =>
      old.map((m, j) =>
        j === i ? { ...m, [key]: key === "day" ? Number(value) : value } : m,
      ),
    );
  }
  return (
    <form
      className="grid-form"
      onSubmit={(e) => {
        e.preventDefault();
        void submit(
          "/admin/sections/",
          "POST",
          {
            period_id: period,
            course_id: course,
            section,
            teacher_id: teacher || null,
            classroom,
            official_code: official,
            capacity,
            meetings,
          },
          "Sección creada como borrador. Revísala y publícala.",
        );
        setSection("");
      }}
    >
      <label>
        Período
        <select
          value={period}
          onChange={(e) => setPeriod(Number(e.target.value))}
        >
          {data.periods.map((p) => (
            <option key={p.id} value={p.id}>
              {p.code}
            </option>
          ))}
        </select>
      </label>
      <label>
        Curso
        <select
          value={course}
          onChange={(e) => setCourse(Number(e.target.value))}
        >
          {data.courses.map((c) => (
            <option key={c.id} value={c.id}>
              {c.code} · {c.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Sección
        <input
          required
          placeholder="Ej.: MD"
          value={section}
          onChange={(e) => setSection(e.target.value)}
        />
      </label>
      <label>
        Docente
        <select
          value={teacher}
          onChange={(e) => setTeacher(Number(e.target.value))}
        >
          <option value={0}>Por asignar</option>
          {data.teachers.map((t) => (
            <option value={t.id} key={t.id}>
              {t.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Salón
        <input
          placeholder="Ej.: B-504"
          value={classroom}
          onChange={(e) => setClassroom(e.target.value)}
        />
      </label>
      <label>
        Código oficial
        <input
          placeholder="Ej.: 100382"
          value={official}
          onChange={(e) => setOfficial(e.target.value)}
        />
      </label>
      <label>
        Vacantes
        <input
          type="number"
          min="1"
          value={capacity}
          onChange={(e) => setCapacity(Number(e.target.value))}
        />
      </label>
      <div className="meeting-editor">
        <strong>Sesiones semanales</strong>
        {meetings.map((m, i) => (
          <div className="meeting-row" key={i}>
            <select
              value={m.day}
              onChange={(e) => update(i, "day", e.target.value)}
            >
              {days.map((d, n) => (
                <option key={d} value={n}>
                  {d}
                </option>
              ))}
            </select>
            <input
              type="time"
              value={m.start}
              onChange={(e) => update(i, "start", e.target.value)}
            />
            <input
              type="time"
              value={m.end}
              onChange={(e) => update(i, "end", e.target.value)}
            />
            {meetings.length > 1 && (
              <button
                type="button"
                onClick={() =>
                  setMeetings((old) => old.filter((_, j) => j !== i))
                }
              >
                ×
              </button>
            )}
          </div>
        ))}
        <button
          className="add-meeting"
          type="button"
          onClick={() =>
            setMeetings((old) => [
              ...old,
              { day: 1, start: "08:00", end: "09:40" },
            ])
          }
        >
          + Agregar sesión
        </button>
      </div>
      <button className="btn primary">Crear sección</button>
    </form>
  );
}
function NewStudent({
  plans,
  submit,
}: {
  plans: AdminData["plans"];
  submit: (p: string, m: string, b: unknown, s: string) => Promise<void>;
}) {
  const [code, setCode] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [plan, setPlan] = useState(plans[0]?.id || 0);
  return (
    <form
      className="stack-form"
      onSubmit={(e) => {
        e.preventDefault();
        void submit(
          "/admin/students/",
          "POST",
          {
            student_code: code,
            full_name: name,
            email,
            password,
            plan_id: plan,
          },
          password
            ? "Alumno registrado con cambio de clave obligatorio"
            : "Alumno creado; ya puede activar su cuenta",
        );
        setCode("");
        setName("");
        setEmail("");
        setPassword("");
      }}
    >
      <label>
        Código
        <input
          required
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
      </label>
      <label>
        Nombres y apellidos
        <input
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </label>
      <label>
        Correo institucional
        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>
      <label>
        Contraseña inicial (opcional)
        <input
          type="password"
          minLength={12}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      <small>
        Si queda vacía, el alumno activará su cuenta con código, correo y nombre
        completo.
      </small>
      <label>
        Plan
        <select value={plan} onChange={(e) => setPlan(Number(e.target.value))}>
          {plans.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </label>
      <button className="btn primary">Registrar alumno</button>
    </form>
  );
}
function NewGrade({
  data,
  submit,
}: {
  data: AdminData;
  submit: (p: string, m: string, b: unknown, s: string) => Promise<void>;
}) {
  const [student, setStudent] = useState(data.students[0]?.id || 0);
  const [course, setCourse] = useState(data.courses[0]?.id || 0);
  const [period, setPeriod] = useState(data.periods[0]?.id || 0);
  const [score, setScore] = useState("");
  return (
    <form
      className="stack-form"
      onSubmit={(e) => {
        e.preventDefault();
        void submit(
          "/admin/grades/",
          "POST",
          { student_id: student, course_id: course, period_id: period, score },
          "Nota registrada",
        );
        setScore("");
      }}
    >
      <label>
        Alumno
        <select
          value={student}
          onChange={(e) => setStudent(Number(e.target.value))}
        >
          {data.students.map((s) => (
            <option value={s.id} key={s.id}>
              {s.student_code} · {s.full_name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Curso
        <select
          value={course}
          onChange={(e) => setCourse(Number(e.target.value))}
        >
          {data.courses.map((c) => (
            <option value={c.id} key={c.id}>
              {c.code} · {c.name}
            </option>
          ))}
        </select>
      </label>
      <label>
        Período
        <select
          value={period}
          onChange={(e) => setPeriod(Number(e.target.value))}
        >
          {data.periods.map((p) => (
            <option value={p.id} key={p.id}>
              {p.code}
            </option>
          ))}
        </select>
      </label>
      <label>
        Nota final (0–20)
        <input
          type="number"
          min="0"
          max="20"
          step="0.01"
          required
          value={score}
          onChange={(e) => setScore(e.target.value)}
        />
      </label>
      <button className="btn primary">Guardar nota</button>
    </form>
  );
}

function NewTeacher({
  teachers,
  submit,
}: {
  teachers: AdminData["teachers"];
  submit: (p: string, m: string, b: unknown, s: string) => Promise<void>;
}) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  return (
    <>
      <form
        className="teacher-account-form"
        onSubmit={(e) => {
          e.preventDefault();
          void submit(
            "/admin/teachers/",
            "POST",
            { name, email, password },
            "Acceso docente vinculado",
          );
          setName("");
          setEmail("");
          setPassword("");
        }}
      >
        <div className="eyebrow">ACCESO DOCENTE</div>
        <p>
          Vincula un docente por correo. Si el correo ya pertenece a un
          administrador, conservará ambos perfiles.
        </p>
        <div className="grid-form">
          <label>
            Nombre del docente
            <input
              list="teachers-without-account"
              required
              minLength={5}
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <datalist id="teachers-without-account">
              {teachers
                .filter((t) => !t.username)
                .map((t) => (
                  <option key={t.id} value={t.name} />
                ))}
            </datalist>
          </label>
          <label>
            Correo institucional
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="off"
            />
          </label>
          <label>
            Contraseña inicial
            <input
              type="password"
              minLength={12}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
            <small>Solo para correos nuevos.</small>
          </label>
          <button className="btn outline">Vincular acceso</button>
        </div>
      </form>
      <div className="table-wrap inner">
        <table>
          <thead>
            <tr>
              <th>Docente</th>
              <th>Correo</th>
              <th>Estado</th>
              <th>Administrar</th>
            </tr>
          </thead>
          <tbody>
            {teachers
              .filter((t) => t.username)
              .map((t) => (
                <tr key={t.id}>
                  <td>
                    <strong>{t.name}</strong>
                  </td>
                  <td>{t.email}</td>
                  <td>
                    <Badge kind={t.active ? "good" : "warn"}>
                      {t.active ? "Activo" : "Suspendido"}
                    </Badge>
                  </td>
                  <td>
                    <div className="account-actions">
                      <button
                        type="button"
                        onClick={() => {
                          const name = window.prompt("Nombre completo", t.name);
                          if (name)
                            void submit(
                              `/admin/teachers/${t.id}/`,
                              "PATCH",
                              { name },
                              "Docente actualizado",
                            );
                        }}
                      >
                        Editar
                      </button>
                      <button
                        type="button"
                        onClick={() =>
                          void submit(
                            `/admin/teachers/${t.id}/`,
                            "PATCH",
                            { active: !t.active },
                            t.active
                              ? "Cuenta suspendida"
                              : "Cuenta reactivada",
                          )
                        }
                      >
                        {t.active ? "Suspender" : "Reactivar"}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          const password = window.prompt(
                            "Contraseña temporal (mínimo 12 caracteres)",
                          );
                          if (password)
                            void submit(
                              `/admin/teachers/${t.id}/`,
                              "PATCH",
                              { temporary_password: password },
                              "Contraseña temporal creada",
                            );
                        }}
                      >
                        Restablecer clave
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function Timetable({ sections }: { sections: Section[] }) {
  return (
    <div className="panel spaced">
      <span className="eyebrow">MATRÍCULA CONFIRMADA</span>
      <h2>Mi horario semanal</h2>
      <div className="week-grid">
        {days.map((day, i) => (
          <div className="week-day" key={day}>
            <strong>{day}</strong>
            {sections.flatMap((s) =>
              s.meetings
                .filter((m) => m.day === i)
                .map((m) => (
                  <div className="week-event" key={`${s.id}-${m.start}`}>
                    <b>
                      {m.start}–{m.end}
                    </b>
                    <span>{s.course_name}</span>
                    <small>
                      {s.section} · {s.classroom}
                    </small>
                  </div>
                )),
            )}
            {sections.every((s) => s.meetings.every((m) => m.day !== i)) && (
              <small className="free-day">Sin clases</small>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

function NewPlan({
  plans,
  submit,
}: {
  plans: AdminData["plans"];
  submit: (p: string, m: string, b: unknown, s: string) => Promise<void>;
}) {
  const [name, setName] = useState("");
  const [source, setSource] = useState(plans[0]?.id || 0);
  return (
    <form
      className="simple-form plan-clone"
      onSubmit={(e) => {
        e.preventDefault();
        void submit(
          "/admin/plans/",
          "POST",
          { name, clone_from: source },
          "Nueva versión de la malla creada",
        );
        setName("");
      }}
    >
      <div className="eyebrow">CREAR VERSIÓN DE MALLA</div>
      <select
        value={source}
        onChange={(e) => setSource(Number(e.target.value))}
      >
        {plans.map((p) => (
          <option key={p.id} value={p.id}>
            {p.name}
          </option>
        ))}
      </select>
      <input
        placeholder="Nombre de la nueva versión"
        value={name}
        required
        onChange={(e) => setName(e.target.value)}
      />
      <button className="btn outline">Copiar plan</button>
    </form>
  );
}
