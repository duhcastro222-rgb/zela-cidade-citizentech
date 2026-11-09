// Tela do cidadão: consulta o chamado pelo protocolo
const formBusca = document.getElementById("form-busca");
const campo = document.getElementById("campo-protocolo");
const msgBusca = document.getElementById("msg-busca");
const resultado = document.getElementById("resultado");
let mapa = null;
let marcador = null;

function texto(id, valor) {
  document.getElementById(id).textContent = valor;
}

// Marca na linha do tempo as etapas já cumpridas
function pintarLinhaTempo(status) {
  const ordem = ["aberto", "em_andamento", "resolvido"];
  document.querySelectorAll("#linha-tempo li").forEach((li) => {
    const etapa = ordem.indexOf(li.dataset.status);
    li.classList.toggle("feito", etapa <= ordem.indexOf(status));
    li.classList.toggle("atual", li.dataset.status === status);
  });
}

function mostrarNoMapa(c) {
  if (!mapa) mapa = criarMapa("mapa");
  mapa.invalidateSize(); // o mapa estava escondido; recalcula o tamanho
  const temPonto = c.latitude !== null && c.longitude !== null;
  document.getElementById("r-sem-ponto").hidden = temPonto;
  if (marcador) { marcador.remove(); marcador = null; }
  if (temPonto) {
    marcador = L.marker([c.latitude, c.longitude]).addTo(mapa);
    mapa.setView([c.latitude, c.longitude], 17);
  }
}

// GET /api/chamados/protocolo/<protocolo>
async function consultar(protocolo) {
  try {
    const c = await api("/api/chamados/protocolo/" + encodeURIComponent(protocolo.trim()));
    msgBusca.className = "mensagem";
    texto("r-protocolo", c.protocolo);
    texto("r-tipo", ROTULOS[c.tipo]);
    texto("r-endereco", enderecoCompleto(c) + (c.referencia ? ` (${c.referencia})` : ""));
    texto("r-descricao", c.descricao);
    texto("r-data", c.criado_em);
    document.getElementById("r-prioridade").innerHTML = "Prioridade " + etiqueta(c.prioridade);
    pintarLinhaTempo(c.status);
    resultado.hidden = false;
    mostrarNoMapa(c);
  } catch (erro) {
    resultado.hidden = true;
    mostrar(msgBusca, "erro", erro.message);
  }
}

formBusca.addEventListener("submit", (ev) => {
  ev.preventDefault();
  consultar(campo.value);
});

// Veio da tela de abertura com ?protocolo=...
const doLink = new URLSearchParams(location.search).get("protocolo");
if (doLink) {
  campo.value = doLink;
  consultar(doLink);
}
