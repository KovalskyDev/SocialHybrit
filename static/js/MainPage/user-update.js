document.getElementById('id_avatar').onchange = function (evt) {
    const [file] = this.files;
    if (file) {
        let display = document.getElementById('avatar-display');
        const letter = document.getElementById('avatar-letter');
        const container = letter ? letter.parentElement : display.parentElement;

        if (!display) {
            // Если аватара не было (была буква), создаем тег img
            if (letter) letter.remove();
            display = document.createElement('img');
            display.id = 'avatar-display';
            display.className = 'w-100 h-100';
            display.style.objectFit = 'cover';
            container.appendChild(display);
        }
        
        display.src = URL.createObjectURL(file);
    }
}


document.querySelectorAll('.toggle-password').forEach(span => {
    span.addEventListener('click', function() {
        // Ищем инпут внутри той же обертки password-wrapper
        const input = this.closest('.password-wrapper').querySelector('.password-input');
        const icon = this.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.replace('bi-eye', 'bi-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.replace('bi-eye-slash', 'bi-eye');
        }
    });
});
