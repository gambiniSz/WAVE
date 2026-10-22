// Endereço da API FastAPI (uvicorn main:app --reload). Troque ao publicar.
const API = "http://localhost:8000";

const DEMO = {
  pesc: [
    {id_pescador: 1, nome: "André Luiz", email: "andre@exemplo.com", telefone: "(44) 99999-0001", endereco: "Santo Inácio, PR"},
    {id_pescador: 2, nome: "Marcos Silva", email: "marcos@exemplo.com", telefone: "(44) 99999-0002", endereco: "Porto Rico, PR"}
  ],
  locais: [
    {id_local: 1, nome_area: "Rio Paranapanema, trecho A", latitude: -22.69, longitude: -51.8, situacao: "Liberado", descricao: "Pesca artesanal permitida."},
    {id_local: 2, nome_area: "Remanso do Rio Paraná", latitude: -22.76, longitude: -53.27, situacao: "Defeso", descricao: "Período de defeso: pesca suspensa."},
    {id_local: 3, nome_area: "Reserva ambiental", latitude: -22.9, longitude: -52.2, situacao: "Proibido", descricao: "Área de preservação."}
  ],
  vend: [
    {id_venda: 1, id_pescador: 1, data_venda: "2026-09-28", valor: 180, descricao: "6 kg de tilápia"},
    {id_venda: 2, id_pescador: 2, data_venda: "2026-09-29", valor: 240, descricao: "8 kg de pintado"}
  ],
  equip: [
    {nome: "Rede de emalhar", tipo: "Aluguel", descricao: "R$ 15 por dia"},
    {nome: "Barco a remo", tipo: "Compartilhado", descricao: "Dividido entre 3 pescadores"},
    {nome: "GPS portátil", tipo: "Aluguel", descricao: "R$ 10 por dia"}
  ]
};

const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const brl = v => Number(v).toLocaleString("pt-BR", {style: "currency", currency: "BRL"});
const st = {pesc: [], locais: [], vend: [], equip: [], demo: false, edit: null};
let map, layer;

function toast(m) {
  const t = $("toast"); t.textContent = m; t.hidden = false;
  clearTimeout(toast.t); toast.t = setTimeout(() => t.hidden = true, 2600);
}

async function call(path, method = "GET", body) {
  const r = await fetch(API + path, {method, headers: {"Content-Type": "application/json"}, body: body ? JSON.stringify(body) : undefined});
  if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(typeof d.detail === "string" ? d.detail : "Erro " + r.status); }
  return r.json();
}

async function load() {
  const paths = {pesc: "/api/pescadores/", locais: "/api/locais/", vend: "/api/vendas/", equip: "/api/equipamentos/"};
  const res = await Promise.allSettled(Object.values(paths).map(p => call(p)));
  const keys = Object.keys(paths);
  const falhou = res.slice(0, 3).every(r => r.status === "rejected");
  st.demo = falhou;
  if (falhou) Object.assign(st, JSON.parse(JSON.stringify(DEMO)));
  else keys.forEach((k, i) => st[k] = res[i].status === "fulfilled" ? res[i].value : (k === "equip" ? DEMO.equip : []));
  $("demo").hidden = !st.demo;
  render();
}

const idKey = {pesc: "id_pescador", locais: "id_local", vend: "id_venda"};
const path = {pesc: "/api/pescadores/", locais: "/api/locais/", vend: "/api/vendas/"};

async function criar(k, body) {
  try {
    if (st.demo) st[k].push({...body, [idKey[k]]: Date.now()});
    else await call(path[k], "POST", body);
    toast("Salvo com sucesso"); st.demo ? render() : load();
  } catch (e) { toast(e.message); }
}

function tag(s) {
  const x = (s || "").toLowerCase();
  const c = /proib|defeso/.test(x) ? "bad" : /aten/.test(x) ? "warn" : /libera/.test(x) ? "ok" : "";
  return s ? `<span class="tag ${c}">${esc(s)}</span>` : "";
}

