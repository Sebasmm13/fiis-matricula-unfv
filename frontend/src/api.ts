export type Role = "student" | "admin" | "teacher";
export interface Identity {
  username: string;
  email: string;
  name: string;
  role: Role | null;
  roles: Role[];
  has_photo: boolean;
  photo_version: string | null;
  must_change_password: boolean;
  student_code?: string;
  plan?: string;
  plan_active?: boolean;
  official_cycle?: number;
  has_enrollment?: boolean;
  period?: { id: number; code: string; status: string; max_credits: number };
}
export interface Meeting {
  day: number;
  day_name: string;
  start: string;
  end: string;
}
export interface Section {
  id: number;
  course_id: number | null;
  course_name: string;
  curricular_code: string | null;
  official_code: string | null;
  section: string;
  teacher: string;
  teacher_id: number | null;
  classroom: string;
  cycle: string;
  capacity: number;
  occupied: number;
  available: number;
  published: boolean;
  review_required: boolean;
  meetings: Meeting[];
  scheduled_minutes: number;
  theory_hours: number | null;
  practice_hours: number | null;
  period?: string;
}
export interface Course {
  id: number;
  plan_id: number;
  plan_name: string;
  code: string;
  name: string;
  semester: number;
  credits: number | null;
  theory_hours: number | null;
  practice_hours: number | null;
  elective_track: string;
  academic_data_verified: boolean;
  prerequisites: { id: number; code: string; name: string }[];
  passed: boolean;
  eligible?: boolean;
}
export interface Catalog {
  period: { code: string; status: string; max_credits: number };
  courses: Course[];
  sections: Section[];
}
export interface Enrollment {
  id: number;
  period: string;
  confirmed_at: string;
  sections: Section[];
}
export interface Grade {
  course_id: number;
  course: string;
  code: string;
  period: string;
  score: number;
  passed: boolean;
  credits: number | null;
  semester: number;
}
export interface AdminData {
  periods: {
    id: number;
    code: string;
    status: string;
    max_credits: number;
    is_current: boolean;
    convalidation_active?: boolean;
  }[];
  plans: { id: number; name: string; active: boolean }[];
  courses: Course[];
  sections: Section[];
  teachers: {
    id: number;
    name: string;
    active: boolean;
    username: string | null;
    email: string | null;
  }[];
  students: {
    id: number;
    student_code: string;
    full_name: string;
    plan__name: string;
    active: boolean;
    email: string;
    activation_pending: boolean;
  }[];
}
export interface Demand {
  period: string;
  capacity_assumption: number;
  total_students: number;
  notification: string;
  courses: {
    course_id: number;
    code: string;
    course: string;
    students: number;
    suggested_sections: number;
    preferences: { section: string; students: number }[];
  }[];
}
export interface TeacherSection extends Section {
  students: { code: string; name: string }[];
}
export interface TeacherData {
  period: string;
  sections: TeacherSection[];
}
let csrfToken = "";
export async function csrf() {
  const r = await fetch("/api/auth/csrf/", { credentials: "include" });
  const d = await r.json();
  csrfToken = d.csrfToken;
  return csrfToken;
}
export async function api<T>(
  path: string,
  method = "GET",
  body?: unknown,
): Promise<T> {
  if (method !== "GET" && !csrfToken) await csrf();
  const request = () =>
    fetch("/api" + path, {
      method,
      credentials: "include",
      headers:
        body === undefined
          ? { "X-CSRFToken": csrfToken }
          : { "Content-Type": "application/json", "X-CSRFToken": csrfToken },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  let r = await request();
  // Django rota el token al iniciar sesión. Si una pestaña conserva uno anterior,
  // obtenemos el vigente y repetimos una sola vez la operación original.
  if (r.status === 403 && method !== "GET") {
    await csrf();
    r = await request();
  }
  if (!r.ok) {
    let msg = "No se pudo completar la solicitud.";
    try {
      const d = await r.json();
      msg = typeof d.detail === "string" ? d.detail : JSON.stringify(d);
    } catch {
      // Conserva el mensaje genérico cuando la respuesta no contiene JSON.
    }
    throw Error(msg);
  }
  const result = (await r.json()) as T;
  if (path === "/auth/login/") await csrf();
  return result;
}
export async function downloadReceipt(id: number, period: string) {
  const r = await fetch(`/api/enrollments/${id}/pdf/`, {
    credentials: "include",
  });
  if (!r.ok) throw Error("No se pudo descargar la constancia.");
  const blob = await r.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `matricula_${period}.pdf`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 15000);
}
export async function changePhoto(file?: File) {
  if (!csrfToken) await csrf();
  const form = new FormData();
  if (file) form.append("photo", file);
  const r = await fetch("/api/profile/photo/", {
    method: file ? "POST" : "DELETE",
    credentials: "include",
    headers: { "X-CSRFToken": csrfToken },
    body: file ? form : undefined,
  });
  if (!r.ok) {
    let message = "No se pudo guardar la foto.";
    try {
      const v = await r.json();
      message = typeof v.detail === "string" ? v.detail : JSON.stringify(v);
    } catch {
      // Conserva el mensaje genérico cuando la respuesta no contiene JSON.
    }
    throw Error(message);
  }
}
export async function downloadTeacherReport(
  period: string,
  sectionId?: number,
) {
  const search = new URLSearchParams({ period });
  if (sectionId) search.set("section_id", String(sectionId));
  const r = await fetch(`/api/teacher/report/pdf/?${search}`, {
    credentials: "include",
  });
  if (!r.ok) throw Error("No se pudo descargar el reporte docente.");
  const url = URL.createObjectURL(await r.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = `horarios_y_alumnos_${period}.pdf`;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 15000);
}
