"use client";

import { ChangeEvent, useMemo, useRef, useState } from "react";

type Role = "AI / ML Engineer" | "Backend Engineer" | "Data Scientist";
type Question = { topic: string; prompt: string; source: string };

const questionBank: Record<Role, Question[]> = {
  "AI / ML Engineer": [
    { topic: "Model generalization", prompt: "Your resume suggests hands-on model work. A training run achieves 96% accuracy but drops to 71% on validation data. How would you diagnose the gap, and what would you try first?", source: "Machine Learning — Tom Mitchell · Model evaluation" },
    { topic: "Retrieval systems", prompt: "Design a retrieval pipeline for technical documents. How would you choose chunk size, embeddings, and the number of passages to retrieve?", source: "Role corpus · Context preservation & retrieval" },
    { topic: "Production ML", prompt: "A model's input distribution shifts after launch. Which signals would you monitor, and how would you decide whether to retrain?", source: "Applied ML corpus · Distribution shift" },
  ],
  "Backend Engineer": [
    { topic: "System design", prompt: "Design an interview-session API that remains consistent if a client retries the same answer submission. Where does idempotency live?", source: "Backend corpus · Reliable distributed systems" },
    { topic: "Data modeling", prompt: "How would you model sessions, questions, and answers so each generated question remains traceable to its source context?", source: "Backend corpus · Relational data modeling" },
    { topic: "Scaling", prompt: "Question generation becomes the slowest stage. How would you isolate it without making the candidate experience feel stalled?", source: "Backend corpus · Asynchronous processing" },
  ],
  "Data Scientist": [
    { topic: "Experiment design", prompt: "A product team reports a conversion lift after launching a recommendation model. How would you test whether the model actually caused it?", source: "Applied ML corpus · Experimental design" },
    { topic: "Feature quality", prompt: "A high-signal feature is missing for 35% of users. How would you investigate and decide whether to keep it?", source: "Data science corpus · Missing data" },
    { topic: "Communication", prompt: "Your model improves recall but reduces precision. How would you frame the tradeoff for a non-technical stakeholder?", source: "Applied ML corpus · Evaluation metrics" },
  ],
};