function render() {
  const total = st.vend.reduce((a, v) => a + Number(v.valor), 0);
  $("s-p").textContent = st.pesc.length; $("s-l").textContent = st.locais.length; $("s-v").textContent = brl(total);
  const av = st.locais.filter(l => /proib|defeso|aten/i.test(l.situacao || ""));
  $("avisos").innerHTML = av.length ? av.map(l => `<div class="card"><div><h4>${esc(l.nome_area)}</h4><small>${esc(l.descricao)}</small></div>${tag(l.situacao)}</div>`).join("") : `<div class="card">Nenhum aviso no momento.</div>`;

  $("l-lista").innerHTML = st.locais.map(l => `<div class="card"><div><h4>${esc(l.nome_area)}</h4><small>${esc(l.descricao)}</small><small>${l.latitude.toFixed(3)}, ${l.longitude.toFixed(3)}</small></div>${tag(l.situacao)}</div>`).join("") || `<div class="card">Nenhum local cadastrado.</div>`;
  pintarMapa();

  $("e-lista").innerHTML = st.equip.map(e => `<article><i>🎣</i><h3>${esc(e.nome)}</h3><p>${esc(e.descricao)}</p><p><span class="tag">${esc(e.tipo)}</span></p></article>`).join("");

  $("p-lista").innerHTML = st.pesc.map(p => `<div class="card"><div><h4>${esc(p.nome)}</h4><small>${esc(p.email)} ${p.telefone ? "· " + esc(p.telefone) : ""}</small><small>${esc(p.endereco)}</small></div><div class="row"><button class="mini" data-ed="${p.id_pescador}">Editar</button><button class="mini del" data-rm="${p.id_pescador}">Excluir</button></div></div>`).join("") || `<div class="card">Nenhum pescador cadastrado.</div>`;
  $("v-pesc").innerHTML = st.pesc.map(p => `<option value="${p.id_pescador}">${esc(p.nome)}</option>`).join("");
  const nome = id => (st.pesc.find(p => p.id_pescador === id) || {}).nome || "Pescador " + id;
  $("v-lista").innerHTML = [...st.vend].reverse().map(v => `<div class="card"><div><h4>${esc(nome(v.id_pescador))}</h4><small>${esc(v.descricao)}</small><small>${new Date(v.data_venda + "T00:00").toLocaleDateString("pt-BR")}</small></div><strong>${brl(v.valor)}</strong></div>`).join("") || `<div class="card">Nenhuma venda registrada.</div>`;
  renderKit();
}

// ---- lista de equipamentos do pescador + conferência na volta ----
// Guardada no navegador (localStorage), separada por pescador.
const KIT_KEY = "wave_kit";
function lerKit() { try { return JSON.parse(localStorage.getItem(KIT_KEY)) || {}; } catch { return {}; } }
function salvarKit() { try { localStorage.setItem(KIT_KEY, JSON.stringify(st.kit)); } catch {} }
st.kit = lerKit();
function kitAtual() {
  const id = $("e-pesc").value;
  if (!id) return null;
  return st.kit[id] || (st.kit[id] = {itens: [], pesca: false, fim: false});
}

