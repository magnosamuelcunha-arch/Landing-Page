from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from flask import Flask, render_template, request, session, redirect
import uuid
from collections import defaultdict
import sqlite3
def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inscritos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria TEXT NOT NULL,
        equipe TEXT NOT NULL
    )
    """)

    


app = Flask(__name__)
init_db()
app.secret_key = "open-jiu-jitsu-2026-chave-super-secreta-123456"



evento = {
    "nome": "OPEN GRADUAÇÃO DE JIU-JITSU – 2026",
    "local": "PROJETO BOM MENINO – ITAITUBA/PA",
    "data": "1 de Fevereiro de 2026",
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

inscritos = []

# ---------------- ROTAS PRINCIPAIS ----------------

@app.route("/")
def home():
    return render_template("evento.html", evento=evento)

@app.route("/inscricao", methods=["GET", "POST"])
def inscricao():
    mensagem = None

    if request.method == "POST":
        nome = request.form["nome"]
        categoria = request.form["categoria"]
        equipe = request.form["equipe"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO inscritos (nome, categoria, equipe) VALUES (?, ?, ?)",
            (nome, categoria, equipe)
        )
        conn.commit()
        conn.close()

        mensagem = "Inscrição realizada com sucesso!"

    return render_template(
        "inscricao.html",
        evento=evento,
        mensagem=mensagem
    )

# ---------------- ADMIN ----------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    erro = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "CT FRANÇA" and senha == "FRANÇA123":
            session["admin"] = True
            return redirect("/admin")
        else:
            erro = "Usuário ou senha inválidos"

    return render_template("admin_login.html", erro=erro)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    inscritos = conn.execute("SELECT * FROM inscritos").fetchall()
    conn.close()

    return render_template("admin.html", inscritos=inscritos)

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")





@app.route("/admin/pdf")
def exportar_pdf():
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    inscritos = conn.execute("SELECT * FROM inscritos").fetchall()
    conn.close()

    arquivo_pdf = "static/inscritos.pdf"
    c = canvas.Canvas(arquivo_pdf, pagesize=A4)
    largura, altura = A4

    y = altura - 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "Lista de Inscritos - Open Jiu-Jitsu 2026")

    y -= 30
    c.setFont("Helvetica", 10)

    for inscrito in inscritos:
        texto = f"{inscrito['nome']} | {inscrito['categoria']} | {inscrito['equipe']}"
        c.drawString(40, y, texto)
        y -= 15

        if y < 40:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = altura - 40

    c.save()

    return redirect("/static/inscritos.pdf")

@app.route("/admin/pdf/categorias")
def pdf_por_categoria():
    if not session.get("admin"):
        return redirect("/admin/login")

    conn = get_db_connection()
    inscritos = conn.execute(
        "SELECT nome, categoria, equipe FROM inscritos"
    ).fetchall()
    conn.close()

    categorias = defaultdict(list)

    for i in inscritos:
        categorias[i["categoria"]].append(i)

    for categoria, lista in categorias.items():
        nome_arquivo = (
            categoria
            .lower()
            .replace(" ", "_")
            .replace("–", "")
            .replace(".", "")
        )

        caminho_pdf = f"static/{nome_arquivo}.pdf"

        c = canvas.Canvas(caminho_pdf, pagesize=A4)
        largura, altura = A4
        y = altura - 40

        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, f"Categoria: {categoria}")

        y -= 30
        c.setFont("Helvetica", 10)

        for inscrito in lista:
            linha = f"{inscrito['nome']} - {inscrito['equipe']}"
            c.drawString(40, y, linha)
            y -= 15

            if y < 40:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = altura - 40

        c.save()

    return redirect("/admin")



# ---------------- EXECUÇÃO ----------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)


