import json,re,glob,os,sys
terms_all=json.load(open("/tmp/glos_terms.json",encoding="utf-8"))
# filtrează: fără paranteze (ambigue), lungime rezonabilă
terms={t:a for t,a in terms_all.items() if "(" not in t and len(t)>=8}
TERMS=sorted(terms, key=lambda s:-len(s))  # cele lungi întâi
DIAC=r'\wăâîșțĂÂÎȘȚ'
def linkify(body, cap=6):
    parts=re.split(r'(<[^>]+>)', body)
    ina=0; inblock=False; used=set(); cnt=0; out=[]
    for p in parts:
        if p.startswith('<'):
            tl=p.lower()
            if tl.startswith('<a'): ina+=1
            elif tl.startswith('</a'): ina=max(0,ina-1)
            if re.match(r'<(p|li)[ >]',tl): inblock=True
            elif re.match(r'</(p|li)>',tl): inblock=False
            out.append(p)
        else:
            if inblock and ina==0 and cnt<cap:
                for term in TERMS:
                    if term in used or cnt>=cap: continue
                    m=re.compile(r'(?<!['+DIAC+r'])('+re.escape(term)+r')(?!['+DIAC+r'])',re.I).search(p)
                    if m:
                        p=p[:m.start()]+f'<a class="gloss-link" href="{terms[term]}">{m.group(1)}</a>'+p[m.end():]
                        used.add(term); cnt+=1
            out.append(p)
    return ''.join(out), cnt
def process(f, write):
    t=open(f,encoding="utf-8").read()
    if 'gloss-link' in t: return 0
    m=re.search(r'(</h1>)(.*?)(<div class="disc")', t, re.S)
    if not m: return 0
    newbody,cnt=linkify(m.group(2))
    if cnt:
        t2=t[:m.start(2)]+newbody+t[m.end(2):]
        if write: open(f,"w",encoding="utf-8").write(t2)
    return cnt
if __name__=="__main__":
    mode=sys.argv[1] if len(sys.argv)>1 else "test"
    files=sorted(glob.glob("docs/articole/*.html"))
    if mode=="test":
        for f in files[:3]:
            t=open(f,encoding="utf-8").read()
            m=re.search(r'(</h1>)(.*?)(<div class="disc")',t,re.S)
            nb,cnt=linkify(m.group(2))
            print(f"\n### {os.path.basename(f)} — {cnt} linkuri")
            for lm in re.finditer(r'<a class="gloss-link"[^>]*>([^<]+)</a>',nb): print("   →",lm.group(1))
    else:
        tot=sum(process(f,True) for f in files)
        print("linkuri glosar adăugate:",tot,"în articole")
