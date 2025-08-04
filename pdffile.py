from flask import Flask,request,render_template
import pdfplumber
import spacy
import nltk
import random
import os
nltk.download('wordnet')
from nltk.corpus import wordnet
nlp=spacy.load("en_core_web_sm")
app=Flask(__name__)
#for uploaded pdf file
def extract_text_from_pdf(sample_pdf):
    content=""
    with pdfplumber.open(sample_pdf) as pdf:
        for page in pdf.pages:
            text=page.extract_text()
            if text:
                content+= "\n"+text
    return content
#for uploaded text file
def extract_text_from_txt(file):
    filepath = os.path.join("uploads", file.filename)
    file.save(filepath)
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    os.remove(filepath)
    return content
#for generating mcqs
def generate_mcqs(text):
    doc = nlp(text)
    questions = []
    for sent in doc.sents:
        for ent in sent.ents:
            if ent.label_ in ["PERSON","GPE","ORG","DATE","TIME","MONEY","PERCENT","LOC","EVENT","WORK_OF_ART","LANGUAGE","FAC","LAW","NORP","QUANTITY"]:
                q=sent.text.replace(ent.text,"_________________")
                a=ent.text
                #getting distractors
                distractors=generate_distractors(a)
                if len(distractors)<3:
                    continue
                options=distractors+[a]
                random.shuffle(options)
                questions.append({
                    "question": q.strip(),
                    "Options": options,
                    "type": "mcq"
                })
    print("generated")
    return questions
def generate_distractors(word):
    distractors=set()
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            name=lemma.name().replace("_"," ")
            if name.lower()!=word.lower():
                distractors.add(name)
            if len(distractors)>=3:
                break
        if len(distractors)>=3:
            break   
    return list(distractors)[:3]
@app.route("/",methods=["GET","POST"])
def upload_file():
    mcqs={}
    if request.method == "POST":
        try: 
            file = request.files["file"]
            if file.filename.endswith(".pdf"):
                text = extract_text_from_pdf(file)
            elif file.filename.endswith(".txt"):
                text = extract_text_from_txt(file)
            else:
                return render_template("index.html", error="UN SUPPORTED FILETYPE")
            mcqs = generate_mcqs(text)
            return render_template("index.html", mcqs=mcqs)
        except Exception as e:
            print("Error during upload:", str(e))
            return render_template("index.html", error="Something went wrong while processing the file.")
    return render_template("index.html")
if __name__=="__main__":
    app.run(debug=True)



