// Minimal MCP client for the frontend
// Exposes helpers to call backend MCP endpoints.

type Story = {
  id: string;
  title?: string;
  description: string;
  acceptance_criteria?: string;
};

function getBackendBase() {
  const env = (process.env as any).NEXT_PUBLIC_API_URL;
  if (env) {
    // strip trailing /api if present (backend routes are at root)
    return env.replace(/\/api\/?$/, "");
  }
  return "http://localhost:8000";
}

async function post(path: string, body: any) {
  const base = getBackendBase();
  const url = `${base}${path}`;
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`MCP API error ${resp.status}: ${text}`);
  }
  return resp.json();
}

export async function analyzeStories(stories: Story[]) {
  return post("mcp/analyze", { stories });
}

export async function extractAndPrioritize(stories: Story[]) {
  return post("mcp/requirements", { stories });
}

export async function buildReport(requirements: any[], project_id?: string) {
  return post("mcp/report", { requirements, project_id });
}

export async function runPipeline(payload: { raw_text?: string; stories?: Story[]; project_id?: string }) {
  return post("mcp/pipeline", payload);
}

export default { analyzeStories, extractAndPrioritize, buildReport };
