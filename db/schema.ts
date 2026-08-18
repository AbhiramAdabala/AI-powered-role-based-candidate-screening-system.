import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const interviewSessions = sqliteTable("interview_sessions", {
  id: integer("id").primaryKey({ autoIncrement: true }),
  role: text("role").notNull(),
  resumeName: text("resume_name"),
  profile: text("profile"),
  questions: text("questions", { mode: "json" }).$type<string[]>().notNull(),
  answers: text("answers", { mode: "json" }).$type<string[]>().notNull(),
  createdAt: integer("created_at", { mode: "timestamp_ms" }).notNull(),
});