function renderKit() {
  const sel = $("e-pesc"), atual = sel.value;
  sel.innerHTML = st.pesc.map(p => `<option value="${p.id_pescador}">${esc(p.nome)}</option>`).join("");
  if ([...sel.options].some(o => o.value === atual)) sel.value = atual;
  const k = kitAtual();
  if (!k) {
    $("k-box").innerHTML = `<div class="vazio">Cadastre um pescador na aba Pescadores primeiro.</div>`;
    $("k-form").hidden = true; $("k-acoes").innerHTML = ""; $("k-res").innerHTML = "";
    return;
  }
  $("k-form").hidden = k.pesca;

  const conf = k.pesca;
  const status = i => {
    if (!i.ok) return `<span class="tag">Pendente</span>`;
    return i.volta >= i.qtd ? `<span class="tag ok">Voltou</span>` : `<span class="tag bad">Faltam ${i.qtd - i.volta}</span>`;
  };
  const linhas = k.itens.map(i => `<tr>
    <td>${esc(i.nome)}</td><td>${i.qtd}</td>
    ${conf ? `<td><input type="number" min="0" max="${i.qtd}" value="${i.volta}" data-kv="${i.id}" aria-label="Quantidade que voltou de ${esc(i.nome)}" ${k.fim ? "disabled" : ""}></td>
    <td><input type="checkbox" data-kc="${i.id}" ${i.ok ? "checked" : ""} ${k.fim ? "disabled" : ""} aria-label="Conferido: ${esc(i.nome)}"></td>
    <td>${status(i)}</td>` : `<td><button class="mini del" data-kdel="${i.id}">Remover</button></td>`}
  </tr>`).join("");
  $("k-box").innerHTML = k.itens.length
    ? `<table><thead><tr><th>Equipamento</th><th>Levou</th>${conf ? "<th>Voltou</th><th>Conferido</th><th>Situação</th>" : "<th></th>"}</tr></thead><tbody>${linhas}</tbody></table>`
    : `<div class="vazio">Nenhum equipamento na lista. Adicione abaixo tudo o que você leva para pescar.</div>`;

  $("k-acoes").innerHTML = !k.pesca ? (k.itens.length ? `<button class="btn" id="k-ini">Iniciar pesca</button>` : "")
    : k.fim ? `<button class="btn" id="k-novo">Nova pesca</button>`
    : `<button class="btn" id="k-fim">Finalizar pesca e conferir</button><button class="btn ghost dk" id="k-cancel">Cancelar pesca</button>`;

  if (k.fim) {
    const falt = k.itens.filter(i => i.volta < i.qtd);
    $("k-res").innerHTML = falt.length
      ? `<div class="res bad">Atenção: faltam equipamentos!<ul>${falt.map(i => `<li>${esc(i.nome)}: levou ${i.qtd}, voltou ${i.volta} (faltam ${i.qtd - i.volta})</li>`).join("")}</ul></div>`
      : `<div class="res ok">Tudo certo! Todos os equipamentos voltaram. ✅</div>`;
  } else $("k-res").innerHTML = "";
}

$("e-pesc").onchange = renderKit;
$("k-add").onclick = () => {
  const k = kitAtual(); if (!k) return toast("Cadastre um pescador primeiro.");
  const nome = $("k-nome").value.trim(), qtd = parseInt($("k-qtd").value);
  if (!nome || !(qtd >= 1)) return toast("Informe o equipamento e a quantidade.");
  k.itens.push({id: Date.now() + Math.floor(Math.random() * 1000), nome, qtd, volta: qtd, ok: false});
  salvarKit(); $("k-nome").value = ""; $("k-qtd").value = 1; renderKit(); $("k-nome").focus();
};
$("k-box").onclick = e => {
  const id = e.target.dataset.kdel, k = kitAtual();
  if (!id || !k) return;
  k.itens = k.itens.filter(i => String(i.id) !== id); salvarKit(); renderKit();
};
$("k-box").onchange = e => {
  const k = kitAtual(); if (!k) return;
  const vid = e.target.dataset.kv, cid = e.target.dataset.kc;
  const item = k.itens.find(i => String(i.id) === (vid || cid)); if (!item) return;
  if (vid) item.volta = Math.max(0, Math.min(item.qtd, parseInt(e.target.value) || 0));
  if (cid) item.ok = e.target.checked;
  salvarKit(); renderKit();
};
$("k-acoes").onclick = e => {
  const k = kitAtual(); if (!k) return;
  if (e.target.id === "k-ini") { k.itens.forEach(i => { i.ok = false; i.volta = i.qtd; }); k.pesca = true; k.fim = false; toast("Boa pesca! Na volta, confira cada item."); }
  else if (e.target.id === "k-fim") {
    if (k.itens.some(i => !i.ok)) return toast("Marque todos os itens como conferidos.");
    k.fim = true;
  }
  else if (e.target.id === "k-novo" || e.target.id === "k-cancel") { k.pesca = false; k.fim = false; }
  else return;
  salvarKit(); renderKit();
};

