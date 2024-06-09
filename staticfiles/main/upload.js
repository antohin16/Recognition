document.getElementById('upload-button').addEventListener('click', function() {
    const formData = new FormData();
    const imageInput = document.getElementById('image-input');
    if (imageInput.files.length > 0) {
        formData.append('image', imageInput.files[0]);
        fetch('/recognize', {
            method: 'POST',
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            // Изменение порядка: сначала изображение, затем результаты распознавания
            if(data.image_url) {
                document.getElementById('result').innerHTML = `
                    <img src="${data.image_url}" alt="Uploaded Image" style="max-width: 500px;"><br>
                    <strong>Результат:</strong> ${data.final_reading ? data.final_reading : 'Не удалось распознать.'}
                `;
            } else {
                document.getElementById('result').textContent = 'Не удалось загрузить изображение. Пожалуйста, попробуйте другое изображение.';
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            document.getElementById('result').textContent = 'Произошла ошибка при отправке изображения. Пожалуйста, проверьте ваше соединение и попробуйте снова.';
        });
    } else {
        document.getElementById('result').textContent = 'Пожалуйста, выберите изображение для загрузки.';
    }
});