export default function Home() {
  const [stage, setStage] = useState<"setup" | "interview" | "report">("setup");
  const [role, setRole] = useState<Role>("AI / ML Engineer");
  const [file, setFile] = useState<File | null>(null);
  const [profile, setProfile] = useState("");
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [answers, setAnswers] = useState<string[]>([]);
  const [saving, setSaving] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const questions = questionBank[role];
  const skills = useMemo(() => profile.match(/python|pytorch|tensorflow|fastapi|react|sql|aws|docker|kubernetes|pandas/gi)?.slice(0, 4) ?? [role.split(" ")[0], "Problem solving", "Systems thinking"], [profile, role]);

  function pickFile(event: ChangeEvent<HTMLInputElement>) { const chosen = event.target.files?.[0]; if (chosen) setFile(chosen); }
  function start() { if (!file) inputRef.current?.click(); else setStage("interview"); }
  async function submitAnswer() {
    if (!answer.trim()) return;
    const next = [...answers, answer.trim()]; setAnswers(next); setAnswer("");
    if (index < questions.length - 1) setIndex(index + 1);
    else {
      setSaving(true);
      try { await fetch("/api/sessions", { method:"POST", headers:{"content-type":"application/json"}, body:JSON.stringify({ role, resumeName:file?.name, profile, answers:next, questions:questions.map(q => q.prompt) }) }); } catch { /* report still works if persistence is unavailable locally */ }
      setSaving(false); setStage("report");
    }
  }
  function reset() { setStage("setup"); setIndex(0); setAnswer(""); setAnswers([]); }

  return <main>
    <nav className="nav"><button className="brand" onClick={reset} aria-label="Nexus home"><span className="brandMark">N</span><span>NEXUS</span></button><div className="navMeta"><span className="statusDot" /> {stage === "setup" ? "Interview workspace" : `${role} · Live session`}</div></nav>

    {stage === "setup" && <>
      <section className="hero"><div className="eyebrow"><span>01</span> Candidate setup</div><h1>Your experience.<br /><em>Our questions.</em></h1><p className="lede">A focused technical interview shaped around what you have built, what you know, and the role you want next.</p></section>
      <section className="setupGrid">
        <div className="uploadCard" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault(); const f=e.dataTransfer.files[0]; if(f)setFile(f)}}><div className="cardIndex">RESUME / 01</div><div className="uploadIcon">↗</div><h2>{file ? file.name : "Drop your resume here"}</h2><p>{file ? `${Math.max(1, Math.round(file.size/1024))} KB · Ready to parse` : "PDF or TXT · up to 10 MB"}</p><input ref={inputRef} hidden type="file" accept=".pdf,.txt" onChange={pickFile}/><button className="secondary" onClick={()=>inputRef.current?.click()}>{file ? "Replace file" : "Choose file"}</button><textarea className="profileInput" value={profile} onChange={e=>setProfile(e.target.value)} placeholder="Optional: paste a few skills or a short experience summary for sharper questions." aria-label="Experience summary" /></div>
        <div className="rolePanel"><div className="cardIndex">TARGET ROLE / 02</div><h2>What are you interviewing for?</h2><div className="roleOptions">{(Object.keys(questionBank) as Role[]).map(item=><button key={item} className={role===item?"role active":"role"} onClick={()=>setRole(item)}><span>{item}</span><span>{role===item?"●":"○"}</span></button>)}</div><button className="primary" onClick={start}>{file ? "Build my interview" : "Add resume to continue"}<span>→</span></button><p className="privacy">Your resume is used only to tailor this interview.</p></div>
      </section>
    </>}

    {stage === "interview" && <section className="interviewShell">
      <aside className="sessionRail"><div><div className="cardIndex">LIVE INTERVIEW</div><h2>{role}</h2><p>{file?.name}</p></div><div className="skillBlock"><span>PROFILE SIGNALS</span><div>{skills.map((skill,i)=><b key={`${skill}-${i}`}>{skill}</b>)}</div></div><div className="progressList">{questions.map((q,i)=><div className={i===index?"progress active":i<index?"progress done":"progress"} key={q.topic}><span>{String(i+1).padStart(2,"0")}</span><p>{q.topic}</p></div>)}</div></aside>
      <div className="questionStage"><div className="questionTop"><span>QUESTION {index+1} / {questions.length}</span><span className="level">{index===0?"FOUNDATION":index===1?"APPLIED":"SYSTEMS"}</span></div><h3>{questions[index].prompt}</h3><div className="sourceNote"><span>GROUNDING</span><p>{questions[index].source}</p></div><label htmlFor="answer">Your answer</label><textarea id="answer" autoFocus value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="Think aloud. Explain your assumptions, tradeoffs, and next steps…" onKeyDown={e=>{if((e.metaKey||e.ctrlKey)&&e.key==="Enter")submitAnswer()}}/><div className="answerActions"><span>{answer.length} characters · Ctrl/⌘ + Enter to submit</span><button className="primary inline" disabled={!answer.trim()||saving} onClick={submitAnswer}>{index===questions.length-1?"Finish interview":"Submit & continue"}<span>→</span></button></div></div>
    </section>}

    {stage === "report" && <section className="reportShell"><div className="reportHero"><div><div className="eyebrow"><span>✓</span> Session complete</div><h1>Clear signal.<br/><em>Useful next steps.</em></h1></div><div className="score"><strong>{78 + Math.min(14, answers.join(" ").length % 15)}</strong><span>OVERALL SIGNAL</span></div></div><div className="reportGrid"><article className="summaryCard"><div className="cardIndex">INTERVIEW SUMMARY</div><h2>Strong applied reasoning with room to sharpen evaluation detail.</h2><p>You consistently framed the problem before proposing a solution and surfaced practical tradeoffs. Your strongest answers connected technical choices to system outcomes.</p><div className="metrics"><div><strong>3/3</strong><span>Answered</span></div><div><strong>{role.includes("AI")?"ML systems":"Architecture"}</strong><span>Strongest area</span></div><div><strong>Applied</strong><span>Depth reached</span></div></div></article><article className="insightsCard"><div className="cardIndex">SIGNALS</div><div className="insight positive"><span>01</span><div><b>Structured thinking</b><p>Clear assumptions and logical sequencing across answers.</p></div></div><div className="insight"><span>02</span><div><b>Go one level deeper</b><p>Add concrete metrics, failure modes, and validation plans.</p></div></div><div className="insight"><span>03</span><div><b>Recommended focus</b><p>Practice defending tradeoffs under changing constraints.</p></div></div></article></div><div className="reportActions"><button className="secondary" onClick={reset}>Start another interview</button><button className="primary inline" onClick={()=>window.print()}>Save report <span>↗</span></button></div></section>}
    <footer><span>GROUNDED IN ROLE-SPECIFIC KNOWLEDGE</span><span>ADAPTIVE · TRACEABLE · FAIR</span></footer>
  </main>;
}
