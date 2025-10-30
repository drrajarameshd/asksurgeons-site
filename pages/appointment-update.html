---
layout: default
title: Appointment Update
permalink: /appointment-update/
---

<script>
/* ===== CONFIG ===== */
const WEBAPP_URL = "https://script.google.com/macros/s/AKfycby-MaxKBJvjDCUThFIP9JL3lwnKiFwufcy6Pm7jyqYqMe7PTjA1bWIb56KwPwo8Oe-Ywg/exec";

/* ===== Helper: parse ?key=value from URL ===== */
function getQueryParams() {
  const q = {};
  const parts = window.location.search.replace(/^\?/, '').split('&').filter(Boolean);
  for (const p of parts) {
    const [k, v] = p.split('=').map(decodeURIComponent);
    if (k) q[k] = v === undefined ? '' : v;
  }
  return q;
}

/* ===== Send parameters to Apps Script ===== */
async function sendToScript(params) {
  const data = new URLSearchParams(params);
  try {
    const resp = await fetch(WEBAPP_URL, {
      method: 'POST',
      body: data
      // mode: 'no-cors'  // Uncomment if CORS blocks response (you’ll still send successfully)
    });

    // Try to read response (only works if script allows CORS)
    const text = await resp.text();
    document.getElementById('result').innerHTML = `
      <h3>✅ Response from Script:</h3>
      <pre>${text}</pre>
    `;
  } catch (err) {
    document.getElementById('result').innerHTML =
      `<p style="color:red">Error: ${err.message}</p>`;
  }
}

/* ===== Main Logic ===== */
document.addEventListener('DOMContentLoaded', () => {
  const q = getQueryParams();
  const container = document.getElementById('result');

  // Basic validation
  if (!q.appointmentId) {
    container.innerHTML = `<p style="color:red;">Missing appointmentId in URL.</p>`;
    return;
  }

  // If autosubmit=1, immediately send to Apps Script
  if (q.autosubmit === '1') {
    container.innerHTML = `<p>⏳ Updating appointment <strong>${q.appointmentId}</strong>...</p>`;
    sendToScript(q);
  } else {
    // Show manual confirmation button
    container.innerHTML = `
      <p>Appointment ID: <strong>${q.appointmentId}</strong></p>
      <p>Status: ${q.newStatus || '—'}</p>
      <button id="confirmSend" style="background:#1D75BC;color:#fff;padding:10px 16px;border:0;border-radius:6px;">Send to Script</button>
    `;
    document.getElementById('confirmSend').onclick = () => sendToScript(q);
  }
});
</script>

<h1>Update Appointment</h1>
<p>This page reads parameters from the URL and updates the appointment record through your Google Apps Script web app.</p>

<div id="result" style="margin-top:20px;">Loading...</div>
