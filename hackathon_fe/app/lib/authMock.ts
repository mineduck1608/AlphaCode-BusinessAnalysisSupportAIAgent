export type User = { email: string; name?: string };

const STORAGE_KEY = "chatgpt_clone_user";

export async function mockLogin(email: string, password: string): Promise<User> {
  // fake network delay
  await new Promise((r) => setTimeout(r, 700));
  const user: User = { email, name: email.split("@")[0] || "User" };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
  return user;
}

export function mockLogout() {
  localStorage.removeItem(STORAGE_KEY);
}

export function getCurrentUser(): User | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null;
    return JSON.parse(raw) as User;
  } catch {
    return null;
  }
}
