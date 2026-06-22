# -*- coding: utf-8 -*-
"""Nanobrowser v2.0 - LLM paid+free, MCP 19, A-Share, Hacker"""
import tkinter as tk
from tkinter import ttk, scrolledtext as st
import threading, json, time, os, re
import urllib.request as ur, urllib.parse as up

BG="#0d1117";C1="#161b22";C2="#1f2937";FG="#c9d1d9"
AC="#238636";RD="#f85149";WN="#d29922";GR="#3fb950";T3="#8b949e"

LLM={"ollama":{"name":"Ollama Free","ok":False,"c":0,"t":0,"cost":0},
"deepseek":{"name":"DeepSeek V3","ok":False,"c":0,"t":0,"cost":0},
"glm":{"name":"GLM-4 Flash","ok":False,"c":0,"t":0,"cost":0},
"openai":{"name":"GPT-4o-mini","ok":False,"c":0,"t":0,"cost":0}}

MCP=["scanner","audit","auto-fix","self-evolve","deepseek-analyzer",
"cloud-llm","memory","global-memory","intelligent-scheduler",
"bounty-hunter","stress-test","desktop-control","mirror-deploy",
"rustdesk","email-watcher","halo-cms","mcp-router",
"auto_trade","ai_trade"]

CAPS=MCP*2+MCP[:13]

DESK=["screenshot","browser_open","window_maximize","keyboard_type",
"keyboard_hotkey","mouse_click","process_list","process_kill",
"window_focus","volume_control","system_lock"]

def ag(p,cb):
  def rn():
    try:r=ur.urlopen(ur.Request("http://127.0.0.1:8765"+p),timeout=8);cb(json.loads(r.read()))
    except Exception as e:cb({"ok":False,"error":str(e)})
  threading.Thread(target=rn,daemon=True).start()

def ap(p,b,cb):
  def rn():
    try:d=json.dumps(b).encode();r=ur.urlopen(ur.Request("http://127.0.0.1:8765"+p,data=d,headers={"Content-Type":"application/json"}),timeout=8);cb(json.loads(r.read()))
    except Exception as e:cb({"ok":False,"error":str(e)})
  threading.Thread(target=rn,daemon=True).start()

def ckllm():
  try:r=ur.urlopen("http://127.0.0.1:11434/api/tags",timeout=3);LLM["ollama"]["ok"]=bool(json.loads(r.read()).get("models"))
  except:LLM["ollama"]["ok"]=False
  for k in["deepseek","glm","openai"]:LLM[k]["ok"]=bool(os.environ.get(k.upper()+"_API_KEY",""))

def llmcall(pid,prompt,cb):
  p=LLM.get(pid)
  if not p:return cb("PF")
  def rn():
    try:
      if pid=="ollama":
        bd=json.dumps({"model":"qwen2.5:0.5b","messages":[{"role":"user","content":prompt}],"stream":False}).encode()
        rq=ur.Request("http://127.0.0.1:11434/api/chat",data=bd,headers={"Content-Type":"application/json"})
        with ur.urlopen(rq,timeout=120)as r:d=json.loads(r.read())
        t=d.get("message",{}).get("content","");p["c"]+=1;p["t"]+=len(t.split());cb(t)
      elif pid=="deepseek":
        k=os.environ.get("DEEPSEEK_API_KEY","")
        bd=json.dumps({"model":"deepseek-chat","messages":[{"role":"user","content":prompt}],"max_tokens":1024}).encode()
        rq=ur.Request("https://api.deepseek.com/v1/chat/completions",data=bd,headers={"Authorization":"Bearer "+k,"Content-Type":"application/json"})
        with ur.urlopen(rq,timeout=120)as r:d=json.loads(r.read())
        t=d["choices"][0]["message"]["content"];tk=d.get("usage",{}).get("total_tokens",0)
        p["c"]+=1;p["t"]+=tk;p["cost"]+=tk*.001/1000;cb(t)
      else:cb("NA")
    except Exception as e:cb("E:"+str(e)[:80])
  threading.Thread(target=rn,daemon=True).start()

