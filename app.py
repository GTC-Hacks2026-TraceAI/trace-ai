"""Trace AI – Self-contained single-file application.

Frontend and backend in one file.  No npm, no CDN, no build step.

Usage
-----
    pip install -r requirements.txt
    python app.py

Then open http://localhost:8000 in your browser.
"""

import os

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.routes import router

# =============================================================================
# Inline frontend – all HTML, CSS, and JavaScript embedded as a raw string.
# =============================================================================
_FRONTEND = r"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Trace AI</title>
<style>
/* Reset */
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{-webkit-font-smoothing:antialiased}
body{background:#09090b;color:#fafafa;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.5;min-height:100vh}
a{color:inherit;text-decoration:none}
button{cursor:pointer;font:inherit;background:none;border:none}
svg{display:block;flex-shrink:0}
/* Custom Properties */
:root{
  --bg:#09090b;--bg-card:#18181b;--bg-muted:rgba(39,39,42,.5);
  --border:rgba(255,255,255,.08);
  --fg:#fafafa;--fg2:#a1a1aa;--fg3:#71717a;
  --primary:#3b82f6;--primary-h:#2563eb;--primary-fg:#fff;
  --destructive:#ef4444;--r:.5rem}
/* Layout */
.container{max-width:1280px;margin:0 auto;padding:0 1.5rem}
.row{display:flex;align-items:center}
.row.gap-xs{gap:.25rem}.row.gap-sm{gap:.5rem}.row.gap-md{gap:.75rem}.row.gap-lg{gap:1rem}
.row.between{justify-content:space-between}
.col{display:flex;flex-direction:column}
.col.gap-sm{gap:.5rem}.col.gap-md{gap:.75rem}.col.gap-lg{gap:1rem}.col.gap-xl{gap:1.5rem}
.grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem}
.grid-3{display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:1.5rem}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:1.5rem;align-items:start}
.main-col{display:grid;grid-template-columns:1fr 2fr;gap:2rem;align-items:start}
.space-y>*+*{margin-top:1.5rem}
.space-y-sm>*+*{margin-top:1rem}
.space-y-xs>*+*{margin-top:.75rem}
/* Navbar */
.navbar{position:sticky;top:0;z-index:50;border-bottom:1px solid var(--border);background:rgba(9,9,11,.95);backdrop-filter:blur(10px)}
.navbar .container{display:flex;align-items:center;height:56px}
.logo{display:flex;align-items:center;gap:.5rem;font-weight:600;margin-right:1.5rem}
.logo svg{color:var(--primary)}
.nav-links{display:flex;gap:1.5rem;align-items:center}
.nav-link{display:flex;align-items:center;gap:.375rem;font-size:.875rem;color:var(--fg3);transition:color .15s}
.nav-link:hover,.nav-link.active{color:var(--fg)}
/* Page Chrome */
.page{padding:2rem 0}
.page-hdr{margin-bottom:2rem}
.page-hdr h1{font-size:1.875rem;font-weight:700;letter-spacing:-.025em}
.page-hdr p{margin-top:.5rem;color:var(--fg2)}
.section-hdr{font-size:1.125rem;font-weight:600;display:flex;align-items:center;gap:.5rem;margin-bottom:1rem}
/* Card */
.card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r)}
.card-hdr{padding:1.25rem 1.25rem .75rem}
.card-title{font-size:1.125rem;font-weight:600;display:flex;align-items:center;gap:.5rem}
.card-sub{font-size:.875rem;color:var(--fg2);margin-top:.25rem}
.card-body{padding:.75rem 1.25rem 1.25rem}
/* Case Card */
.case-card{display:block;transition:border-color .2s,background .2s;cursor:pointer}
.case-card:hover{border-color:rgba(59,130,246,.5);background:rgba(39,39,42,.4)}
.case-hdr{padding:1rem 1rem .5rem;display:flex;justify-content:space-between;align-items:flex-start;gap:.75rem}
.case-name{font-size:1rem;font-weight:600;display:flex;align-items:center;gap:.5rem}
.case-date{font-size:.75rem;color:var(--fg3);margin-top:.25rem}
.case-content{padding:.25rem 1rem 1rem;display:flex;flex-direction:column;gap:.5rem}
.case-desc{font-size:.875rem;color:var(--fg2);overflow:hidden;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2}
.case-loc{font-size:.875rem;color:var(--fg2);display:flex;align-items:center;gap:.25rem}
.case-hint{font-size:.875rem;color:var(--primary);display:flex;align-items:center;gap:.25rem;opacity:0;transition:opacity .2s}
.case-card:hover .case-hint{opacity:1}
/* Button */
.btn{display:inline-flex;align-items:center;justify-content:center;gap:.5rem;padding:.5rem 1rem;border-radius:var(--r);font-size:.875rem;font-weight:500;transition:background .15s,opacity .15s;white-space:nowrap}
.btn-primary{background:var(--primary);color:var(--primary-fg)}
.btn-primary:hover:not(:disabled){background:var(--primary-h)}
.btn-primary:disabled{opacity:.5;cursor:not-allowed}
.btn-outline{background:transparent;border:1px solid var(--border);color:var(--fg)}
.btn-outline:hover:not(:disabled){background:var(--bg-muted)}
.btn-sm{padding:.25rem .75rem;font-size:.8125rem}
.btn-lg{padding:.75rem 1.5rem;font-size:1rem}
.btn-full{width:100%}
/* Form */
.form-group{display:flex;flex-direction:column;gap:.375rem}
.form-label{font-size:.875rem;font-weight:500;color:var(--fg);display:flex;align-items:center;gap:.375rem}
.input,.textarea{width:100%;background:transparent;border:1px solid var(--border);border-radius:var(--r);padding:.5rem .75rem;font:inherit;font-size:.875rem;color:var(--fg);transition:border-color .15s}
.input:focus,.textarea:focus{outline:none;border-color:var(--primary)}
.input::placeholder,.textarea::placeholder{color:var(--fg3)}
.textarea{resize:vertical;min-height:80px}
.input[type=datetime-local]{color-scheme:dark}
/* Badge */
.badge{display:inline-flex;align-items:center;gap:.25rem;padding:.125rem .5rem;border-radius:.25rem;font-size:.75rem;font-weight:500;border:1px solid transparent;white-space:nowrap}
.badge-amber{background:rgba(217,119,6,.2);color:#fbbf24;border-color:rgba(217,119,6,.3)}
.badge-green{background:rgba(5,150,105,.2);color:#34d399;border-color:rgba(5,150,105,.3)}
.badge-blue{background:rgba(37,99,235,.2);color:#60a5fa;border-color:rgba(37,99,235,.3)}
.badge-emerald{background:rgba(5,150,105,.2);color:#34d399;border-color:rgba(5,150,105,.3)}
.badge-red{background:rgba(220,38,38,.2);color:#f87171;border-color:rgba(220,38,38,.3)}
.badge-orange{background:rgba(234,88,12,.2);color:#fb923c;border-color:rgba(234,88,12,.3)}
.badge-muted{background:rgba(39,39,42,.5);color:var(--fg2);border-color:var(--border)}
/* Tabs */
.tabs-list{display:flex;gap:.25rem;background:rgba(39,39,42,.5);border-radius:var(--r);padding:.25rem;margin-bottom:1.5rem}
.tab-btn{padding:.375rem .75rem;border-radius:calc(var(--r) - 2px);font-size:.875rem;color:var(--fg2);transition:all .15s;white-space:nowrap}
.tab-btn:hover{color:var(--fg)}
.tab-btn.active{background:var(--bg-card);color:var(--fg);box-shadow:0 1px 2px rgba(0,0,0,.4)}
/* Timeline */
.tl-item{display:flex;gap:1rem;padding-bottom:1.5rem}
.tl-item:last-child{padding-bottom:0}
.tl-left{display:flex;flex-direction:column;align-items:center;width:12px}
.tl-dot{width:12px;height:12px;border-radius:50%;flex-shrink:0}
.tl-line{width:2px;background:var(--border);flex:1;margin-top:.25rem}
.tl-body{flex:1;padding-top:.125rem}
.tl-time{font-weight:500;display:flex;align-items:center;gap:.5rem;margin-bottom:.25rem}
.tl-loc{font-size:.875rem;color:var(--fg2);display:flex;align-items:center;gap:.25rem;margin-bottom:.25rem}
.tl-expl{font-size:.875rem;color:var(--fg2)}
/* Sighting Card */
.sight-card{border-radius:var(--r);padding:1rem;display:flex;gap:1rem}
.sight-thumb{width:7rem;height:5rem;border-radius:.375rem;background:var(--bg-muted);flex-shrink:0;position:relative;display:flex;align-items:center;justify-content:center;color:var(--fg3)}
.sight-rank{position:absolute;top:.25rem;left:.25rem;background:rgba(9,9,11,.9);font-size:.6875rem;font-weight:700;padding:.125rem .375rem;border-radius:.25rem}
.sight-details{flex:1;min-width:0;display:flex;flex-direction:column;gap:.4rem}
.sight-row{display:flex;align-items:flex-start;justify-content:space-between;gap:.5rem}
.sight-cam{display:flex;align-items:center;gap:.375rem;font-size:.875rem;font-weight:500;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sight-meta{display:flex;align-items:center;gap:.75rem;font-size:.8125rem;color:var(--fg2);flex-wrap:wrap}
.sight-item{display:flex;align-items:center;gap:.25rem}
.sight-expl{font-size:.8125rem;color:var(--fg2);overflow:hidden;display:-webkit-box;-webkit-box-orient:vertical;-webkit-line-clamp:2}
/* Recommendation Card */
.rec-card{border-radius:var(--r);padding:1rem}
.rec-hdr{display:flex;align-items:flex-start;justify-content:space-between;gap:.75rem;margin-bottom:.625rem}
.rec-name{display:flex;align-items:center;gap:.5rem;font-weight:500}
.rec-loc{display:flex;align-items:center;gap:.25rem;font-size:.875rem;color:var(--fg2);margin-bottom:.5rem}
.rec-reason{font-size:.875rem;color:var(--fg2);margin-bottom:.625rem}
.rec-deadline{display:flex;align-items:center;gap:.375rem;font-size:.75rem;color:#fbbf24}
/* Loading Skeleton */
@keyframes shimmer{0%,100%{opacity:.4}50%{opacity:.75}}
.sk{border-radius:.25rem;animation:shimmer 1.5s ease-in-out infinite;background:rgba(39,39,42,.8)}
.sk-title{height:1.125rem;width:55%;margin-bottom:.625rem}
.sk-line{height:.875rem;margin-bottom:.375rem}
.sk-line.w60{width:60%}
.sk-line.w75{width:75%}
.sk-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--r);padding:1.25rem}
/* Spinner */
@keyframes spin{to{transform:rotate(360deg)}}
.spinner{width:1rem;height:1rem;border:2px solid rgba(255,255,255,.2);border-top-color:#fff;border-radius:50%;animation:spin .65s linear infinite;display:inline-block;flex-shrink:0}
/* Alerts */
.alert-err{background:rgba(220,38,38,.1);border:1px solid rgba(220,38,38,.3);border-radius:var(--r);padding:1rem 1.25rem}
.alert-err-title{display:flex;align-items:center;gap:.5rem;color:var(--destructive);font-weight:500;margin-bottom:.375rem}
.alert-err p{font-size:.875rem;color:var(--fg2);margin-bottom:.75rem}
.alert-err p:last-child{margin-bottom:0}
/* Empty State */
.empty{display:flex;flex-direction:column;align-items:center;justify-content:center;padding:3rem 1rem;text-align:center;color:var(--fg2)}
.empty svg{opacity:.4;margin-bottom:1rem}
.empty h3{font-size:1rem;font-weight:600;color:var(--fg);margin-bottom:.375rem}
.empty p{font-size:.875rem}
/* Landing */
.hero{padding:6rem 0 5rem;text-align:center}
.hero-pill{display:inline-flex;align-items:center;gap:.5rem;background:rgba(39,39,42,.5);border:1px solid var(--border);border-radius:9999px;padding:.375rem 1rem;font-size:.875rem;color:var(--fg2);margin-bottom:1.5rem}
.hero h1{font-size:clamp(2.25rem,5.5vw,4.5rem);font-weight:700;letter-spacing:-.03em;line-height:1.1}
.hero h1 .muted{display:block;color:var(--fg2)}
.hero-sub{margin-top:1.5rem;max-width:42rem;font-size:1.125rem;color:var(--fg2);margin-left:auto;margin-right:auto}
.hero-btns{margin-top:2.5rem;display:flex;gap:1rem;justify-content:center;flex-wrap:wrap}
.stripe{border-top:1px solid var(--border);border-bottom:1px solid var(--border);background:rgba(39,39,42,.25);padding:5rem 0}
.sec-hdr{text-align:center;margin-bottom:4rem}
.sec-hdr h2{font-size:clamp(1.5rem,2.5vw,2rem);font-weight:600}
.sec-hdr p{margin-top:.5rem;color:var(--fg2)}
.step-icon{width:3rem;height:3rem;background:rgba(59,130,246,.1);border-radius:.5rem;display:flex;align-items:center;justify-content:center;margin-bottom:1rem}
.step-icon svg{color:var(--primary)}
.step-num{font-size:.8125rem;font-weight:500;color:var(--fg2);margin-bottom:.25rem}
.step-title{font-size:1.125rem;font-weight:600;margin-bottom:.5rem}
.step-desc{font-size:.875rem;color:var(--fg2)}
.feat-item{display:flex;flex-direction:column;align-items:center;text-align:center;padding:1.5rem}
.feat-item svg{color:var(--primary);margin-bottom:1rem}
.feat-title{font-weight:600;margin-bottom:.375rem}
.feat-desc{font-size:.875rem;color:var(--fg2)}
.cta-box{border:1px solid var(--border);background:rgba(24,24,27,.5);border-radius:1rem;padding:3rem;text-align:center}
.cta-box h2{font-size:clamp(1.5rem,2.5vw,2rem);font-weight:600}
.cta-box p{margin-top:1rem;color:var(--fg2);max-width:40rem;margin-left:auto;margin-right:auto}
.site-footer{border-top:1px solid var(--border);padding:2rem 0}
.footer-inner{display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem}
.footer-brand{display:flex;align-items:center;gap:.5rem;color:var(--fg2);font-size:.875rem}
.footer-copy{font-size:.75rem;color:var(--fg3)}
/* Misc */
.back-link{display:inline-flex;align-items:center;gap:.5rem;font-size:.875rem;color:var(--fg2);margin-bottom:1.5rem;transition:color .15s}
.back-link:hover{color:var(--fg)}
.summary-muted{background:rgba(39,39,42,.5);border-radius:.375rem;padding:.875rem 1rem;font-size:.875rem;color:var(--fg2)}
.conf-hi-hdr{font-size:.875rem;font-weight:500;color:#34d399;margin-bottom:.75rem}
.conf-lo-hdr{font-size:.875rem;font-weight:500;color:var(--fg2);margin-top:1rem;margin-bottom:.75rem}
.dot-amber{width:.5rem;height:.5rem;border-radius:50%;background:#f59e0b;flex-shrink:0}
.dot-green{width:.5rem;height:.5rem;border-radius:50%;background:#22c55e;flex-shrink:0}
.mt2{margin-top:.5rem}.mt3{margin-top:.75rem}.mt4{margin-top:1rem}.mt6{margin-top:1.5rem}
.mb4{margin-bottom:1rem}.mb6{margin-bottom:1.5rem}
/* Responsive */
@media(max-width:900px){.main-col,.two-col{grid-template-columns:1fr}}
@media(max-width:700px){.grid-2,.grid-3,.grid-4{grid-template-columns:1fr}.hero{padding:3rem 0 2.5rem}.cta-box{padding:1.5rem 1rem}}
@media(max-width:500px){.tabs-list{flex-wrap:wrap}.tab-btn{flex:1 1 auto}}
</style>
</head>
<body>
<div id="root"></div>
<script>
// ── SVG helpers ───────────────────────────────────────────────────────────────
function ic(d,w,h){
  return '<svg xmlns="http://www.w3.org/2000/svg" width="'+(w||16)+'" height="'+(h||16)+'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'+d+'</svg>';
}
var I={
  shield:  ic('<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',20,20),
  dash:    ic('<rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>'),
  folder:  ic('<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>'),
  folderOpen: ic('<path d="M5 19a2 2 0 0 1-2-2V7a2 2 0 0 1 2-2h4l2 2h4a2 2 0 0 1 2 2v1"/><path d="M5 19h14a2 2 0 0 0 2-2v-5a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2v5a2 2 0 0 1-2 2z"/>',24,24),
  arrowR:  ic('<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>'),
  arrowL:  ic('<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>'),
  camera:  ic('<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>'),
  camera24:ic('<path d="M14.5 4h-5L7 7H4a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-3l-2.5-3z"/><circle cx="12" cy="13" r="3"/>',24,24),
  brain:   ic('<path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96-.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-1.16z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96-.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-1.16z"/>',24,24),
  users:   ic('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',24,24),
  search:  ic('<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>'),
  clock:   ic('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
  clock24: ic('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',24,24),
  target:  ic('<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',24,24),
  alertC:  ic('<circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/>'),
  plus:    ic('<path d="M5 12h14"/><path d="M12 5v14"/>'),
  user:    ic('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>'),
  user20:  ic('<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>',20,20),
  mapPin:  ic('<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>'),
  chevR:   ic('<path d="m9 18 6-6-6-6"/>'),
  userP:   ic('<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" x2="19" y1="8" y2="14"/><line x1="22" x2="16" y1="11" y2="11"/>'),
  shirt:   ic('<path d="M20.38 3.46 16 2a4 4 0 0 1-8 0L3.62 3.46a2 2 0 0 0-1.34 2.23l.58 3.57a1 1 0 0 0 .99.84H6v10c0 1.1.9 2 2 2h8a2 2 0 0 0 2-2V10h2.15a1 1 0 0 0 .99-.84l.58-3.57a2 2 0 0 0-1.34-2.23z"/>'),
  backpack:ic('<path d="M4 20V10a8 8 0 0 1 16 0v10a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2z"/><path d="M9 20v-9a3 3 0 0 1 6 0v9"/><path d="M8 7a4 4 0 0 1 8 0"/>'),
  eye:     ic('<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>'),
  eye24:   ic('<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',24,24),
  route24: ic('<circle cx="6" cy="19" r="3"/><path d="M9 19h8.5a3.5 3.5 0 0 0 0-7h-11a3.5 3.5 0 0 1 0-7H15"/><circle cx="18" cy="5" r="3"/>',24,24),
  compass24:ic('<circle cx="12" cy="12" r="10"/><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"/>',24,24),
  video24: ic('<polygon points="23 7 16 12 23 17 23 7"/><rect width="15" height="14" x="1" y="5" rx="2" ry="2"/>',24,24),
  trendUp: ic('<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"/><polyline points="16 7 22 7 22 13"/>'),
  alertT:  ic('<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>'),
};

// ── Utilities ─────────────────────────────────────────────────────────────────
function esc(s){
  return String(s==null?'':s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;').replace(/'/g,'&#39;');
}
function fdate(iso){
  try{return new Date(iso).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});}
  catch(e){return String(iso);}
}
function fdatetime(iso){
  try{return new Date(iso).toLocaleString('en-US',{month:'short',day:'numeric',year:'numeric',hour:'numeric',minute:'2-digit'});}
  catch(e){return String(iso);}
}
function ftime(iso){
  try{return new Date(iso).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'});}
  catch(e){return String(iso);}
}
function pct(score){return Math.round(score*100)+'%';}

// ── API ───────────────────────────────────────────────────────────────────────
async function apiFetch(path,opts){
  opts=opts||{};
  var r=await fetch(path,Object.assign({headers:{'Content-Type':'application/json'}},opts));
  if(!r.ok){
    var e=await r.json().catch(function(){return{};});
    throw new Error(e.detail||'Error '+r.status);
  }
  return r.json();
}

// ── State ─────────────────────────────────────────────────────────────────────
var S={
  cases:null, casesErr:null, casesTab:'all',
  form:{subject_name:'',approximate_age:'',description:'',last_known_location:'',last_known_time:'',clothing_description:'',accessories:''},
  formErr:null, formSubmitting:false,
  wsId:null, wsCase:null, wsCaseErr:null, wsCaseLoading:false,
  wsSightings:[], wsTimeline:null, wsRecs:[],
  wsSearched:false, wsSearching:false, wsSearchErr:null,
  wsTlLoading:false, wsRecLoading:false,
};

// ── Router ────────────────────────────────────────────────────────────────────
function getRoute(){
  var hash=location.hash.slice(1)||'/';
  var parts=hash.split('/').filter(function(x){return x;});
  if(!parts.length) return {page:'landing'};
  if(parts[0]==='dashboard') return {page:'dashboard'};
  if(parts[0]==='cases'&&parts.length===1) return {page:'cases'};
  if(parts[0]==='cases'&&parts.length>=2) return {page:'workspace',id:parts[1]};
  return {page:'landing'};
}
function go(path){location.hash=path;}
window.go=go;

// ── Re-render ─────────────────────────────────────────────────────────────────
function render(){
  var r=getRoute();
  var html;
  if(r.page==='landing') html=renderLanding();
  else if(r.page==='dashboard') html=renderDashboard();
  else if(r.page==='cases') html=renderCases();
  else if(r.page==='workspace') html=renderWorkspace(r.id);
  else html=renderLanding();
  document.getElementById('root').innerHTML=html;
  bind();
}

// ── Shared Components ─────────────────────────────────────────────────────────
function navbar(){
  var hash=location.hash.slice(1)||'/';
  var isDash=hash.indexOf('/dashboard')===0;
  var isCases=hash.indexOf('/cases')===0;
  return '<header class="navbar"><div class="container">'
    +'<a href="#/" class="logo">'+I.shield+'<span>Trace AI</span></a>'
    +'<nav class="nav-links">'
    +'<a href="#/dashboard" class="nav-link'+(isDash?' active':'')+'">'+I.dash+' Dashboard</a>'
    +'<a href="#/cases" class="nav-link'+(isCases?' active':'')+'">'+I.folder+' Cases</a>'
    +'</nav></div></header>';
}

function statusBadge(s){
  var cls=s==='open'?'badge-amber':s==='closed'?'badge-green':'badge-blue';
  return '<span class="badge '+cls+'">'+esc(s.charAt(0).toUpperCase()+s.slice(1))+'</span>';
}
function confBadge(score){
  var cls=score>=0.8?'badge-emerald':score>=0.6?'badge-amber':'badge-red';
  var lbl=score>=0.8?'High':score>=0.6?'Medium':'Low';
  return '<span class="badge '+cls+'">'+I.trendUp+' '+pct(score)+' '+lbl+'</span>';
}
function urgBadge(lvl){
  if(!lvl) return '';
  var cls=lvl==='high'?'badge-orange':lvl==='medium'?'badge-amber':'badge-blue';
  return '<span class="badge '+cls+'">'+I.alertT+' '+esc(lvl.charAt(0).toUpperCase()+lvl.slice(1))+'</span>';
}

function skCard(){
  return '<div class="sk-card"><div class="sk sk-title"></div><div class="sk sk-line"></div><div class="sk sk-line w75"></div><div class="sk sk-line w60"></div></div>';
}
function skGrid(n){
  var h='<div class="grid-2 mt4">';
  for(var i=0;i<(n||3);i++) h+=skCard();
  return h+'</div>';
}
function empty(ico,title,desc){
  return '<div class="empty">'+ico+'<h3>'+esc(title)+'</h3><p>'+esc(desc)+'</p></div>';
}
function errBox(msg,fn){
  return '<div class="alert-err"><div class="alert-err-title">'+I.alertC+' Failed to load</div>'
    +'<p>'+esc(msg)+'</p>'
    +(fn?'<button class="btn btn-outline btn-sm" onclick="'+fn+'()">Try Again</button>':'')
    +'</div>';
}
function caseCard(c){
  return '<a href="#/cases/'+esc(c.id)+'" class="card case-card">'
    +'<div class="case-hdr"><span class="case-name">'+I.user+' '+esc(c.subject_name)+'</span>'+statusBadge(c.status)+'</div>'
    +'<div class="case-content">'
    +'<span class="case-date">Created '+fdate(c.created_at)+'</span>'
    +(c.description?'<p class="case-desc">'+esc(c.description)+'</p>':'')
    +(c.last_known_location?'<span class="case-loc">'+I.mapPin+' '+esc(c.last_known_location)+'</span>':'')
    +'<span class="case-hint">View details '+I.chevR+'</span>'
    +'</div></a>';
}

// ── Landing Page ──────────────────────────────────────────────────────────────
function renderLanding(){
  return navbar()
  +'<section class="hero"><div class="container" style="display:flex;flex-direction:column;align-items:center">'
  +'<div class="hero-pill">'+I.camera+' AI-Powered Surveillance Analysis</div>'
  +'<h1>Find Missing Persons<span class="muted">Faster</span></h1>'
  +'<p class="hero-sub">Trace AI is an investigative triage platform that helps authorities locate missing people by intelligently analyzing indexed security footage and providing prioritized leads.</p>'
  +'<div class="hero-btns"><button class="btn btn-primary btn-lg" onclick="go(\'/dashboard\')">Launch Dashboard '+I.arrowR+'</button></div>'
  +'</div></section>'

  +'<section class="stripe"><div class="container"><div style="max-width:48rem;margin:0 auto;text-align:center">'
  +'<h2 style="font-size:1.5rem;font-weight:600">The Problem</h2>'
  +'<p class="mt4" style="color:var(--fg2);line-height:1.7">When someone goes missing, every minute counts. Investigators often face <strong style="color:var(--fg)">hundreds of hours</strong> of surveillance footage from dozens of cameras. Manual review is time-consuming and error-prone, causing critical leads to be missed during the golden hours of a search.</p>'
  +'</div></div></section>'

  +'<section style="padding:5rem 0"><div class="container"><div class="sec-hdr"><h2>How It Works</h2><p>Three steps to accelerate your investigation</p></div>'
  +'<div class="grid-3">'
  +'<div class="card card-body"><div class="step-icon">'+I.users+'</div><div class="step-num">Step 1</div><div class="step-title">Input Case Details</div><p class="step-desc">Enter the missing person\'s description, last known location, time last seen, and any distinguishing characteristics.</p></div>'
  +'<div class="card card-body"><div class="step-icon">'+I.brain+'</div><div class="step-num">Step 2</div><div class="step-title">AI Searches Footage</div><p class="step-desc">Our AI analyzes indexed camera frames, matching against the subject\'s description to identify potential sightings.</p></div>'
  +'<div class="card card-body"><div class="step-icon">'+I.target+'</div><div class="step-num">Step 3</div><div class="step-title">Receive Prioritized Leads</div><p class="step-desc">Get ranked candidate sightings, a movement timeline, and recommendations for which cameras to check next.</p></div>'
  +'</div></div></section>'

  +'<section class="stripe"><div class="container"><div class="sec-hdr"><h2>Key Capabilities</h2></div>'
  +'<div class="grid-4">'
  +'<div class="feat-item">'+I.search+'<div class="feat-title">Intelligent Search</div><p class="feat-desc">AI-powered matching across indexed surveillance frames</p></div>'
  +'<div class="feat-item">'+I.clock24+'<div class="feat-title">Movement Timeline</div><p class="feat-desc">Chronological tracking of subject movements</p></div>'
  +'<div class="feat-item">'+I.target+'<div class="feat-title">Confidence Scoring</div><p class="feat-desc">Ranked results to prioritize high-probability leads</p></div>'
  +'<div class="feat-item">'+I.camera24+'<div class="feat-title">Camera Recommendations</div><p class="feat-desc">Guidance on which cameras to check next</p></div>'
  +'</div></div></section>'

  +'<section style="padding:5rem 0"><div class="container">'
  +'<div class="cta-box"><h2>Ready to accelerate your investigation?</h2>'
  +'<p>Start using Trace AI to reduce the time spent reviewing footage and focus on what matters—finding the missing person.</p>'
  +'<div class="mt6"><button class="btn btn-primary btn-lg" onclick="go(\'/dashboard\')">Launch Dashboard '+I.arrowR+'</button></div>'
  +'</div></div></section>'

  +'<footer class="site-footer"><div class="container"><div class="footer-inner">'
  +'<div class="footer-brand">'+I.shield+' Trace AI — Investigative Triage Platform</div>'
  +'<p class="footer-copy">Built for public safety and campus security teams.</p>'
  +'</div></div></footer>';
}

// ── Dashboard Page ────────────────────────────────────────────────────────────
function renderDashboard(){
  var cases=S.cases;
  var open=cases?cases.filter(function(c){return c.status==='open'||c.status==='investigating';})  :[];
  var closed=cases?cases.filter(function(c){return c.status==='closed';})  :[];

  var formHtml='<div class="card">'
    +'<div class="card-hdr"><div class="card-title">'+I.userP+' Create New Case</div>'
    +'<p class="card-sub">Enter details about the missing person to begin the investigation.</p></div>'
    +'<div class="card-body">'
    +(S.formErr?'<div class="alert-err mb4"><p style="margin:0">'+esc(S.formErr)+'</p></div>':'')
    +'<form id="caseForm" class="col gap-md">'
    +'<div class="grid-2">'
    +'<div class="form-group"><label class="form-label" for="f_name">Subject Name *</label>'
    +'<input id="f_name" class="input" name="subject_name" placeholder="Full name of missing person" value="'+esc(S.form.subject_name)+'" required></div>'
    +'<div class="form-group"><label class="form-label" for="f_age">Approximate Age</label>'
    +'<input id="f_age" class="input" name="approximate_age" type="number" placeholder="Estimated age" value="'+esc(S.form.approximate_age)+'" min="0" max="120"></div>'
    +'</div>'
    +'<div class="form-group"><label class="form-label" for="f_desc">Description *</label>'
    +'<textarea id="f_desc" class="textarea" name="description" placeholder="Physical description (height, build, hair color, distinguishing features...)" required rows="3">'+esc(S.form.description)+'</textarea></div>'
    +'<div class="grid-2">'
    +'<div class="form-group"><label class="form-label" for="f_loc">'+I.mapPin+' Last Known Location *</label>'
    +'<input id="f_loc" class="input" name="last_known_location" placeholder="Building, street, or area" value="'+esc(S.form.last_known_location)+'" required></div>'
    +'<div class="form-group"><label class="form-label" for="f_time">'+I.clock+' Last Seen Time *</label>'
    +'<input id="f_time" class="input" name="last_known_time" type="datetime-local" value="'+esc(S.form.last_known_time)+'"></div>'
    +'</div>'
    +'<div class="grid-2">'
    +'<div class="form-group"><label class="form-label" for="f_cloth">'+I.shirt+' Clothing</label>'
    +'<input id="f_cloth" class="input" name="clothing_description" placeholder="Shirt, pants, shoes..." value="'+esc(S.form.clothing_description)+'"></div>'
    +'<div class="form-group"><label class="form-label" for="f_acc">'+I.backpack+' Accessories</label>'
    +'<input id="f_acc" class="input" name="accessories" placeholder="Backpack, glasses, watch..." value="'+esc(S.form.accessories)+'"></div>'
    +'</div>'
    +'<button type="submit" class="btn btn-primary btn-full"'+(S.formSubmitting?' disabled="disabled"':'')+'>'+
      (S.formSubmitting?'<span class="spinner"></span> Creating Case...':I.plus+' Create Case')
    +'</button>'
    +'</form></div></div>';

  var rightHtml='<div class="space-y">'
    +'<section><div class="section-hdr"><span class="dot-amber"></span> Active Cases'
    +(cases&&open.length>0?' <span style="font-size:.875rem;font-weight:400;color:var(--fg2)">('+open.length+')</span>':'')+'</div>'
    +(cases===null?skGrid(2):S.casesErr?errBox(S.casesErr,'retryFetchCases')
      :open.length===0?empty(I.folderOpen,'No active cases','Create a new case using the form to start an investigation.')
      :'<div class="grid-2">'+open.map(caseCard).join('')+'</div>')
    +'</section>'
    +(cases!==null&&closed.length>0
      ?'<section><div class="section-hdr"><span class="dot-green"></span> Closed Cases'
        +' <span style="font-size:.875rem;font-weight:400;color:var(--fg2)">('+closed.length+')</span></div>'
        +'<div class="grid-2">'+closed.map(caseCard).join('')+'</div></section>'
      :'')
    +'</div>';

  return navbar()
    +'<main class="container page">'
    +'<div class="page-hdr"><h1>Investigation Dashboard</h1><p>Create new cases and manage ongoing investigations.</p></div>'
    +'<div class="main-col"><div>'+formHtml+'</div><div>'+rightHtml+'</div></div>'
    +'</main>';
}

// ── Cases Page ────────────────────────────────────────────────────────────────
function renderCases(){
  var cases=S.cases||[];
  var tab=S.casesTab;
  var all=cases;
  var open=cases.filter(function(c){return c.status==='open';});
  var inv=cases.filter(function(c){return c.status==='investigating';});
  var closed=cases.filter(function(c){return c.status==='closed';});
  var list=tab==='open'?open:tab==='investigating'?inv:tab==='closed'?closed:all;

  return navbar()
    +'<main class="container page">'
    +'<div class="row between mb6" style="align-items:flex-start;flex-wrap:wrap;gap:1rem">'
    +'<div class="page-hdr" style="margin-bottom:0"><h1>All Cases</h1><p>View and manage all investigation cases.</p></div>'
    +'<button class="btn btn-primary" onclick="go(\'/dashboard\')">'+I.plus+' New Case</button>'
    +'</div>'
    +(cases.length===0&&S.casesErr?errBox(S.casesErr,'retryFetchCases')
      :'<div class="tabs-list">'
      +'<button class="tab-btn'+(tab==='all'?' active':'')+'" onclick="switchTab(\'all\')">All ('+all.length+')</button>'
      +'<button class="tab-btn'+(tab==='open'?' active':'')+'" onclick="switchTab(\'open\')">Open ('+open.length+')</button>'
      +'<button class="tab-btn'+(tab==='investigating'?' active':'')+'" onclick="switchTab(\'investigating\')">Investigating ('+inv.length+')</button>'
      +'<button class="tab-btn'+(tab==='closed'?' active':'')+'" onclick="switchTab(\'closed\')">Closed ('+closed.length+')</button>'
      +'</div>'
      +(S.cases===null?skGrid(3)
        :list.length===0?empty(I.folderOpen,'No cases found','There are no cases matching this filter.')
        :'<div class="grid-3">'+list.map(caseCard).join('')+'</div>')
    )
    +'</main>';
}
window.switchTab=function(t){S.casesTab=t;render();};

// ── Case Workspace Page ───────────────────────────────────────────────────────
function renderWorkspace(id){
  // ── Case Summary ──
  var summaryHtml;
  if(S.wsCaseLoading){
    summaryHtml=skCard();
  } else if(S.wsCaseErr){
    summaryHtml=errBox(S.wsCaseErr,'retryLoadCase');
  } else if(S.wsCase){
    var c=S.wsCase;
    summaryHtml='<div class="card">'
      +'<div class="card-hdr row between" style="align-items:flex-start">'
      +'<div><div class="card-title">'+I.user20+' '+esc(c.subject_name)+'</div>'
      +'<p class="card-sub">Case opened '+fdatetime(c.created_at)+'</p></div>'
      +statusBadge(c.status)+'</div>'
      +'<div class="card-body col gap-md">'
      +(c.last_known_location
        ?'<div><div class="row gap-sm" style="font-size:.875rem;color:var(--fg2);margin-bottom:.25rem">'+I.mapPin+' Last Known Location</div>'
         +'<p style="font-weight:500">'+esc(c.last_known_location)+'</p></div>':'')
      +(c.description
        ?'<div><div style="font-size:.875rem;color:var(--fg2);margin-bottom:.25rem">Description</div>'
         +'<p style="font-size:.875rem;line-height:1.6">'+esc(c.description)+'</p></div>':'')
      +(c.clothing
        ?'<div><div class="row gap-sm" style="font-size:.875rem;color:var(--fg2);margin-bottom:.25rem">'+I.shirt+' Clothing</div>'
         +'<p style="font-size:.875rem">'+esc(c.clothing)+'</p></div>':'')
      +'<button class="btn btn-primary" style="align-self:flex-start" onclick="doSearch()"'
        +(S.wsSearching?' disabled="disabled"':'')+'>'+
        (S.wsSearching?'<span class="spinner"></span> Searching Footage...':I.search+' Run Footage Search')
      +'</button>'
      +(S.wsSearchErr?'<div class="alert-err mt3"><div class="alert-err-title">'+I.alertC+' Search Error</div><p>'+esc(S.wsSearchErr)+'</p></div>':'')
      +'</div></div>';
  } else {
    summaryHtml='';
  }

  // ── Timeline ──
  var tlHtml;
  if(S.wsTlLoading||S.wsSearching){
    tlHtml='<div class="mt4">'+skCard()+'</div>';
  } else {
    var tl=S.wsTimeline;
    var entries=tl&&tl.entries?[].concat(tl.entries).sort(function(a,b){return new Date(a.timestamp)-new Date(b.timestamp);}):[];
    tlHtml='<div class="card mt4">'
      +'<div class="card-hdr"><div class="card-title">'+I.route24+' Movement Timeline</div>'
      +'<p class="card-sub">Chronological tracking of subject movements</p></div>'
      +'<div class="card-body">';
    if(!S.wsSearched){
      tlHtml+=empty(I.clock24,'Timeline not available','Run a footage search to generate a movement timeline.');
    } else if(entries.length===0){
      tlHtml+=empty(I.route24,'No movement data','Not enough sightings to construct a movement timeline.');
    } else {
      if(tl.summary) tlHtml+='<div class="summary-muted mb4">'+esc(tl.summary)+'</div>';
      tlHtml+='<div>';
      entries.forEach(function(e,idx){
        var dot=e.similarity_score>=0.8?'#10b981':e.similarity_score>=0.6?'#f59e0b':'#ef4444';
        tlHtml+='<div class="tl-item">'
          +'<div class="tl-left"><div class="tl-dot" style="background:'+dot+'"></div>'
          +(idx<entries.length-1?'<div class="tl-line"></div>':'')+'</div>'
          +'<div class="tl-body">'
          +'<div class="tl-time"><span>'+ftime(e.timestamp)+'</span>'
          +'<span class="badge badge-muted">'+pct(e.similarity_score)+'</span></div>'
          +'<div class="tl-loc">'+I.mapPin+' '+esc(e.location)
          +' <span style="font-size:.75rem;color:var(--fg3)">('+esc(e.camera_name)+')</span></div>'
          +'<div class="tl-expl">'+esc(e.explanation)+'</div>'
          +'</div></div>';
      });
      tlHtml+='</div>';
    }
    tlHtml+='</div></div>';
  }

  // ── Sightings ──
  var sightHtml;
  if(S.wsSearching){
    sightHtml=skCard();
  } else {
    var sights=[].concat(S.wsSightings).sort(function(a,b){return b.similarity_score-a.similarity_score;});
    var hi=sights.filter(function(s){return s.similarity_score>=0.8;});
    var lo=sights.filter(function(s){return s.similarity_score<0.8;});
    sightHtml='<div class="card">'
      +'<div class="card-hdr"><div class="card-title">'+I.eye24+' Candidate Sightings</div>'
      +'<p class="card-sub">'+(sights.length>0
        ?sights.length+' potential match'+(sights.length!==1?'es':'')+' found &bull; '+hi.length+' high confidence'
        :'Potential matches will appear here after searching')+'</p></div>'
      +'<div class="card-body">';
    if(!S.wsSearched){
      sightHtml+=empty(I.camera24,'No search performed','Run a footage search to find potential sightings of the subject.');
    } else if(sights.length===0){
      sightHtml+=empty(I.eye24,'No sightings found','The search did not find any potential matches in the indexed footage.');
    } else {
      if(hi.length>0){sightHtml+='<div class="conf-hi-hdr">High Confidence Matches</div>';hi.forEach(function(s,i){sightHtml+=sightCard(s,i+1);});}
      if(lo.length>0){if(hi.length>0)sightHtml+='<div class="conf-lo-hdr">Other Matches</div>';lo.forEach(function(s,i){sightHtml+=sightCard(s,hi.length+i+1);});}
    }
    sightHtml+='</div></div>';
  }

  // ── Recommendations ──
  var recHtml;
  if(S.wsRecLoading||S.wsSearching){
    recHtml='<div class="mt4">'+skCard()+'</div>';
  } else {
    var recs=[].concat(S.wsRecs).sort(function(a,b){return a.priority-b.priority;});
    var hiRec=recs.filter(function(r){return r.urgency_level==='high';});
    recHtml='<div class="card mt4">'
      +'<div class="card-hdr"><div class="card-title">'+I.compass24+' Next Camera Recommendations</div>'
      +'<p class="card-sub">'+(recs.length>0
        ?recs.length+' camera'+(recs.length!==1?'s':'')+' to review &bull; '+hiRec.length+' high priority'
        :'Recommended cameras to check next')+'</p></div>'
      +'<div class="card-body">';
    if(!S.wsSearched){
      recHtml+=empty(I.video24,'No recommendations yet','Run a footage search to get camera recommendations.');
    } else if(recs.length===0){
      recHtml+=empty(I.compass24,'No recommendations','No additional cameras recommended at this time.');
    } else {
      recHtml+='<div class="space-y-xs">';
      recs.forEach(function(r){recHtml+=recCard(r);});
      recHtml+='</div>';
    }
    recHtml+='</div></div>';
  }

  return navbar()
    +'<main class="container page">'
    +(S.wsCaseErr?'<div class="alert-err mb4"><div class="alert-err-title">'+I.alertC+' Error loading case</div><p>'+esc(S.wsCaseErr)+'</p></div>':'')
    +'<a href="#/dashboard" class="back-link">'+I.arrowL+' Back to Dashboard</a>'
    +'<div class="two-col"><div>'+summaryHtml+tlHtml+'</div><div>'+sightHtml+recHtml+'</div></div>'
    +'</main>';
}

function sightCard(s,rank){
  var hi=s.similarity_score>=0.8;
  return '<div class="card sight-card'+(hi?' mt2':' mt2')+'" style="'+(hi?'border-color:rgba(5,150,105,.3)':'')+'">'
    +'<div class="sight-thumb">'+I.camera24
    +'<div class="sight-rank">#'+rank+'</div></div>'
    +'<div class="sight-details">'
    +'<div class="sight-row"><div class="sight-cam">'+I.camera+' '+esc(s.camera_id)+'</div>'+confBadge(s.similarity_score)+'</div>'
    +'<div class="sight-meta">'
    +'<span class="sight-item">'+I.mapPin+' '+esc(s.location)+'</span>'
    +'<span class="sight-item">'+I.clock+' '+fdatetime(s.timestamp)+'</span>'
    +'</div>'
    +'<div class="sight-expl">'+esc(s.explanation)+'</div>'
    +'</div></div>';
}

function recCard(r){
  var hi=r.urgency_level==='high';
  return '<div class="card rec-card" style="'+(hi?'border-color:rgba(234,88,12,.3)':'')+'">'
    +'<div class="rec-hdr"><div class="rec-name">'+I.camera+' '+esc(r.camera_name)+'</div>'+urgBadge(r.urgency_level)+'</div>'
    +'<div class="rec-loc">'+I.mapPin+' '+esc(r.location)+'</div>'
    +'<div class="rec-reason">'+esc(r.reason)+'</div>'
    +(r.review_before?'<div class="rec-deadline">'+I.clock+' Review before: '+fdatetime(r.review_before)+'</div>':'')
    +'</div>';
}

// ── Event Binding ─────────────────────────────────────────────────────────────
function bind(){
  var form=document.getElementById('caseForm');
  if(form){
    form.addEventListener('input',function(ev){
      var n=ev.target.name;
      if(n) S.form[n]=ev.target.value;
    });
    form.addEventListener('submit',function(ev){
      ev.preventDefault();
      submitCase();
    });
  }
}

// ── Globals for onclick ───────────────────────────────────────────────────────
window.switchTab=function(t){S.casesTab=t;render();};
window.retryFetchCases=function(){S.cases=null;S.casesErr=null;loadCases();};
window.retryLoadCase=function(){if(S.wsId)initWorkspace(S.wsId,true);};
window.doSearch=function(){if(!S.wsSearching)runSearch();};

// ── Data Operations ───────────────────────────────────────────────────────────
async function loadCases(){
  S.cases=null;S.casesErr=null;
  render();
  try{S.cases=await apiFetch('/cases');}
  catch(e){S.casesErr=e.message;S.cases=[];}
  render();
}

async function initWorkspace(id,force){
  if(!force&&S.wsId===id&&S.wsCase!==null) return;
  S.wsId=id;S.wsCase=null;S.wsCaseErr=null;S.wsCaseLoading=true;
  S.wsSightings=[];S.wsTimeline=null;S.wsRecs=[];
  S.wsSearched=false;S.wsSearching=false;S.wsSearchErr=null;
  render();
  try{S.wsCase=await apiFetch('/cases/'+id);}
  catch(e){S.wsCaseErr=e.message;}
  S.wsCaseLoading=false;
  render();
}

async function runSearch(){
  var id=S.wsId;
  S.wsSearching=true;S.wsSearchErr=null;S.wsSightings=[];S.wsTimeline=null;S.wsRecs=[];
  S.wsTlLoading=true;S.wsRecLoading=true;
  render();
  try{
    S.wsSightings=await apiFetch('/cases/'+id+'/search',{method:'POST'});
    S.wsSearched=true;S.wsSearching=false;
    render();
    var res=await Promise.all([
      apiFetch('/cases/'+id+'/timeline').catch(function(){return null;}),
      apiFetch('/cases/'+id+'/recommendations').catch(function(){return[];})
    ]);
    S.wsTimeline=res[0];S.wsRecs=res[1];
    S.wsTlLoading=false;S.wsRecLoading=false;
  }catch(e){
    S.wsSearchErr=e.message;S.wsSearching=false;S.wsTlLoading=false;S.wsRecLoading=false;
  }
  render();
}

async function submitCase(){
  if(S.formSubmitting) return;
  var name=S.form.subject_name;
  if(!name||!name.trim()){S.formErr='Subject name is required.';render();return;}
  S.formSubmitting=true;S.formErr=null;
  render();
  try{
    var payload={
      subject_name:S.form.subject_name.trim(),
      description:S.form.description||undefined,
      last_known_location:S.form.last_known_location||undefined,
      clothing:S.form.clothing_description||undefined,
    };
    var c=await apiFetch('/cases',{method:'POST',body:JSON.stringify(payload)});
    S.formSubmitting=false;
    S.form={subject_name:'',approximate_age:'',description:'',last_known_location:'',last_known_time:'',clothing_description:'',accessories:''};
    S.cases=null;
    go('/cases/'+c.id);
  }catch(e){
    S.formErr=e.message;S.formSubmitting=false;
    render();
  }
}

// ── Bootstrap ─────────────────────────────────────────────────────────────────
function onNav(){
  var r=getRoute();
  render();
  if(r.page==='dashboard'||r.page==='cases'){
    if(S.cases===null) loadCases();
  } else if(r.page==='workspace'&&r.id){
    initWorkspace(r.id);
  }
}

window.addEventListener('hashchange',onNav);
window.addEventListener('DOMContentLoaded',onNav);
</script>
</body>
</html>"""


# =============================================================================
# FastAPI Application
# =============================================================================
application = FastAPI(
    title="Trace AI",
    description="Missing-person investigative triage backend.",
    version="0.1.0",
)

# CORS: defaults to wildcard for ease of local development.
# Set CORS_ORIGINS env var (comma-separated) to restrict in production.
_cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
application.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

application.include_router(router)


@application.get("/", response_class=HTMLResponse, include_in_schema=False)
async def frontend() -> str:
    """Serve the self-contained SPA frontend."""
    return _FRONTEND


@application.get("/health", tags=["system"])
def health_check() -> dict:
    return {"status": "ok", "service": "trace-ai"}


if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(application, host=host, port=port)
