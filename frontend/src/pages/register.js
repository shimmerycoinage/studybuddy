const form = document.getElementById('register-form');
const nameInput = document.getElementById('reg-name');
const emailInput = document.getElementById('reg-email');
const passwordInput = document.getElementById('reg-password');
const nameError = document.getElementById('reg-name-error');
const emailError = document.getElementById('reg-email-error');
const passwordError = document.getElementById('reg-password-error');
const formError = document.getElementById('form-error');
const submitBtn = document.getElementById('register-submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateField(input, errorSpan, validationFn, errorMsg) {
  const isValid = validationFn(input.value);
  input.setAttribute('aria-invalid', !isValid);
  errorSpan.textContent = isValid ? '' : errorMsg;
  return isValid;
}

nameInput.addEventListener('input', () => {
  validateField(nameInput, nameError, (val) => val.trim().length >= 1, 'Имя не может быть пустым');
});

emailInput.addEventListener('input', () => {
  validateField(emailInput, emailError, (val) => emailRegex.test(val), 'Введите корректный email');
});

passwordInput.addEventListener('input', () => {
  validateField(passwordInput, passwordError, (val) => val.length >= 8, 'Пароль должен быть не менее 8 символов');
});

function setLoading(isLoading) {
  submitBtn.disabled = isLoading;
  btnText.hidden = isLoading;
  btnLoader.hidden = !isLoading;
}

function clearErrors() {
  nameError.textContent = '';
  emailError.textContent = '';
  passwordError.textContent = '';
  formError.textContent = '';
  formError.hidden = true;
  nameInput.setAttribute('aria-invalid', 'false');
  emailInput.setAttribute('aria-invalid', 'false');
  passwordInput.setAttribute('aria-invalid', 'false');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearErrors();

  const isNameValid = validateField(nameInput, nameError, (val) => val.trim().length >= 1, 'Имя не может быть пустым');
  const isEmailValid = validateField(emailInput, emailError, (val) => emailRegex.test(val), 'Введите корректный email');
  const isPasswordValid = validateField(passwordInput, passwordError, (val) => val.length >= 8, 'Пароль должен быть не менее 8 символов');

  if (!isNameValid || !isEmailValid || !isPasswordValid) {
    return;
  }

  setLoading(true);

  try {
    const response = await fetch('http://localhost:8000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: nameInput.value.trim(),
        email: emailInput.value.trim(),
        password: passwordInput.value,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 409) {
        emailError.textContent = data.detail;
        emailInput.setAttribute('aria-invalid', 'true');
      } else if (response.status === 422 && Array.isArray(data.detail)) {
        data.detail.forEach((err) => {
          const fieldName = err.loc[1];
          if (fieldName === 'name') {
            nameError.textContent = err.msg;
            nameInput.setAttribute('aria-invalid', 'true');
          } else if (fieldName === 'email') {
            emailError.textContent = err.msg;
            emailInput.setAttribute('aria-invalid', 'true');
          } else if (fieldName === 'password') {
            passwordError.textContent = err.msg;
            passwordInput.setAttribute('aria-invalid', 'true');
          }
        });
      } else {
        formError.textContent = data.detail || 'Произошла ошибка сервера.';
        formError.hidden = false;
      }
      return;
    }

    // Успешная регистрация (201)
    window.location.href = '/src/pages/login.html';

  } catch (error) {
    formError.textContent = 'Ошибка сети. Проверьте подключение к интернету.';
    formError.hidden = false;
  } finally {
    setLoading(false);
  }
});