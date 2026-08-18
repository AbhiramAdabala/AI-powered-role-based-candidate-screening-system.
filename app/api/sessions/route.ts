import { env } from "cloudflare:workers";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  try {
    const body = await request.json() as { role?: string; resumeName?: string; profile?: string; questions?: string[]; answers?: string[] };
    if (!body.role || !Array.isArray(body.questions) || !Array.isArray(body.answers)) return NextResponse.json({ error: "Invalid session" }, { status: 400 });
    await env.DB.prepare("CREATE TABLE IF NOT EXISTS interview_sessions (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL, resume_name TEXT, profile TEXT, questions TEXT NOT NULL, answers TEXT NOT NULL, created_at INTEGER NOT NULL)").run();
    await env.DB.prepare("INSERT INTO interview_sessions (role, resume_name, profile, questions, answers, created_at) VALUES (?, ?, ?, ?, ?, ?)")
      .bind(body.role, body.resumeName ?? null, body.profile ?? null, JSON.stringify(body.questions), JSON.stringify(body.answers), Date.now()).run();
    return NextResponse.json({ saved: true }, { status: 201 });
  } catch {
    return NextResponse.json({ saved: false }, { status: 503 });
  }
}
