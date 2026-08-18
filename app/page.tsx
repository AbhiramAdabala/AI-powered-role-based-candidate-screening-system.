"use client";

import { ChangeEvent, useRef, useState } from "react";

type Role = "AI / ML Engineer" | "Backend Engineer" | "Data Scientist";
type Source = { chunk_id:string; source:string; excerpt:string; relevance:number };
type Question = { id:string; ordinal:number; prompt:string; topic:string; difficulty:string; sources:Source[] };
type Report = { score:number; summary:string; strongest_area:string; depth:string; strengths:string[]; improvements:string[] };
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const roles:Role[] = ["AI / ML Engineer", "Backend Engineer", "Data Scientist"];

export default function Home() {
  const [stage,setStage]=useState<"setup"|"interview"|"report">("setup");
  const [role,setRole]=useState<Role>("AI / ML Engineer");
  const [file,setFile]=useState<File|null>(null);
  const [sessionId,setSessionId]=useState("");
  const [question,setQuestion]=useState<Question|null>(null);
  const [skills,setSkills]=useState<string[]>([]);
  const [answer,setAnswer]=useState("");
  const [answered,setAnswered]=useState(0);
  const [maxQuestions,setMaxQuestions]=useState(5);
  const [report,setReport]=useState<Report|null>(null);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const inputRef=useRef<HTMLInputElement>(null);

  function pickFile(e:ChangeEvent<HTMLInputElement>){const chosen=e.target.files?.[0];if(chosen){setFile(chosen);setError("")}}
  async function start(){
    if(!file){inputRef.current?.click();return}
    setBusy(true);setError("");
    try{const form=new FormData();form.append("role",role);form.append("resume",file);const response=await fetch(`${API}/api/interviews/start`,{method:"POST",body:form});const data=await response.json();if(!response.ok)throw new Error(data.detail||"Could not start interview");setSessionId(data.session_id);setQuestion(data.question);setSkills(data.skills);setMaxQuestions(data.max_questions);setStage("interview")}
    catch(e){setError(e instanceof Error?e.message:"Could not reach the interview service")}
    finally{setBusy(false)}
  }
  async function submitAnswer(){
    if(!answer.trim()||!question)return;setBusy(true);setError("");
    try{const response=await fetch(`${API}/api/interviews/${sessionId}/answers`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({question_id:question.id,answer:answer.trim()})});const data=await response.json();if(!response.ok)throw new Error(data.detail||"Could not save answer");setAnswered(v=>v+1);setAnswer("");if(data.complete){setReport(data.report);setStage("report")}else setQuestion(data.question)}
    catch(e){setError(e instanceof Error?e.message:"Could not submit answer")}
    finally{setBusy(false)}
  }
  function reset(){setStage("setup");setSessionId("");setQuestion(null);setAnswer("");setAnswered(0);setReport(null);setError("")}

  return <main>
    <nav className="nav"><button className="brand" onClick={reset} aria-label="Nexus home"><span className="brandMark">N</span><span>NEXUS</span></button><div className="navMeta"><span className="statusDot" />{stage==="setup"?"RAG interview workspace":`${role} · Live session`}</div></nav>
    {stage==="setup"&&<><section className="hero"><div className="eyebrow"><span>01</span>Candidate setup</div><h1>Your experience.<br/><em>Our questions.</em></h1><p className="lede">A grounded technical interview generated from your resume and a role-specific knowledge base—not a fixed questionnaire.</p></section><section className="setupGrid"><div className="uploadCard" onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();const f=e.dataTransfer.files[0];if(f)setFile(f)}}><div className="cardIndex">RESUME / 01</div><div className="uploadIcon">↗</div><h2>{file?file.name:"Drop your resume here"}</h2><p>{file?`${Math.max(1,Math.round(file.size/1024))} KB · Ready to parse`:"PDF or TXT · up to 10 MB"}</p><input ref={inputRef} hidden type="file" accept=".pdf,.txt" onChange={pickFile}/><button className="secondary" onClick={()=>inputRef.current?.click()}>{file?"Replace file":"Choose file"}</button><div className="pipeline"><span>PARSE</span><i>→</i><span>EMBED</span><i>→</i><span>RETRIEVE</span><i>→</i><span>GENERATE</span></div></div><div className="rolePanel"><div className="cardIndex">TARGET ROLE / 02</div><h2>What are you interviewing for?</h2><div className="roleOptions">{roles.map(item=><button key={item} className={role===item?"role active":"role"} onClick={()=>setRole(item)}><span>{item}</span><span>{role===item?"●":"○"}</span></button>)}</div>{error&&<p className="error" role="alert">{error}</p>}<button className="primary" disabled={busy} onClick={start}>{busy?"Building from retrieved context…":file?"Build my interview":"Add resume to continue"}<span>→</span></button><p className="privacy">Your resume is parsed securely and used to tailor retrieval.</p></div></section></>}
    {stage==="interview"&&question&&<section className="interviewShell"><aside className="sessionRail"><div><div className="cardIndex">LIVE INTERVIEW</div><h2>{role}</h2><p>{file?.name}</p></div><div className="skillBlock"><span>EXTRACTED SIGNALS</span><div>{(skills.length?skills:["Profile parsed"]).map(skill=><b key={skill}>{skill}</b>)}</div></div><div className="progressList">{Array.from({length:maxQuestions},(_,i)=><div className={i===answered?"progress active":i<answered?"progress done":"progress"} key={i}><span>{String(i+1).padStart(2,"0")}</span><p>{i===answered?question.topic:i<answered?"Answered":"Adaptive follow-up"}</p></div>)}</div></aside><div className="questionStage"><div className="questionTop"><span>QUESTION {question.ordinal} / {maxQuestions}</span><span className="level">{question.difficulty.toUpperCase()}</span></div><h3>{question.prompt}</h3><details className="sourceNote"><summary>GROUNDING · {question.sources.length} RETRIEVED CHUNKS</summary>{question.sources.map(source=><div className="trace" key={source.chunk_id}><b>{source.source}</b><span>{Math.round(source.relevance*100)}% match</span><p>{source.excerpt}</p><code>{source.chunk_id}</code></div>)}</details><label htmlFor="answer">Your answer</label><textarea id="answer" autoFocus value={answer} onChange={e=>setAnswer(e.target.value)} placeholder="Think aloud. Explain assumptions, tradeoffs, validation, and failure modes…" onKeyDown={e=>{if((e.metaKey||e.ctrlKey)&&e.key==="Enter")submitAnswer()}}/>{error&&<p className="error" role="alert">{error}</p>}<div className="answerActions"><span>{answer.length} characters · Ctrl/⌘ + Enter</span><button className="primary inline" disabled={!answer.trim()||busy} onClick={submitAnswer}>{busy?"Retrieving next context…":question.ordinal===maxQuestions?"Finish interview":"Submit & adapt"}<span>→</span></button></div></div></section>}
    {stage==="report"&&report&&<section className="reportShell"><div className="reportHero"><div><div className="eyebrow"><span>✓</span>Session complete</div><h1>Clear signal.<br/><em>Useful next steps.</em></h1></div><div className="score"><strong>{report.score}</strong><span>OVERALL SIGNAL</span></div></div><div className="reportGrid"><article className="summaryCard"><div className="cardIndex">INTERVIEW SUMMARY</div><h2>{report.summary}</h2><div className="metrics"><div><strong>{answered}/{maxQuestions}</strong><span>Answered</span></div><div><strong>{report.strongest_area}</strong><span>Strongest area</span></div><div><strong>{report.depth}</strong><span>Depth reached</span></div></div></article><article className="insightsCard"><div className="cardIndex">EVIDENCE-BASED SIGNALS</div>{report.strengths.map((item,i)=><div className="insight positive" key={item}><span>0{i+1}</span><div><b>{item}</b><p>Supported by the recorded interview transcript.</p></div></div>)}{report.improvements.map((item,i)=><div className="insight" key={item}><span>0{i+report.strengths.length+1}</span><div><b>{item}</b><p>Recommended focus for the next practice session.</p></div></div>)}</article></div><div className="reportActions"><button className="secondary" onClick={reset}>Start another interview</button><button className="primary inline" onClick={()=>window.print()}>Save report <span>↗</span></button></div></section>}
    <footer><span>RESUME → QUERY → RETRIEVAL → QUESTION → ANSWER → STORAGE</span><span>ADAPTIVE · TRACEABLE · GROUNDED</span></footer>
  </main>
}
