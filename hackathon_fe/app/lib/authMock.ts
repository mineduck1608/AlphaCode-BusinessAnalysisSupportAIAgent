export type User = { email: string; name?: string, id: number };

const STORAGE_KEY = "chatgpt_clone_user";

export async function mockLogin(email: string, password: string): Promise<User> {
  // fake network delay
  await new Promise((r) => setTimeout(r, 700));
  const user: User = { email, name: email.split("@")[0] || "User", id: 2};
  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  return user;
}

export function getCurrentUserId(): number | null {
  if (typeof window === "undefined") return null;
  const id = localStorage.getItem("user_id");
  return id ? Number(id) : null;
}

export function logout() {
  if (typeof window === "undefined") return;
  localStorage.removeItem("user_id");
}

export function getCurrentUserEmail(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("user_email");
}