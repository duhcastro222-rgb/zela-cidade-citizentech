// Tela: consome a API REST /api/chamados
const corpo = document.getElementById("corpo-chamados");
const form = document.getElementById("form-chamado");
const filtro = document.getElementById("filtro-status");
const msgForm = document.getElementById("msg-form");
const msgLista = document.getElementById("msg-lista");

const STATUS = { aberto: "Aberto", em_andamento: "Em andamento", resolvido: "Resolvido" };

// Chama a API; se a resposta for erro, lança a mensagem enviada pelo servidor
async function api(url, metodo = "GET", dados) {
  const opcoes = { method: metodo, headers: { "Content-Type": "application/json" } };
  if (dados) opcoes.body = JSON.stringify(dados);
  const resposta = await fetch(url, opcoes);
  const json = await resposta.json();
  if (!resposta.ok) throw new Error(json.erro);
  return json;
}

// Escapa texto digitado antes de virar HTML (evita XSS)
function escapar(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

function mostrar(el, tipo, texto) {
  el.className = "mensagem " + tipo;
  el.textContent = texto;
}

// GET: lista e filtra por status na tela
async function carregar() {
  try {
    const chamados = (await api("/api/chamados"))
      .filter(c => !filtro.value || c.status === filtro.value);
    corpo.innerHTML = chamados.map(c => `
      <tr>
        <td>${c.id}</td>
        <td>${escapar(c.tipo)}</td>
        <td>${escapar(`${c.logradouro}, ${c.bairro} - ${c.cidade}/${c.uf}`)}
            ${c.referencia ? "<br>" + escapar(c.referencia) : ""}</td>
        <td>${escapar(c.descricao)}</td>
        <td>${escapar(c.prioridade)}</td>
        <td><select data-id="${c.id}">
          ${Object.keys(STATUS).map(s => `<option value="${s}" ${s === c.status ? "selected" : ""}>${STATUS[s]}</option>`).join("")}
        </select></td>
        <td>${escapar(c.criado_em)}</td>
        <td><button class="excluir" data-id="${c.id}">Excluir</button></td>
      </tr>`).join("") || '<tr><td colspan="8">Nenhum chamado.</td></tr>';
  } catch (erro) {
    mostrar(msgLista, "erro", erro.message);
  }
}

// POST: abre chamado
form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    const c = await api("/api/chamados", "POST", Object.fromEntries(new FormData(form)));
    let texto = `Chamado nº ${c.id} aberto (${c.bairro} - ${c.cidade}/${c.uf}).`;
    if (c.alerta_central === true) texto += " Central avisada.";
    if (c.alerta_central === false) texto += " Central offline.";
    mostrar(msgForm, "ok", texto);
    form.reset();
    carregar();
  } catch (erro) {
    mostrar(msgForm, "erro", erro.message);
  }
});

// PUT: muda status
corpo.addEventListener("change", async (ev) => {
  try {
    const c = await api(`/api/chamados/${ev.target.dataset.id}`, "PUT", { status: ev.target.value });
    mostrar(msgLista, "ok", `Chamado nº ${c.id}: ${STATUS[c.status]}.`);
    carregar();
  } catch (erro) {
    mostrar(msgLista, "erro", erro.message);
  }
});

// DELETE: exclui após confirmação
corpo.addEventListener("click", async (ev) => {
  if (!ev.target.matches("button.excluir") || !confirm("Excluir este chamado?")) return;
  try {
    const r = await api(`/api/chamados/${ev.target.dataset.id}`, "DELETE");
    mostrar(msgLista, "ok", `Chamado nº ${r.removido.id} excluído.`);
    carregar();
  } catch (erro) {
    mostrar(msgLista, "erro", erro.message);
  }
});

filtro.addEventListener("change", carregar);
carregar();
