const BASE_URL = "http://127.0.0.1:8000";

export async function getTags() {
  const res = await fetch(`${BASE_URL}/tags`);
  if (!res.ok) {
    throw new Error(`Failed to fetch tags: ${res.status}`);
  }
  return res.json();
}

export async function getTag(id: string) {
  const res = await fetch(`${BASE_URL}/tags/${id}`);
  if (!res.ok) {
    throw new Error(`Failed to fetch tag ${id}: ${res.status}`);
  }
  return res.json();
}

export async function createTag(tag: Record<string, unknown>) {
  const res = await fetch(`${BASE_URL}/tags`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(tag),
  });
  if (!res.ok) {
    throw new Error(`Failed to create tag: ${res.status}`);
  }
  return res.json();
}
