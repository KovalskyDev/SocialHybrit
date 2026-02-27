document.addEventListener('DOMContentLoaded', function() {
    const autoExpandFields = document.querySelectorAll('.auto-expand');
    const textareaAbout = document.getElementById('id_about');
    const charCount = document.getElementById('char-count');
    const MAX_CHARS = 2200;

    const mediaInput = document.getElementById('id_media');
    const previewContainer = document.getElementById('media-preview-container');
    const imgPreview = document.getElementById('image-preview');
    const videoPreview = document.getElementById('video-preview');
    const removeMediaBtn = document.getElementById('remove-media');
    const fileNameHint = document.getElementById('file-name-hint');

    const labelText = document.getElementById('label-text');
    const labelIcon = document.getElementById('label-icon');

    // --- 1. Авто-высота ---
    const adjustHeight = (el) => {
        if (!el) return;
        el.style.height = 'auto';
        el.style.height = el.scrollHeight + 'px';
    };

    autoExpandFields.forEach(field => {
        field.addEventListener('input', () => adjustHeight(field));
        setTimeout(() => adjustHeight(field), 50);
    });

    // --- 2. Лимит символов ---
    const handleAboutInput = () => {
        if (!textareaAbout || !charCount) return;
        const currentLength = textareaAbout.value.length;
        charCount.textContent = currentLength;
        charCount.className = currentLength >= 2100 ? 'fw-bold text-danger' : 'fw-bold';
    };

    if (textareaAbout) {
        textareaAbout.addEventListener('input', handleAboutInput);
        handleAboutInput();
    }

    // --- 3. Предпросмотр Медиа ---
    if (mediaInput) {
        mediaInput.onchange = function() {
            const file = this.files[0];
            if (file) {
                const fileName = file.name.toLowerCase();
                
                if (fileName.endsWith('.mkv')) {
                    alert("Формат .mkv не підтримується. Оберіть MP4 або MOV.");
                    this.value = '';
                    return;
                }

                const isVideo = file.type.startsWith('video/');
                fileNameHint.textContent = file.name;
                
                // Показываем контейнер: убираем d-none, добавляем d-flex
                previewContainer.classList.remove('d-none');
                previewContainer.classList.add('d-flex');
                removeMediaBtn.classList.remove('d-none');

                // Меняем текст кнопки
                if (labelText) labelText.textContent = 'Змінити';
                if (labelIcon) labelIcon.className = 'bi bi-arrow-repeat me-2';
                
                if (isVideo) {
                    imgPreview.classList.add('d-none');
                    videoPreview.classList.remove('d-none');
                    videoPreview.src = URL.createObjectURL(file);
                    videoPreview.load();
                } else {
                    videoPreview.classList.add('d-none');
                    videoPreview.src = '';
                    imgPreview.classList.remove('d-none');
                    imgPreview.src = URL.createObjectURL(file);
                }
            }
        };
    }

    // --- 4. Удаление выбранного медиа ---
    if (removeMediaBtn) {
        removeMediaBtn.onclick = function() {
            mediaInput.value = '';
            fileNameHint.textContent = 'Файл не обрано';
            
            // Скрываем контейнер
            previewContainer.classList.add('d-none');
            previewContainer.classList.remove('d-flex');
            
            imgPreview.src = '';
            videoPreview.src = '';
            removeMediaBtn.classList.add('d-none');

            // Возвращаем кнопку "Додати"
            if (labelText) labelText.textContent = 'Додати фото/відео';
            if (labelIcon) labelIcon.className = 'bi bi-plus-lg me-2';
        };
    }
});