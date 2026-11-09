import io,json,streamlit as st
from pypdf import PdfReader
from docx import Document
from common import ask,parse,err
st.set_page_config(page_title="AI Multilingual FAQ Builder",page_icon="🌐",layout="wide")
st.title("🌐 AI Multilingual FAQ Builder")
st.write("Generate editable English and Urdu FAQs grounded in business source material.")
def extract(f):
 b=f.getvalue(); n=f.name.lower()
 if n.endswith(".pdf"): return "\\n".join(f"[{f.name} page {i+1}] "+(p.extract_text() or "") for i,p in enumerate(PdfReader(io.BytesIO(b)).pages))
 if n.endswith(".docx"): return "\\n".join(p.text for p in Document(io.BytesIO(b)).paragraphs)
 return b.decode("utf-8",errors="replace")
with st.sidebar:
 files=st.file_uploader("Business documents",type=["pdf","docx","txt"],accept_multiple_files=True)
 count=st.slider("FAQ pairs",5,30,12)
 tone=st.selectbox("Tone",["Professional","Friendly","Formal","Concise"])
 audience=st.text_input("Audience","Customers")
if st.button("Generate FAQs",type="primary",disabled=not files):
 try:
  docs=[{"file":f.name,"text":extract(f)[:14000]} for f in files]
  docs=[d for d in docs if len(d["text"].strip())>30]
  if not docs: st.error("No readable text. Scanned PDFs need OCR.")
  else:
   prompt=("Create exactly "+str(count)+" FAQ pairs. Return JSON key faqs; each FAQ has id,category,question_en,answer_en,question_ur,answer_ur,source_file,evidence. "
   "Urdu must be natural Urdu script and equivalent in meaning. Use ONLY supplied facts; never invent prices, policies, contacts, delivery dates, warranties. "
   "If source is insufficient, advise contacting business for confirmation in both languages. Cite source filename. "
   f"Tone={tone}; Audience={audience}; Sources={json.dumps(docs,ensure_ascii=False)}")
   with st.spinner("Generating bilingual FAQs..."): st.session_state.faqs=parse(ask(prompt,"You are a careful bilingual FAQ writer. Ground every answer in source evidence.")).get("faqs",[])
 except Exception as e: st.error(err(e))
faqs=st.session_state.get("faqs",[])
if faqs:
 st.subheader("Edit FAQs")
 edited=[]
 for i,f in enumerate(faqs):
  with st.expander(f"FAQ {i+1}: {f.get('category','General')}",expanded=i==0):
   qe=st.text_input("Question (English)",f.get("question_en",""),key=f"qe{i}")
   ae=st.text_area("Answer (English)",f.get("answer_en",""),key=f"ae{i}")
   qu=st.text_input("سوال (اردو)",f.get("question_ur",""),key=f"qu{i}")
   au=st.text_area("جواب (اردو)",f.get("answer_ur",""),key=f"au{i}")
   st.caption("Source: "+f.get("source_file","")+" | Evidence: "+f.get("evidence",""))
   edited.append({"id":f.get("id",i+1),"category":f.get("category",""),"question_en":qe,"answer_en":ae,"question_ur":qu,"answer_ur":au,"source_file":f.get("source_file",""),"evidence":f.get("evidence","")})
 st.download_button("Download editable JSON",json.dumps(edited,ensure_ascii=False,indent=2),"faqs.json","application/json")
 md="\\n\\n".join("## "+x["question_en"]+"\\n"+x["answer_en"]+"\\n\\n### "+x["question_ur"]+"\\n"+x["answer_ur"] for x in edited)
 st.download_button("Download Markdown",md,"faqs.md","text/markdown")
st.caption("A fluent Urdu reviewer should verify wording and business facts before publication.")
