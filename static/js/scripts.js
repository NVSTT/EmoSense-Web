document.addEventListener('DOMContentLoaded', function() {
    const radios = document.querySelectorAll('input[name="analysis_type"]');
    const note = document.getElementById('note');
    const form = document.querySelector('form');
    const loader = document.getElementById('loader');
    const button = document.querySelector('button');

    // Изменение совета при переключении
    radios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'objective') {
                note.textContent = '💡 Совет: используй фразы вроде "I\'m happy", "This is terrible", "It\'s okay" - объективный анализ с RuBERT (математический подход)';
            } else {
                note.textContent = '💡 Совет: пиши естественно, как человек - субъективный анализ с LLM (человекоподобные рассуждения)';
            }
        });
    });

    // Показать loader при submit
    form.addEventListener('submit', function() {
        loader.style.display = 'block';
        button.disabled = true;
        button.textContent = 'Анализируем...';
    });

    // Исправление ширины прогресс-баров
    const progressFills = document.querySelectorAll('.progress-fill');
    progressFills.forEach(fill => {
        const width = fill.getAttribute('data-width');
        if (width) {
            fill.style.width = width + '%';
        }
    });
});