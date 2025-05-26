document.addEventListener('DOMContentLoaded', () => {
  const teams = [
    "Arsenal", 
    "Aston Villa", 
    "Bournemouth", 
    "Brentford", 
    "Brighton", 
    "Burnley", 
    "Cardiff", 
    "Chelsea", 
    "Crystal Palace", 
    "Everton", 
    "Fulham", 
    "Huddersfield", 
    "Hull", 
    "Ipswich", 
    "Leeds", 
    "Leicester", 
    "Liverpool", 
    "Luton", 
    "Man City", 
    "Man United", 
    "Middlesbrough", 
    "Newcastle", 
    "Norwich", 
    "Nott'm Forest", 
    "Sheffield United", 
    "Southampton", 
    "Stoke", 
    "Sunderland", 
    "Swansea", 
    "Tottenham", 
    "Watford", 
    "West Brom", 
    "West Ham", 
    "Wolves"
];

  
  const teamImages = {
    "Arsenal":          "static/images/arsenal.png",
    "Aston Villa":      "static/images/aston_villa.png",
    "Bournemouth":      "static/images/bournemouth.png",
    "Brentford":        "static/images/brentford.png",
    "Brighton":         "static/images/brighton.png",
    "Burnley":          "static/images/burnley.png",
    "Cardiff":          "static/images/cardiff.png",
    "Chelsea":          "static/images/chelsea.png",
    "Crystal Palace":   "static/images/crystal_palace.png",
    "Everton":          "static/images/everton.png",
    "Fulham":           "static/images/fulham.png",
    "Huddersfield":     "static/images/huddersfield.png",
    "Hull":             "static/images/hull.png",
    "Ipswich":          "static/images/ipswich.png",
    "Leeds":            "static/images/leeds.png",
    "Leicester":        "static/images/leicester.png",
    "Liverpool":        "static/images/liverpool.png",
    "Luton":            "static/images/luton.png",
    "Man City":         "static/images/man_city.png",
    "Man United":       "static/images/man_united.png",
    "Middlesbrough":    "static/images/middlesbrough.png",
    "Newcastle":        "static/images/newcastle.png",
    "Norwich":          "static/images/norwich.png",
    "Nott'm Forest":    "static/images/nott_m_forest.png",
    "Sheffield United": "static/images/sheffield_united.png",
    "Southampton":      "static/images/southampton.png",
    "Stoke":            "static/images/stoke.png",
    "Sunderland":       "static/images/sunderland.png",
    "Swansea":          "static/images/swansea.png",
    "Tottenham":        "static/images/tottenham.png",
    "Watford":          "static/images/watford.png",
    "West Brom":        "static/images/west_brom.png",
    "West Ham":         "static/images/west_ham.png",
    "Wolves":            "static/images/wolves.png"
  };

  const homeSelect      = document.getElementById('home-team-select');
  const awaySelect      = document.getElementById('away-team-select');
  const leftImage       = document.getElementById('left-team-image');
  const rightImage      = document.getElementById('right-team-image');
  const predictButton   = document.getElementById('predict-button');
  const resultSection   = document.getElementById('result');
  const resultHome      = document.getElementById('result-home');
  const resultDraw      = document.getElementById('result-draw');
  const resultAway      = document.getElementById('result-away');

  // Preenche os selects
  teams.forEach(team => {
    const opt1 = new Option(team, team);
    const opt2 = new Option(team, team);
    homeSelect.add(opt1);
    awaySelect.add(opt2);
  });

  // Atualiza opções desabilitando o time já escolhido
  function updateSelectOptions() {
    const homeTeam = homeSelect.value;
    const awayTeam = awaySelect.value;

    Array.from(homeSelect.options).forEach(opt => {
      opt.disabled = (opt.value && opt.value === awayTeam);
    });
    Array.from(awaySelect.options).forEach(opt => {
      opt.disabled = (opt.value && opt.value === homeTeam);
    });
  }

  // Atualiza as imagens de acordo com o time selecionado
  function updateImages() {
    if (teamImages[homeSelect.value]) {
      leftImage.src = teamImages[homeSelect.value];
    }
    if (teamImages[awaySelect.value]) {
      rightImage.src = teamImages[awaySelect.value];
    }
  }

  homeSelect.addEventListener('change', () => {
    updateSelectOptions();
    updateImages();
  });

  awaySelect.addEventListener('change', () => {
    updateSelectOptions();
    updateImages();
  });

  // Mock de chamada ao backend
  predictButton.addEventListener('click', () => {
    const mock = {
      home_win: (Math.random() * 0.6 + 0.2).toFixed(2),
      draw:     (Math.random() * 0.4 + 0.1).toFixed(2),
      away_win: (Math.random() * 0.6 + 0.2).toFixed(2)
    };

    resultHome.textContent = `H: ${mock.home_win}`;
    resultDraw.textContent = `D: ${mock.draw}`;
    resultAway.textContent = `A: ${mock.away_win}`;
    resultSection.style.display = 'block';
  });
});
