// Funções usadas pelas três telas

const ROTULOS = {
  buraco: "Buraco na rua", iluminacao: "Iluminação apagada", lixo: "Lixo / entulho",
  calcada: "Calçada quebrada", arvore: "Árvore caída",
  baixa: "Baixa", media: "Média", alta: "Alta",
  aberto: "Aberto", em_andamento: "Em andamento", resolvido: "Resolvido"
};

// Chama a API; se a resposta for erro, lança a mensagem enviada pelo servidor
async function api(url, metodo = "GET", dados) {
  const opcoes = { method: metodo, headers: { "Content-Type": "application/json" } };
  if (dados) opcoes.body = JSON.stringify(dados);
  let resposta;
  try {
    resposta = await fetch(url, opcoes);
  } catch {
    throw new Error("Servidor fora do ar. Tente novamente.");
  }
  const json = await resposta.json();
  if (!resposta.ok) throw new Error(json.erro);
  return json;
}

// Escapa texto antes de virar HTML (evita XSS)
function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

function mostrar(el, tipo, texto) {
  el.className = "mensagem " + tipo;
  el.textContent = texto;
}

function etiqueta(valor) {
  return `<span class="etiqueta ${escapar(valor)}">${escapar(ROTULOS[valor] || valor)}</span>`;
}

function enderecoCompleto(c) {
  return `${c.logradouro}, ${c.bairro} - ${c.cidade}/${c.uf}`;
}

// Mapa Leaflet com OpenStreetMap; começa mostrando o Brasil
function criarMapa(idElemento) {
  const mapa = L.map(idElemento).setView([-14.2, -51.9], 4);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap"
  }).addTo(mapa);
  return mapa;
}

// Animações Lottie (arquivos em visao/animacoes, baixados do LottieFiles)
// Quem pediu menos movimento no sistema vê só o primeiro quadro
function animar(elemento, nome) {
  if (!elemento || !window.lottie) return;
  const parado = matchMedia("(prefers-reduced-motion: reduce)").matches;
  lottie.loadAnimation({
    container: elemento, renderer: "svg", loop: !parado, autoplay: !parado,
    path: `animacoes/${nome}.json`
  });
}

animar(document.getElementById("anim-topo"), "topo");
const animTela = document.getElementById("anim-tela");
if (animTela) animar(animTela, animTela.dataset.animacao);

// Converte endereço em coordenadas (Nominatim / OpenStreetMap)
async function localizarEndereco(endereco) {
  const url = "https://nominatim.openstreetmap.org/search?format=json&limit=1&q=" +
    encodeURIComponent(endereco + ", Brasil");
  const resposta = await fetch(url);
  const lista = await resposta.json();
  return lista.length ? [Number(lista[0].lat), Number(lista[0].lon)] : null;
}
