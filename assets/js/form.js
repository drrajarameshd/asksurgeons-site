 <script>
    const form = document.getElementById('patientForm');
    const btn = document.getElementById('submitBtn');
    const toast = document.getElementById('toast');
    const whatsappBtn = document.querySelector('.whatsapp-float');

    function showToast(msg, type='success') {
      toast.textContent = msg;
      toast.className = `show ${type}`;
      setTimeout(() => toast.className = toast.className.replace('show',''), 4000);
    }

    form.addEventListener('submit', e => {
      e.preventDefault();
      document.querySelectorAll('.error-text').forEach(el => el.style.display='none');
      let valid = true;

      if (!form.name.value.trim()) {
        document.getElementById('nameError').style.display='block'; valid=false;
      }
      if (!/^[6-9]\d{9}$/.test(form.phone.value.trim())) {
        document.getElementById('phoneError').style.display='block'; valid=false;
      }
      if (!form.message.value.trim()) {
        document.getElementById('messageError').style.display='block'; valid=false;
      }

      const emailVal = form.email.value.trim();
      if (emailVal && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailVal)) {
        document.getElementById('emailError').style.display='block'; valid=false;
      }

      if (!valid) return;

      btn.disabled = true;
      btn.textContent = '⏳ Sending...';

      fetch('https://script.google.com/macros/s/AKfycbxVT3_NEgcvGYZZAgEeOahRydyRZLkWLqTWJyZXRUl1okMJKRvW4TmldK4DxYKhgfvmrA/exec', {
        method:'POST',
        body: JSON.stringify({
          name: form.name.value.trim(),
          phone: form.phone.value.trim(),
          email: form.email.value.trim(),
          message: form.message.value.trim()
        })
      })
      .then(res => res.text())
      .then(() => { showToast('✅ Enquiry submitted successfully!', 'success'); form.reset(); })
      .catch(() => { showToast('❌ Submission failed. Please try again.', 'error'); })
      .finally(() => { btn.disabled = false; btn.textContent = 'Send Enquiry'; });
    });

  </script>
