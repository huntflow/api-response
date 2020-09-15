(function () {
  const SIZE_LIMIT = 5 * 1024 * 1024;
  document.querySelectorAll('.input-file-wrapper').forEach((input) => {
    const valueEl = input.querySelector('span');
    input.addEventListener('dragenter', (e) => {
      if (e.dataTransfer.items[0] && e.dataTransfer.items[0].kind === 'file') {
        input.classList.add('-drag-hover');
      }
    });
    input.addEventListener('dragleave', () => {
      input.classList.remove('-drag-hover');
    });
    input.addEventListener('drop', () => {
      input.classList.remove('-drag-hover');
    });
    input.querySelector('input').addEventListener('change', (e) => {
      if (e.target.files.length) {
        const file = e.target.files[0];
        if (file.size > SIZE_LIMIT) {
          e.target.value = '';
          alert('Слишком большой файл (>5МБ)');
          return;
        }

        valueEl.innerText = file.name;
        e.target.classList.add('-has-value');
        input.title = file.name;
      } else {
        valueEl.innerText = 'Приклепление резюме';
        e.target.classList.remove('-has-value');
        input.title = '';
      }
    });
  });

  const form = document.querySelector('form');
  const title = document.querySelector('h1');
  function showSuccess() {
    form.style.display = 'none';
    title.innerText = 'Спасибо за отклик!';
  }

  function hideError() {
    showError('');
  }

  function showError(message) {
    form.querySelector('.error').innerText = message;
  }

  if (form) {
    const submitButton = document.querySelector('.button');
    let sending = false;
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (sending) {
        return;
      }
      const inputs = form.querySelectorAll('input, textarea');
      for (const input of inputs) {
        if (input && !input.validity.valid) {
          input.focus();
          return;
        }
      }
      sending = true;
      submitButton.setAttribute('disabled', true);

      hideError();

      fetch('', {
        method: 'POST',
        body: new FormData(form),
      })
        .then((r) => r.json())
        .then((json) => {
          if (json.errors) {
            return Promise.reject(json.errors.common[0]);
          } else {
            showSuccess();
          }
        })
        .catch((err) => {
          if (typeof err === 'string') {
            showError(err);
          } else {
            showError('Не получилось отправить. Попробуйте позже');
          }
        })
        .then(() => {
          sending = false;
          submitButton.removeAttribute('disabled');
        });
    });
  }
})();
