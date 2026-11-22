const form = document.getElementById('login-form');
const emailInput = document.getElementById('login-email');
const passwordInput = document.getElementById('login-password');
const emailError = document.getElementById('login-email-error');
const passwordError = document.getElementById('login-password-error');
const formError = document.getElementById('form-error');
const submitBtn = document.getElementById('login-submit-btn');
const btnText = submitBtn.querySelector('.btn-text');
const btnLoader = submitBtn.querySelector('.btn-loader');

const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function validateField(input, errorSpan, validationFn, errorMsg) {
  const isValid = validationFn(input.value);
  input.setAttribute('aria-invalid', !isValid);
  errorSpan.textContent = isValid ? '' : errorMsg;
  return isValid;
}

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
  emailError.textContent = '';
  passwordError.textContent = '';
  formError.textContent = '';
  formError.hidden = true;
  emailInput.setAttribute('aria-invalid', 'false');
  passwordInput.setAttribute('aria-invalid', 'false');
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearErrors();

  const isEmailValid = validateField(emailInput, emailError, (val) => emailRegex.test(val), 'Введите корректный email');
  const isPasswordValid = validateField(passwordInput, passwordError, (val) => val.length >= 8, 'Пароль должен быть не менее 8 символов');

  if (!isEmailValid || !isPasswordValid) {
    return;
  }

  setLoading(true);

  try {
    const response = await fetch('http://localhost:8000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: emailInput.value,
        password: passwordInput.value,
      }),
    });

    const data = await response.json();

    if (!response.ok) {
      if (response.status === 401) {
        formError.textContent = data.detail || 'Неверный email или пароль';
        formError.hidden = false;
      } else if (response.status === 422 && Array.isArray(data.detail)) {
        data.detail.forEach((err) => {
          const fieldName = err.loc[1];
          if (fieldName === 'email') {
            emailError.textContent = err.msg;
            emailInput.setAttribute('aria-invalid', 'true');
          } else if (fieldName === 'password') {
            passwordError.textContent = err.msg;
            passwordInput.setAttribute('aria-invalid', 'true');
          }
        });
      } else {
        formError.textContent = 'Произошла ошибка сервера. Попробуйте позже.';
        formError.hidden = false;
      }
      return;
    }

    // Успешный вход (200)
    localStorage.setItem('access_token', data.access_token);
    window.location.href = '/src/pages/groups.html';

  } catch (error) {
    formError.textContent = 'Ошибка сети. Проверьте подключение к интернету.';
    formError.hidden = false;
  } finally {
    setLoading(false);
  }
});