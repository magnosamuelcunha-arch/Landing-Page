from flask import Flask, render_template, request, session, redirect

app = Flask(__name__)
app.secret_key = "segredo_admin"

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

        inscritos.append({
            "nome": nome,
            "categoria": categoria,
            "equipe": equipe
        })

        mensagem = "Inscrição realizada com sucesso!"

    return render_template("inscricao.html", evento=evento, mensagem=mensagem)

# ---------------- ADMIN ----------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    erro = None

    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if usuario == "CT FRANÇA" and senha == "FRANÇA123":
            session["CT FRANÇA"] = True
            return redirect("/admin")
        else:
            erro = "Usuário ou senha inválidos"

    return render_template("admin_login.html", erro=erro)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/admin/login")

    return render_template("admin.html", inscritos=inscritos)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")
@app.route("/admin/excluir/<int:index>", methods=["POST"])
def excluir_inscricao(index):
    if not session.get("admin"):
        return redirect("/admin/login")

    if 0 <= index < len(inscritos):
        inscritos.pop(index)

    return redirect("/admin")


# ---------------- EXECUÇÃO ----------------

if __name__ == "__main__":
    app.run(debug=True)