// ---- abas e mapa ----
document.querySelectorAll(".tabs button").forEach(b => b.onclick = () => {
  document.querySelectorAll(".tabs button").forEach(x => x.classList.toggle("on", x === b));
  document.querySelectorAll(".pane").forEach(p => p.hidden = p.id !== b.dataset.t);
  if (b.dataset.t === "mapa") { iniciarMapa(); setTimeout(() => map && map.invalidateSize(), 60); }
});
function iniciarMapa() {
  if (map) return;
  if (typeof L === "undefined") {
    $("map").innerHTML = '<p style="padding:24px;margin:0">Não deu para carregar o mapa. Confira a internet e se o Live Server está aberto (http://127.0.0.1...), não o arquivo direto. Os locais continuam listados abaixo.</p>';
    return;
  }
  map = L.map("map").setView([-22.7, -52], 6);
  const tiles = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {attribution: "© OpenStreetMap", maxZoom: 19}).addTo(map);
  let avisou = false;
  tiles.on("tileerror", () => { if (!avisou) { avisou = true; toast("Os blocos do mapa não carregaram. Verifique a internet."); } });
  layer = L.layerGroup().addTo(map); pintarMapa();
}
function pintarMapa() {
  if (!map) return;
  layer.clearLayers();
  const pts = st.locais.map(l => { L.marker([l.latitude, l.longitude]).addTo(layer).bindPopup(`<b>${esc(l.nome_area)}</b><br>${esc(l.situacao)}`); return [l.latitude, l.longitude]; });
  if (pts.length) map.fitBounds(pts, {padding: [30, 30], maxZoom: 10});
}

// ---- formulários ----
$("l-ok").onclick = () => {
  const b = {nome_area: $("l-nome").value.trim(), latitude: parseFloat($("l-lat").value), longitude: parseFloat($("l-lng").value), situacao: $("l-sit").value, descricao: $("l-desc").value.trim() || null};
  if (!b.nome_area || isNaN(b.latitude) || isNaN(b.longitude)) return toast("Informe nome, latitude e longitude.");
  criar("locais", b); ["l-nome", "l-lat", "l-lng", "l-desc"].forEach(i => $(i).value = "");
};

function limparP() { st.edit = null; ["p-nome", "p-email", "p-tel", "p-end"].forEach(i => $(i).value = ""); $("p-tit").textContent = "Novo pescador"; $("p-cancel").hidden = true; }
$("p-cancel").onclick = limparP;
$("p-ok").onclick = async () => {
  const b = {nome: $("p-nome").value.trim(), email: $("p-email").value.trim(), telefone: $("p-tel").value.trim() || null, endereco: $("p-end").value.trim() || null};
  if (!b.nome || !b.email) return toast("Informe nome e e-mail.");
  if (st.edit) {
    try {
      if (st.demo) Object.assign(st.pesc.find(p => p.id_pescador === st.edit), b); else await call(path.pesc + st.edit, "PUT", b);
      toast("Pescador atualizado");
    } catch (e) { return toast(e.message); }
    limparP(); st.demo ? render() : load();
  } else { criar("pesc", b); limparP(); }
};
$("p-lista").onclick = async e => {
  const ed = e.target.dataset.ed, rm = e.target.dataset.rm;
  if (ed) {
    const p = st.pesc.find(x => x.id_pescador == ed); st.edit = p.id_pescador;
    $("p-nome").value = p.nome; $("p-email").value = p.email; $("p-tel").value = p.telefone || ""; $("p-end").value = p.endereco || "";
    $("p-tit").textContent = "Editar pescador"; $("p-cancel").hidden = false; $("p-nome").scrollIntoView({block: "center"});
  }
  if (rm && confirm("Excluir este pescador? As vendas dele também serão apagadas.")) {
    try {
      if (st.demo) { st.pesc = st.pesc.filter(p => p.id_pescador != rm); st.vend = st.vend.filter(v => v.id_pescador != rm); render(); }
      else { await call(path.pesc + rm, "DELETE"); load(); }
      toast("Pescador removido");
    } catch (er) { toast(er.message); }
  }
};

$("v-data").valueAsDate = new Date();
$("v-ok").onclick = () => {
  const b = {id_pescador: parseInt($("v-pesc").value), data_venda: $("v-data").value, valor: parseFloat($("v-valor").value), descricao: $("v-desc").value.trim() || null};
  if (!b.id_pescador || !b.data_venda || isNaN(b.valor)) return toast("Escolha o pescador, a data e o valor.");
  criar("vend", b); $("v-valor").value = ""; $("v-desc").value = "";
};

load();