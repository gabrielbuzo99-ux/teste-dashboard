// BSC dynamic loader
function loadBSCs(regionalId) {
    const sel = document.getElementById('sel-bsc');
    if (!sel) return;
    if (!regionalId) {
        // keep all options, just reset value
        sel.value = '';
        return;
    }
    fetch(`/api/bscs/${regionalId}`)
        .then(r => r.json())
        .then(bscs => {
            sel.innerHTML = '<option value="">Todos</option>';
            bscs.forEach(b => {
                const o = document.createElement('option');
                o.value = b.id;
                o.textContent = b.nome;
                sel.appendChild(o);
            });
        });
}

// Highlight active nav on load
document.querySelectorAll('.nav-item').forEach(a => {
    if (a.href === window.location.href.split('?')[0]) {
        a.classList.add('active');
    }
});

// Auto-pulse for critical emergency rows
document.querySelectorAll('.row-critica').forEach(row => {
    row.style.animation = 'pulse-row 2.5s ease-in-out infinite';
});

// Inject keyframes
const style = document.createElement('style');
style.textContent = `
@keyframes pulse-row {
    0%, 100% { background: rgba(239,68,68,.06); }
    50%       { background: rgba(239,68,68,.13); }
}`;
document.head.appendChild(style);
