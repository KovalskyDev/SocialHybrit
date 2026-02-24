// 1. Константы и поиск элементов
const autoExpandFields = document.querySelectorAll('.auto-expand');
const textareaAbout = document.getElementById('id_about');
const charCount = document.getElementById('char-count');
const MAX_CHARS = 2200;

const mediaInput = document.getElementById('id_media');
const previewContainer = document.getElementById('media-preview-container');
const imgPreview = document.getElementById('image-preview');
const videoPreview = document.getElementById('video-preview');
const fileNameHint = document.getElementById('file-name-hint');
const deleteBtn = document.getElementById('delete-media-btn');
const clearCheckbox = document.getElementById('media-clear_id');

const labelText = document.getElementById('label-text');
const labelIcon = document.getElementById('label-icon');

// 2. Авто-высота текстовых полей (Название и Описание)
const adjustHeight = (el) => {
    el.style.height = 'auto';
    el.style.height = el.scrollHeight + 'px';
};

autoExpandFields.forEach(field => {
    field.addEventListener('input', () => adjustHeight(field));
    adjustHeight(field); // Вызываем сразу при загрузке
});

// 3. Лимит символов для поля "Опис"
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

// 4. Логика выбора нового файла (Предпросмотр + Смена кнопок)
mediaInput.onchange = function() {
    const file = this.files[0];
    if (file) {
        const fileName = file.name.toLowerCase();
        
        // Проверка на MKV
        if (fileName.endsWith('.mkv')) {
            alert("Формат .mkv не підтримується браузерами. Будь ласка, оберіть MP4 або MOV.");
            this.value = '';
            return;
        }

        // Если выбрали новый файл:
        if (clearCheckbox) clearCheckbox.checked = false; // Отменяем удаление
        if (deleteBtn) deleteBtn.classList.remove('d-none'); // Показываем кнопку "Видалити"

        // Обновляем главную кнопку на "Змінити"
        if (labelText) labelText.textContent = 'Змінити';
        if (labelIcon) {
            labelIcon.classList.remove('bi-plus-lg');
            labelIcon.classList.add('bi-arrow-repeat');
        }

        const isVideo = file.type.startsWith('video/');
        fileNameHint.textContent = file.name;
        previewContainer.classList.remove('d-none');
        
        // Установка превью
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

// 5. Логика моментального удаления (Instagram Style)
if (deleteBtn) {
    deleteBtn.onclick = function() {
        // Визуально скрываем всё
        previewContainer.classList.add('d-none');
        imgPreview.src = '';
        videoPreview.setAttribute('src', ''); 
        mediaInput.value = ''; // Сбрасываем выбранный файл в инпуте
        
        // Ставим галочку для Django, чтобы очистить поле в БД
        if (clearCheckbox) {
            clearCheckbox.checked = true;
        }
        
        // Меняем главную кнопку обратно на "Додати"
        if (labelText) labelText.textContent = 'Додати';
        if (labelIcon) {
            labelIcon.classList.remove('bi-arrow-repeat');
            labelIcon.classList.add('bi-plus-lg');
        }
        
        fileNameHint.textContent = 'Медіа видалено (збережіть зміни)';
        deleteBtn.classList.add('d-none'); // Прячем саму кнопку "Видалити"
    };
}