class NB:
  def __init__(self):
    self.r=tk.Tk();self.r.title("Nanobrowser v2.0");self.r.geometry("1200x750")
    self.r.minsize(850,500);self.r.configure(bg=BG)
    self.hist=[];self.hi=-1;self.curl="";self.p={};self._ui();ckllm();self._tk()

  def _ui(self):
    tb=tk.Frame(self.r,bg=C1,height=38);tb.pack(fill=tk.X);tb.pack_propagate(False)
    nf=tk.Frame(tb,bg=C1);nf.pack(side=tk.LEFT,padx=4,pady=3)
    bs={"bg":C1,"fg":FG,"bd":0,"font":("Segoe UI",11),"cursor":"hand2","activebackground":C2,"activeforeground":FG}
    for t,cmd in[("[<]",self.gb),("[>]",self.gf),("[X]",self.rl),("[H]",self.gh)]:tk.Button(nf,text=t,width=3,command=cmd,**bs).pack(side=tk.LEFT,padx=1)
    uf=tk.Frame(tb,bg=C1);uf.pack(side=tk.LEFT,fill=tk.X,expand=True,padx=4,pady=5)
    self.uv=tk.StringVar();self.ub=tk.Entry(uf,textvariable=self.uv,bg=BG,fg=FG,insertbackground=FG,font=("Consolas",11),bd=1,relief="solid")
    self.ub.pack(side=tk.LEFT,fill=tk.X,expand=True,ipady=2);self.ub.bind("<Return>",lambda e:self.nav(self.uv.get()))
    tk.Button(uf,text="Go",width=3,bg=AC,fg="white",bd=0,font=("Segoe UI",10,"bold"),command=lambda:self.nav(self.uv.get())).pack(side=tk.RIGHT,padx=(4,0),ipady=2)
    self.sb=tk.Frame(self.r,bg=C1,width=160);self.sb.pack(side=tk.LEFT,fill=tk.Y);self.sb.pack_propagate(False)
    tk.Label(self.sb,text="NB v2.0",bg=C1,fg=AC,font=("Segoe UI",11,"bold")).pack(pady=(10,2))
    self.sbtn={}
    for nm,pn in[("Dash","d"),("LLM","l"),("Share","a"),("Hack","h"),("MCP","m"),("Desk","k")]:
      b=tk.Button(self.sb,text=nm,bg=C1,fg=T3,font=("Segoe UI",9),bd=0,anchor="w",cursor="hand2",activebackground=C2,activeforeground=FG,command=lambda v=pn:self._sh(v))
      b.pack(fill=tk.X,padx=4,pady=1,ipady=5);self.sbtn[pn]=b
    self.ct=tk.Frame(self.r,bg=BG);self.ct.pack(side=tk.LEFT,fill=tk.BOTH,expand=True)
    for pn in["d","l","a","h","m","k"]:f=tk.Frame(self.ct,bg=BG);self.p[pn]=f
    self._bd();self._bl();self._ba();self._bh();self._bm();self._bk();self._sh("d")
    sb=tk.Frame(self.r,bg=C2,height=20);sb.pack(fill=tk.X,side=tk.BOTTOM);sb.pack_propagate(False)
    self.stl=tk.Label(sb,text="Ready",bg=C2,fg=T3,font=("Segoe UI",8),anchor="w");self.stl.pack(side=tk.LEFT,padx=8)

  def _sh(self,pn):
    for k,f in self.p.items():f.pack_forget()
    self.p[pn].pack(fill=tk.BOTH,expand=True)
    for k,b in self.sbtn.items():b.configure(fg=AC if k==pn else T3)
    if pn=="l":self._rl()
    if pn=="a":self._ra()
    if pn=="h":self._rh()
    if pn=="m":self._rm()
    if pn=="k":self._rk()

  def _bd(self):
    p=self.p["d"];r1=tk.Frame(p,bg=BG);r1.pack(fill=tk.BOTH,expand=True);r2=tk.Frame(p,bg=BG);r2.pack(fill=tk.BOTH,expand=True)
    def c(parent,t):
      f=tk.Frame(parent,bg=C1);f.pack(side=tk.LEFT,fill=tk.BOTH,expand=True,padx=3,pady=3)
      tk.Label(f,text=t,bg=C1,fg=FG,font=("Segoe UI",10,"bold")).pack(padx=8,pady=(5,1))
      bd=tk.Frame(f,bg=C1);bd.pack(fill=tk.BOTH,expand=True,padx=8,pady=5);return bd
    b=c(r1,"LLM");self.d_llm=tk.Label(b,bg=C1,fg=FG,font=("Consolas",9),anchor="nw",justify="left");self.d_llm.pack(fill=tk.BOTH)
    b=c(r1,"Trade");self.d_tr=tk.Label(b,bg=C1,fg=FG,font=("Consolas",9),anchor="nw",justify="left");self.d_tr.pack(fill=tk.BOTH)
    b=c(r2,"System");self.d_sy=tk.Label(b,bg=C1,fg=FG,font=("Consolas",9),anchor="nw",justify="left");self.d_sy.pack(fill=tk.BOTH)
    b=c(r2,"MCP");self.d_mc=tk.Label(b,bg=C1,fg=FG,font=("Consolas",7),anchor="nw",justify="left");self.d_mc.pack(fill=tk.BOTH)
  def _bl(self):
    p=self.p["l"];hd=tk.Frame(p,bg=C1,height=28);hd.pack(fill=tk.X,padx=8,pady=(8,4));hd.pack_propagate(False)
    tk.Label(hd,text="LLM Providers",bg=C1,fg=FG,font=("Segoe UI",11,"bold")).pack(side=tk.LEFT)
    self.l_g=tk.Frame(p,bg=BG);self.l_g.pack(fill=tk.X,padx=8,pady=2)
    pf=tk.Frame(p,bg=BG);pf.pack(fill=tk.X,padx=8)
    self.l_in=tk.Text(pf,bg=C2,fg=FG,font=("Segoe UI",10),height=3,wrap=tk.WORD);self.l_in.pack(fill=tk.X,pady=2)
    self.l_in.insert(1.0,"Enter prompt...")
    tk.Button(pf,text="Send (auto)",bg=AC,fg="white",font=("Segoe UI",9,"bold"),bd=0,command=self._ls).pack(fill=tk.X,ipady=4,pady=2)
    self.l_o=st.ScrolledText(p,bg=C2,fg=FG,font=("Consolas",9),wrap=tk.WORD);self.l_o.pack(fill=tk.BOTH,expand=True,padx=8,pady=(4,8))

  def _rl(self):
    ckllm();[w.destroy()for w in self.l_g.winfo_children()]
    for i,kv in enumerate(LLM.items()):
      k,v=kv;c=GR if v["ok"]else RD;f=tk.Frame(self.l_g,bg=C1 if i%2==0 else BG);f.pack(fill=tk.X,pady=1)
      tk.Label(f,text="*"if v["ok"]else"o",bg=f["bg"],fg=c,font=("Segoe UI",12)).pack(side=tk.LEFT,padx=(8,4))
      tk.Label(f,text=v["name"][:16],bg=f["bg"],fg=FG,font=("Segoe UI",9,"bold"),width=16,anchor="w").pack(side=tk.LEFT)
      tk.Label(f,text="C:"+str(v["c"]),bg=f["bg"],fg=T3,font=("Segoe UI",7)).pack(side=tk.LEFT,padx=4)
      tk.Label(f,text="T:"+str(v["t"]),bg=f["bg"],fg=T3,font=("Segoe UI",7)).pack(side=tk.LEFT,padx=4)
      tk.Label(f,text="$"+str(round(v["cost"],4)),bg=f["bg"],fg=AC if v["cost"]>0 else T3,font=("Segoe UI",7)).pack(side=tk.LEFT,padx=4)
      if v["ok"]:tk.Button(f,text="Test",bg=AC,fg="white",font=("Segoe UI",7),bd=0,command=lambda k=k:self._lt(k)).pack(side=tk.RIGHT,padx=4)

  def _lt(self,k):
    self.l_o.insert(tk.END,chr(10)+"[Test "+k+"]"+chr(10));self.l_o.see(tk.END);llmcall(k,"Hello!",lambda t:self.l_o.insert(tk.END,t+chr(10)))

  def _ls(self):
    t=self.l_in.get(1.0,tk.END).strip()
    if not t or"Enter"in t:return
    N=chr(10);self.l_o.insert(tk.END,N+"[You] "+t[:100]+N);self.l_o.see(tk.END)
    for k,v in LLM.items():
      if v["ok"]:self.l_o.insert(tk.END,"["+k+"]..."+N);self.l_o.see(tk.END);llmcall(k,t,lambda x:self.l_o.insert(tk.END,x+N+N));return
    self.l_o.insert(tk.END,"[No active provider]"+N)
  def _ba(self):
    p=self.p["a"];hd=tk.Frame(p,bg=C1,height=28);hd.pack(fill=tk.X,padx=8,pady=(8,4));hd.pack_propagate(False)
    tk.Label(hd,text="A-Share",bg=C1,fg=FG,font=("Segoe UI",11,"bold")).pack(side=tk.LEFT)
    self.a_t=st.ScrolledText(p,bg=C2,fg=FG,font=("Consolas",10),wrap=tk.WORD);self.a_t.pack(fill=tk.BOTH,expand=True,padx=8,pady=(4,8))
  def _ra(self):ag("/api/market",self._sm)
  def _sm(self,d):
    self.a_t.delete(1.0,tk.END)
    if d.get("ok"):
      for i in d.get("indices",[]):pct=i.get("pct",0);s="+"if pct>=0 else"";self.a_t.insert(tk.END,"%-12s %10.2f %s%.2f%%"+chr(10)%(i.get("name",""),i.get("price",0),s,pct))
    else:self.a_t.insert(tk.END,d.get("error","N/A")+chr(10))

  def _bh(self):
    p=self.p["h"];hd=tk.Frame(p,bg=C1,height=28);hd.pack(fill=tk.X,padx=8,pady=(8,4));hd.pack_propagate(False)
    tk.Label(hd,text="Hacker 49",bg=C1,fg=FG,font=("Segoe UI",11,"bold")).pack(side=tk.LEFT)
    cv=tk.Canvas(p,bg=BG);cv.pack(fill=tk.BOTH,expand=True,padx=8);sc=tk.Scrollbar(p,orient=tk.VERTICAL,command=cv.yview);sc.pack(side=tk.RIGHT,fill=tk.Y)
    cv.configure(yscrollcommand=sc.set);self.hg=tk.Frame(cv,bg=BG);cv.create_window((0,0),window=self.hg,anchor="nw")
    self.hg.bind("<Configure>",lambda e:cv.configure(scrollregion=cv.bbox("all")))
    self.hl=st.ScrolledText(p,height=5,bg=C2,fg=FG,font=("Consolas",9),wrap=tk.WORD);self.hl.pack(fill=tk.X,padx=8,pady=(4,8))
  def _rh(self):
    [w.destroy()for w in self.hg.winfo_children()];row=tk.Frame(self.hg,bg=BG);row.pack(fill=tk.X,pady=1);col=0
    for c in CAPS:
      if col>=5:row=tk.Frame(self.hg,bg=BG);row.pack(fill=tk.X,pady=1);col=0
      tk.Button(row,text=c[:14],bg=C2,fg=FG,font=("Segoe UI",7),bd=1,relief="solid",cursor="hand2",activebackground=AC,command=lambda cid=c:self._hx(cid)).pack(side=tk.LEFT,padx=1,pady=1);col+=1
  def _hx(self,cid):
    self.hl.insert(1.0,"Run: "+cid+chr(10))
    ap("/api/hacker/exec",{"id":cid,"action":"run"},lambda d:self.hl.insert(1.0,"["+("OK"if d.get("ok")else"FAIL")+"] "+cid+chr(10)))

  def _bm(self):
    p=self.p["m"];hd=tk.Frame(p,bg=C1,height=28);hd.pack(fill=tk.X,padx=8,pady=(8,4));hd.pack_propagate(False)
    tk.Label(hd,text="MCP 19",bg=C1,fg=FG,font=("Segoe UI",11,"bold")).pack(side=tk.LEFT)
    self.mg=tk.Frame(p,bg=BG);self.mg.pack(fill=tk.BOTH,expand=True,padx=8,pady=4)
    self.ml=st.ScrolledText(p,height=4,bg=C2,fg=FG,font=("Consolas",9),wrap=tk.WORD);self.ml.pack(fill=tk.X,padx=8,pady=(4,8))
  def _rm(self):
    [w.destroy()for w in self.mg.winfo_children()];row=tk.Frame(self.mg,bg=BG);row.pack(fill=tk.X,pady=1);col=0
    for s in MCP:
      if col>=3:row=tk.Frame(self.mg,bg=BG);row.pack(fill=tk.X,pady=1);col=0
      f=tk.Frame(row,bg=C2);f.pack(side=tk.LEFT,fill=tk.X,expand=True,padx=3,pady=3)
      tk.Label(f,text="*",bg=C2,fg=GR,font=("Segoe UI",10)).pack(side=tk.LEFT,padx=(6,4))
      tk.Label(f,text=s[:14],bg=C2,fg=FG,font=("Segoe UI",8,"bold")).pack(side=tk.LEFT);col+=1

  def _bk(self):
    p=self.p["k"];hd=tk.Frame(p,bg=C1,height=28);hd.pack(fill=tk.X,padx=8,pady=(8,4));hd.pack_propagate(False)
    tk.Label(hd,text="Desktop",bg=C1,fg=FG,font=("Segoe UI",11,"bold")).pack(side=tk.LEFT)
    self.kg=tk.Frame(p,bg=BG);self.kg.pack(fill=tk.X,padx=8,pady=4)
    for nm in DESK:tk.Button(self.kg,text=nm[:12],bg=C2,fg=FG,font=("Segoe UI",9),bd=1,relief="solid",cursor="hand2",activebackground=AC,command=lambda c=nm:self._kx(c)).pack(side=tk.LEFT,padx=2,pady=3)
    self.kl=st.ScrolledText(p,bg=C2,fg=FG,font=("Consolas",9),wrap=tk.WORD);self.kl.pack(fill=tk.BOTH,expand=True,padx=8,pady=(4,8))
  def _rk(self):pass
  def _kx(self,cid):
    self.kl.insert(1.0,"Run: "+cid+chr(10))
    ap("/api/hacker/exec",{"id":cid,"action":"run"},lambda d:self.kl.insert(1.0,"["+("OK"if d.get("ok")else"FAIL")+"] "+cid+chr(10)))
  def _tk(self):
    def rd():ag("/api/dashboard",self._up)
    rd();self.r.after(5000,self._tk)
  def _up(self,d):
    if not d:return
    s="";m="";N=chr(10)
    for k,v in LLM.items():s+=N+"  "+v["name"][:14]+": "+("ON"if v["ok"]else"OFF")+" C:"+str(v["c"])+" T:"+str(v["t"])
    self.d_llm.config(text="Tokens:"+s)
    td=d.get("trade",{});acct=td.get("account",{})
    self.d_tr.config(text="Cash:$"+str(acct.get("cash",0))+" P&L:$"+str(acct.get("pnl",0)))
    sy=d.get("system",{})
    self.d_sy.config(text="CPU:"+str(round(sy.get("cpu",0),1))+"% MEM:"+str(round(sy.get("memory",0),1))+"%")
    srvs=(d.get("mcp",{})or{}).get("servers",[])or[]
    for sv in srvs:m+="* "+str(sv)+N if isinstance(sv,str)else"* "+sv.get("id","")+N
    self.d_mc.config(text=m or"No MCP");self.stl.config(text=str(len(srvs))+" MCP")

  def gb(self):
    if self.hi>0:self.hi-=1;self._lh()
  def gf(self):
    if self.hi<len(self.hist)-1:self.hi+=1;self._lh()
  def _lh(self):e=self.hist[self.hi];self._f(e["url"],False)
  def gh(self):self.nav("http://localhost:8765/dashboard")
  def rl(self):
    if self.curl:self._f(self.curl,False)
  def nav(self,url):
    if not url:return
    if not url.startswith("http"):
      if"."in url and" "not in url:url="https://"+url
      else:url="https://google.com/search?q="+up.quote(url)
    self._f(url)
  def _f(self,url,ah=True):
    self.uv.set(url);self.curl=url;self.stl.config(text="Loading...")
    def dn():
      try:
        rq=ur.Request(url,headers={"User-Agent":"Nanobrowser/2.0"})
        with ur.urlopen(rq,timeout=15)as r:ct=r.headers.get("Content-Type","");data=r.read()
        if"json"in ct:
          try:text=json.dumps(json.loads(data),indent=2,ensure_ascii=False)
          except:text=data.decode("utf-8","replace")
        else:text=data.decode("utf-8","replace")
        self.r.after(0,lambda:self._r(text,url,ct,ah))
      except Exception as e:self.r.after(0,lambda e=e:self._e(url,str(e)))
    threading.Thread(target=dn,daemon=True).start()
  def _r(self,text,url,ct,ah):
    if"br"not in self.p:bf=tk.Frame(self.ct,bg=BG);self.p["br"]=bf;self.bct=st.ScrolledText(bf,bg=BG,fg=FG,font=("Consolas",10),wrap=tk.WORD,padx=16,pady=12);self.bct.pack(fill=tk.BOTH,expand=True)
    self._sh("br");self.bct.configure(state=tk.NORMAL);self.bct.delete(1.0,tk.END)
    if"text/html"in ct:self._ht(text)
    else:self._tt(text)
    self.bct.configure(state=tk.DISABLED);self.bct.see(1.0)
    if ah:self.hist=self.hist[:self.hi+1];self.hist.append({"url":url});self.hi=len(self.hist)-1
    self.stl.config(text="Done");self.r.title("NB - "+url[:60])
  def _ht(self,html):
    html=re.sub(r"<script[^>]*>.*?</script>","",html,flags=re.I|re.S)
    html=re.sub(r"<style[^>]*>.*?</style>","",html,flags=re.I|re.S)
    NL=chr(10);text=re.sub(r"<br[^>]*>",NL,html,flags=re.I);text=re.sub(r"<p[^>]*>",NL+NL,text,flags=re.I)
    text=re.sub(r"</p>","",text,flags=re.I);text=re.sub(r"</?div[^>]*>",NL,text,flags=re.I)
    text=re.sub(r"<li[^>]*>",NL+"- ",text,flags=re.I);text=re.sub(r"</li>","",text,flags=re.I)
    text=re.sub(r"<[^>]+>","",text);text=re.sub(r"&nbsp;"," ",text);text=re.sub(r"&lt;","<",text)
    text=re.sub(r"&gt;",">",text);text=re.sub(r"&amp;","&",text);text=text.strip()
    for line in text.split(NL):self.bct.insert(tk.END,line+NL if line.strip()else NL)
  def _tt(self,text):
    for line in text.split(chr(10)):self.bct.insert(tk.END,line+chr(10))
  def _e(self,url,err):
    if"br"in self.p:self._sh("br");self.bct.configure(state=tk.NORMAL);self.bct.delete(1.0,tk.END)
    self.bct.insert(tk.END,"ERR"+chr(10)+url+chr(10)+chr(10)+err+chr(10));self.bct.configure(state=tk.DISABLED);self.stl.config(text="Error")
  def run(self):self.r.mainloop()

def main():b=NB();b.r.after(1000,lambda:b.nav("http://localhost:8765/dashboard"));b.run()
if __name__=="__main__":main()
