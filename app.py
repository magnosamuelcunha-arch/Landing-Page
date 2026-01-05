import re
import zipfile
from collections import defaultdict

import requests
from flask import Flask, render_template, request, session, redirect, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# ================= SUPABASE CONFIG =================
SUPABASE_URL = "https://hohrkvydajmzbmlvfyil.supabase.co"
SUPABASE_KEY = "sb_publishable_ObCicLiZDdgxhkd5mYZENw_dqgFF0R4"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ================= FUNÇÕES SUPABASE =================
def salvar_inscricao(nome, categoria, faixa, equipe):
    url = f"{SUPABASE_URL}/rest/v1/inscritos"
    requests.post(url, headers=HEADERS, json={
        "nome": nome,
        "categoria": categoria,
        "faixa": faixa,
        "equipe": equipe
    })

def listar_inscritos():
    url = f"{SUPABASE_URL}/rest/v1/inscritos?select=*"
    r = requests.get(url, headers=HEADERS)
    return r.json()

def excluir_inscrito_supabase(id):
    url = f"{SUPABASE_URL}/rest/v1/inscritos?id=eq.{id}"
    requests.delete(url, headers=HEADERS)

# ================= APP =================
app = Flask(__name__)
app.secret_key = "open-jiu-jitsu-2026-chave-super-secreta"

# ================= EVENTO =================
evento = {
    "nome": "OPEN GRADUAÇÃO DE JIU-JITSU – 2026",
    "local": "PROJETO BOM MENINO – ITAITUBA/PA",
    "data": "8 de Fevereiro de 2026",
    "status": "Inscrições Abertas",
    "categorias": [
        "Até 20 kg – Idade máxima: 6 anos. Faixa branca e cinza.",
        "Até 22 kg – Idade máxima: 10 anos. Faixas branca, cinza e amarela.",
        "Até 28 kg – Idade máxima: 10 anos. Faixas branca, cinza, amarela e laranja.",
        "Até 36 kg – Idade máxima: 10 anos. Faixas branca, cinza, amarela e laranja.",
        "Até 42 kg – Idade máxima: 11 anos. Faixas branca, cinza, amarela e laranja.",
        "Até 50 kg – Idade máxima: 12 anos. Faixas branca, cinza, amarela e laranja.",
        "Até 52 kg – Idade máxima: 13 anos. Faixas branca, cinza, amarela, laranja e verde.",
        "Até 60 kg – Idade máxima: 15 anos. Faixas branca, amarela, laranja e verde.",
        "Até 75 kg – Idade máxima: 17 anos. Faixas branca, amarela, laranja e verde.",
        "Acima de 75 kg – Idade máxima: 17 anos. Faixas branca, amarela, laranja e verde.",
        "Até 80 kg – Acima de 18 anos. Somente faixa branca.",
        "Mais de 81 kg – Acima de 18 anos. Somente faixa branca.",
        "Até 56 kg – Faixas azul e roxa.",
        "Até 75 kg – Faixas azul e roxa.",
        "Acima de 76 kg – Faixas azul e roxa.",
        "Faixas marrom e preta – Sem limite de peso.",
        "Até 90 kg – Acima de 18 anos. Somente faixa branca para academias convidadas.",
        "Até 90 kg – Acima de 18 anos. Somente faixa azul para academias convidadas."
    ],
    "equipes": [
        "CT FRANÇA",
        "TEAM BASTOS",
        "ATTACK",
        "BF TEAM",
        "CT JOSÉ FILHO",
        "MONTE JIU-JITSU",
        "LYCANS",
        "GARAGEM FIGHT CLUBE"
    ]
}

# ================= ROTAS =================
@app.route("/")
def home():
    return render_template("evento.html", evento=evento)

@app.route("/inscricao", methods=["GET", "POST"])
def inscricao():
    mensagem = None
    if request.method == "POST":
        salvar_inscricao(
            request.form["nome"],
            request.form["categoria"],
            request.form["faixa"],
            request.form["equipe"]
        )
        mensagem = "Inscrição realizada com sucesso!"
    return render_template("inscricao.html", mensagem=mensagem, evento=evento)

# ================= ADMIN =================
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    erro = None
    if request.method == "POST":
        if request.form["usuario"] == "CT FRANÇA" and request.form["senha"] == "FRANÇA123":
            session["admin"] = True
            return redirect("/admin")
        erro = "Usuário ou senha inválidos"
    return render_template("admin_login.html", erro=erro)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin/login")
    inscritos = listar_inscritos()
    return render_template("admin.html", inscritos=inscritos)

@app.route("/admin/excluir/<int:id>", methods=["POST"])
def excluir(id):
    if not session.get("admin"):
        return redirect("/admin/login")
    excluir_inscrito_supabase(id)
    return redirect("/admin")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")

# ================= PDF GERAL =================
@app.route("/admin/pdf")
def exportar_pdf():
    if not session.get("admin"):
        return redirect("/admin/login")

    inscritos = listar_inscritos()
    arquivo_pdf = "/tmp/inscritos.pdf"
    c = canvas.Canvas(arquivo_pdf, pagesize=A4)
    largura, altura = A4
    y = altura - 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Lista de Inscritos - Open Jiu-Jitsu 2026")
    y -= 30
    c.setFont("Helvetica", 10)

    for i in inscritos:
        c.drawString(40, y, f"{i['nome']} | {i['categoria']} | {i['faixa']} | {i['equipe']}")
        y -= 15
        if y < 40:
            c.showPage()
            y = altura - 40

    c.save()
    return send_file(arquivo_pdf, as_attachment=True)

# ================= PDF POR CATEGORIA =================
@app.route("/admin/pdf/categorias")
def pdf_por_categoria():
    if not session.get("admin"):
        return redirect("/admin/login")

    inscritos = listar_inscritos()
    categorias = defaultdict(list)
    for i in inscritos:
        categorias[i["categoria"]].append(i)

    zip_path = "/tmp/pdfs_categorias.zip"
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for categoria, lista in categorias.items():
            nome = re.sub(r'[^a-zA-Z0-9_]', '', categoria.lower().replace(" ", "_"))
            pdf_path = f"/tmp/{nome}.pdf"
            c = canvas.Canvas(pdf_path, pagesize=A4)
            y = A4[1] - 40

            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, categoria)
            y -= 30
            c.setFont("Helvetica", 10)

            for i in lista:
                c.drawString(40, y, f"{i['nome']} - {i['faixa']} - {i['equipe']}")
                y -= 15
                if y < 40:
                    c.showPage()
                    y = A4[1] - 40

            c.save()
            zipf.write(pdf_path, arcname=f"{nome}.pdf")

    return send_file(zip_path, as_attachment=True)
#execução
if __name__ == "__main__":
    app.run(host="0.0.0.0")
    




