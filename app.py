from flask import Flask, request, jsonify, render_template
from MLpipeline.pipeline import Pipeline

app = Flask(__name__)


# Rota raiz: retorna uma página HTML simples
@app.route('/')
def index():
    return render_template('index.html')  # Você pode criar o arquivo templates/index.html depois


# Rota que recebe os nomes dos times e retorna as probabilidades preditas
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    home_team = data.get('home_team')
    away_team = data.get('away_team')

    print('home team:', home_team)
    print('away team:', away_team)

    # Aqui você chamaria seu modelo com base apenas nos nomes
    # Por enquanto, vamos retornar um mock
    result = {
        "home_win": 0.45,
        "draw": 0.30,
        "away_win": 0.25
    }
    return jsonify(result)



# Rota que recebe os times e os dados de entrada manualmente
@app.route('/predict_custom', methods=['POST'])
def predict_custom():
    data = request.get_json()
    
    # Aqui você pode extrair todos os dados necessários
    # Por exemplo: gols, pontos, estatísticas customizadas etc.
    # Vamos só simular uma resposta por agora
    result = {
        "home_win": 0.60,
        "draw": 0.20,
        "away_win": 0.20
    }
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
