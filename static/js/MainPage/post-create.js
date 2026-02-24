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

// 1. Авто-высота
const adjustHeight = (el) => {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
};

autoExpandFields.forEach(field => {
    field.addEventListener('input', () => adjustHeight(field));
    adjustHeight(field);
});

// 2. Лимит символов
const handleAboutInput = () => {
    if (textareaAbout.value.length > MAX_CHARS) {
        textareaAbout.value = textareaAbout.value.substring(0, MAX_CHARS);
    }
    const currentLength = textareaAbout.value.length;
    charCount.textContent = currentLength;
    charCount.className = currentLength >= 2100 ? 'text-danger' : 'text-muted';
};

textareaAbout.addEventListener('input', handleAboutInput);
handleAboutInput();

// 3. Предпросмотр Медиа + Проверка MKV + Умные кнопки
mediaInput.onchange = function() {
    const file = this.files[0];
    if (file) {
        const fileName = file.name.toLowerCase();
        
        // Проверка формата
        if (fileName.endsWith('.mkv')) {
            alert("Формат .mkv не підтримується браузерами. Будь ласка, оберіть MP4 або MOV.");
            this.value = '';
            return;
        }

        const isVideo = file.type.startsWith('video/');
        fileNameHint.textContent = file.name;
        previewContainer.classList.remove('d-none');
        removeMediaBtn.classList.remove('d-none');

        // Меняем кнопку на "Змінити"
        labelText.textContent = 'Змінити';
        labelIcon.className = 'bi bi-arrow-repeat me-2';
        
        if (isVideo) {
            imgPreview.classList.add('d-none');
            videoPreview.classList.remove('d-none');
            videoPreview.src = URL.createObjectURL(file);
        } else {
            videoPreview.classList.add('d-none');
            imgPreview.classList.remove('d-none');
            imgPreview.src = URL.createObjectURL(file);
        }
    }
};

// 4. Удаление выбранного медиа
removeMediaBtn.onclick = function() {
    mediaInput.value = '';
    fileNameHint.textContent = 'Файл не обрано';
    previewContainer.classList.add('d-none');
    imgPreview.src = '';
    videoPreview.setAttribute('src', '');
    removeMediaBtn.classList.add('d-none');

    // Возвращаем кнопку "Додати"
    labelText.textContent = 'Додати';
    labelIcon.className = 'bi bi-plus-lg me-2';
};