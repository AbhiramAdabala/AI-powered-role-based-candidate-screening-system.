CREATE TABLE `interview_sessions` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`role` text NOT NULL,
	`resume_name` text,
	`profile` text,
	`questions` text NOT NULL,
	`answers` text NOT NULL,
	`created_at` integer NOT NULL
);
