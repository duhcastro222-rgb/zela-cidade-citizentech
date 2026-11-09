// Tela do cidadão: abre chamado e mostra o protocolo
const form = document.getElementById("form-chamado");
const msgForm = document.getElementById("msg-form");
const infoPonto = document.getElementById("info-ponto");
const mapa = criarMapa("mapa");
let marcador = null;

// Coloca (ou move) o pino e guarda as coordenadas no formulário
function marcar(lat, lon) {
  if (marcador) marcador.setLatLng([lat, lon]);
  else marcador = L.marker([lat, lon]).addTo(mapa);
  document.getElementById("latitude").value = lat.toFixed(6);
  document.getElementById("longitude").value = lon.toFixed(6);
  infoPonto.textContent = "Local marcado. Clique em outro ponto para ajustar.";
}

mapa.on("click", (ev) => marcar(ev.latlng.lat, ev.latlng.lng));

// CEP -> endereço (ViaCEP pela nossa API) -> centraliza o mapa
document.getElementById("campo-cep").addEventListener("blur", async (ev) => {
  const aviso = document.getElementById("endereco-cep");
  const cep = ev.target.value.replace(/\D/g, "");
  if (cep.length !== 8) return;
  try {
    const endereco = await api("/api/cep/" + cep);
    aviso.textContent = enderecoCompleto(endereco);
    const ponto = await localizarEndereco(`${endereco.logradouro}, ${endereco.cidade}, ${endereco.uf}`);
    if (ponto) {
      mapa.setView(ponto, 17);
      marcar(ponto[0], ponto[1]);
    }
  } catch (erro) {
    aviso.textContent = erro.message;
  }
});

// GPS do navegador
document.getElementById("btn-localizacao").addEventListener("click", () => {
  if (!navigator.geolocation) return;
  infoPonto.textContent = "Buscando sua localização...";
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      mapa.setView([pos.coords.latitude, pos.coords.longitude], 18);
      marcar(pos.coords.latitude, pos.coords.longitude);
    },
    () => { infoPonto.textContent = "Não foi possível obter a localização."; }
  );
});

// POST: envia o chamado e mostra o protocolo
form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    const c = await api("/api/chamados", "POST", Object.fromEntries(new FormData(form)));
    document.getElementById("numero-protocolo").textContent = c.protocolo;
    document.getElementById("info-protocolo").textContent =
      `${ROTULOS[c.tipo]} em ${enderecoCompleto(c)}` +
      (c.alerta_central ? " · Central da prefeitura avisada." : "");
    document.getElementById("link-acompanhar").href = "acompanhar.html?protocolo=" + c.protocolo;
    document.getElementById("caixa-protocolo").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });

    form.reset();
    document.getElementById("latitude").value = "";  // reset() não limpa campo hidden
    document.getElementById("longitude").value = "";
    document.getElementById("btn-copiar").textContent = "Copiar protocolo";
    msgForm.className = "mensagem";
    document.getElementById("endereco-cep").textContent = "Digite o CEP para localizar no mapa.";
    if (marcador) { marcador.remove(); marcador = null; }
    infoPonto.textContent = "Clique no mapa para marcar o local exato.";
  } catch (erro) {
    mostrar(msgForm, "erro", erro.message);
  }
});

document.getElementById("btn-copiar").addEventListener("click", async (ev) => {
  await navigator.clipboard.writeText(document.getElementById("numero-protocolo").textContent);
  ev.target.textContent = "Copiado!";
});
