// Login da gestão: POST /api/login cria a sessão e abre a gestão
const formLogin = document.getElementById("form-login");

formLogin.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  try {
    await api("/api/login", "POST", Object.fromEntries(new FormData(formLogin)));
    location.href = "gestao.html";
  } catch (erro) {
    formLogin.senha.value = "";
    mostrar(document.getElementById("msg-login"), "erro", erro.message);
  }
});
