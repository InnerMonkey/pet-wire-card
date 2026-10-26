document.addEventListener('click', e => {
    const chip = e.target.closest('.piece-chip');
    document.querySelectorAll('.piece-chip.open').forEach(c => { if (c !== chip) c.classList.remove('open') });
    if (chip) { chip.classList.toggle('open'); e.stopPropagation(); }
    else { document.querySelectorAll('.piece-chip.open').forEach(c => c.classList.remove('open')); }
});