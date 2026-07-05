// NaVe — interações leves
document.addEventListener('click', (e) => {
  // fecha o menu mobile ao navegar
  if (e.target.closest('.nav a')) document.body.classList.remove('menu-aberto');
});
// some com as mensagens flash depois de alguns segundos
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(f => {
    f.style.transition = 'opacity .6s'; f.style.opacity = '0';
    setTimeout(() => f.remove(), 700);
  });
}, 6000);
