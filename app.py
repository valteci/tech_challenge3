from flask import Flask, request, jsonify, render_template
from MLpipeline.pipeline import Pipeline

app = Flask(__name__)
pipeline = Pipeline()
pipeline.raw_data_update()
pipeline.clear_data()
pipeline.load_model()
pipeline.print_model_stats()


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

    result = pipeline.predict(home_team, away_team)
    return jsonify(result)





if __name__ == '__main__':
    app.run(debug=True)
