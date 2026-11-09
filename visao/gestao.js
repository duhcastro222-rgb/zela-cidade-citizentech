// Tela da prefeitura: lista, muda status (PUT) e exclui (DELETE)
const corpo = document.getElementById("corpo-chamados");
const filtro = document.getElementById("filtro-status");
const msgLista = document.getElementById("msg-lista");
const mapa = criarMapa("mapa");
const camadaPinos = L.layerGroup().addTo(mapa);

function opcoesStatus(atual) {
  return ["aberto", "em_andamento", "resolvido"]
    .map((s) => `<option value="${s}" ${s === atual ? "selected" : ""}>${ROTULOS[s]}</option>`)
    .join("");
}

function contadores(chamados) {
  const total = (s) => chamados.filter((c) => c.status === s).length;
  document.getElementById("contadores").innerHTML = `
    <div><strong>${chamados.length}</strong><span>Total</span></div>
    <div><strong>${total("aberto")}</strong><span>Abertos</span></div>
    <div><strong>${total("em_andamento")}</strong><span>Em andamento</span></div>
    <div><strong>${total("resolvido")}</strong><span>Resolvidos</span></div>`;
}

// Um pino por chamado com coordenadas
function pinos(chamados) {
  camadaPinos.clearLayers();
  const pontos = [];
  chamados.forEach((c) => {
    if (c.latitude === null || c.longitude === null) return;
    L.marker([c.latitude, c.longitude]).addTo(camadaPinos)
      .bindPopup(`<strong>${escapar(c.protocolo)}</strong><br>${escapar(ROTULOS[c.tipo])}<br>${escapar(ROTULOS[c.status])}`);
    pontos.push([c.latitude, c.longitude]);
  });
  if (pontos.length) mapa.fitBounds(pontos, { padding: [30, 30], maxZoom: 15 });
}

// GET: lista e filtra por status na tela
async function carregar() {
  try {
    const todos = await api("/api/chamados");
    const chamados = todos.filter((c) => !filtro.value || c.status === filtro.value);
    contadores(todos);
    pinos(chamados);
    corpo.innerHTML = chamados.map((c) => `
      <tr>
        <td><a href="acompanhar.html?protocolo=${escapar(c.protocolo)}">${escapar(c.protocolo)}</a></td>
        <td>${escapar(ROTULOS[c.tipo])}</td>
        <td>${escapar(enderecoCompleto(c))}${c.referencia ? "<br><small>" + escapar(c.referencia) + "</small>" : ""}</td>
        <td>${escapar(c.descricao)}</td>
        <td>${etiqueta(c.prioridade)}</td>
        <td><select data-id="${c.id}">${opcoesStatus(c.status)}</select></td>
        <td>${escapar(c.criado_em)}</td>
        <td><button class="perigo" data-id="${c.id}">Excluir</button></td>
      </tr>`).join("") || '<tr><td colspan="8" class="vazio">Nenhum chamado.</td></tr>';
  } catch (erro) {
    mostrar(msgLista, "erro", erro.message);
  }
}

// PUT: muda status
corpo.addEventListener("change", async (ev) => {
  try {
    const c = await api(`/api/chamados/${ev.target.dataset.id}`, "PUT", { status: ev.target.value });
    mostrar(msgLista, "ok", `${c.protocolo}: ${ROTULOS[c.status]}.`);
    carregar();
  } catch (erro) {
    mostrar(msgLista, "erro", erro.message);
  }
});

// DELETE: exclui após confirmação
corpo.addEventListener("click", async (ev) => {
  if (!ev.target.matches("button.perigo") || !confirm("Excluir este chamado?")) return;
  try {
    const r = await api(`/api/chamados/${ev.target.dataset.id}`, "DELETE");
    mostrar(msgLista, "ok", `${r.removido.protocolo} excluído.`);
    carregar();
  } catch (erro) {
    mostrar(msgLista, "erro", erro.message);
  }
});

filtro.addEventListener("change", carregar);
carregar();
