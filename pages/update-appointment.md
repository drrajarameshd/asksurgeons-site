---
layout: default
title: Update Appointment
permalink : /update-appointment/
---

<!--
  Jekyll page: posts form data to your Apps Script Webapp.
  Replace WEBAPP_URL below with your webapp endpoint (from your CONFIG.WEBAPP_BASE_URL).
-->

<script>
  // Replace this with your deployed Apps Script webapp URL (the "exec" URL).
  const WEBAPP_URL = "https://script.google.com/macros/s/AKfycby-MaxKBJvjDCUThFIP9JL3lwnKiFwufcy6Pm7jyqYqMe7PTjA1bWIb56KwPwo8Oe-Ywg/exec";

  // Helper: read query params from current URL
  function getQueryParams() {
    const q = {};
    const parts = window.location.search.replace(/^\?/, '').split('&').filter(Boolean);
    for (const p of parts) {
      const [k, v] = p.split('=').map(decodeURIComponent);
      if (k) q[k] = v === undefined ? '' : v;
    }
    return q;
  }

  // On DOM ready: prefill inputs from query params if present
  document.addEventListener('DOMContentLoaded', function () {
    const q = getQueryParams();
    // Map known params to input names if present
    ['appointmentId','token','newStatus','appDate','appTime','auditNote','doctor','phone'].forEach(name => {
      if (q[name]) {
        const el = document.querySelector(`[name="${name}"]`);
        if (el) el.value = q[name];
      }
    });

    // Optional: if ?autosubmit=1 is present, auto-submit the form (useful for single-click links)
    if (q.autosubmit === '1') {
      // Make sure appointmentId exists before auto-submitting
      if (q.appointmentId) {
        document.getElementById('updateForm').submit();
      }
    }
  });

  // Optional: submit form via JS (ajax). NOTE: Apps Script webapps often block read of response because of CORS.
  // For simplicity and reliability, prefer normal form POST (below). If you use fetch, you may need to
  // deploy webapp with appropriate CORS headers and handle authentication.
  async function submitViaFetch(e) {
    e.preventDefault();
    const form = e.target;
    const data = new URLSearchParams(new FormData(form));
    // If Apps Script doesn't return proper CORS headers your fetch will fail to read the response.
    // You can still do fetch with mode:'no-cors' but won't be able to read response body.
    try {
      const resp = await fetch(WEBAPP_URL, {
        method: 'POST',
        body: data,
        // mode: 'no-cors' // fallback (you won't be able to read response)
      });
      // If webapp returns CORS-allowed response you can read it:
      const text = await resp.text();
      document.getElementById('result').innerText = text;
    } catch (err) {
      document.getElementById('result').innerText = 'Submit error: ' + err.message;
    }
  }
</script>

<h1>Update Appointment</h1>
<p>Use this form to update an existing appointment. You can also prefill fields by adding query parameters to this page, for example:
<code>?appointmentId=AS123&token=TOKENVALUE&autosubmit=1</code></p>

<form id="updateForm" method="post" action="https://script.google.com/macros/s/AKfycby-MaxKBJvjDCUThFIP9JL3lwnKiFwufcy6Pm7jyqYqMe7PTjA1bWIb56KwPwo8Oe-Ywg/exec" onsubmit="/*return false;*/" >
  <!-- Hidden items often sent by your email links (appointmentId + token) -->
  <label>Appointment ID<br/>
    <input name="appointmentId" placeholder="AS123" required />
  </label>
  <br/>

  <label>Token (if required)<br/>
    <input name="token" placeholder="action token" />
  </label>
  <br/>

  <label>New Status<br/>
    <select name="newStatus">
      <option value="">-- no change --</option>
      <option value="confirmed">confirmed</option>
      <option value="cancelled">cancelled</option>
      <option value="rescheduled">rescheduled</option>
    </select>
  </label>
  <br/>

  <label>App Date<br/>
    <input name="appDate" placeholder="YYYY-MM-DD" />
  </label>
  <br/>

  <label>App Time<br/>
    <input name="appTime" placeholder="HH:MM" />
  </label>
  <br/>

  <label>Note<br/>
    <input name="auditNote" placeholder="optional note" />
  </label>
  <br/>

  <div style="margin-top:10px">
    <button type="submit">Save</button>
    <!-- alternative: use JS fetch - uncomment if you add submitViaFetch handler -->
    <!-- <button onclick="submitViaFetch(event)">Save (AJAX)</button> -->
  </div>
</form>

<div id="result" style="margin-top:12px;color:#1D75BC"></div>

<hr/>
<p>If you want to create a link (eg. in an email) that opens this page and auto-submits, use:
<code>/appointment-update.html?appointmentId=AS123&token=TOKENVALUE&autosubmit=1</code></p>
