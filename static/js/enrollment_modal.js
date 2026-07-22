(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    const modalEl = document.getElementById("enrollModal");
    if (!modalEl) {
      return;
    }

    const form = document.getElementById("enrollForm");
    const submitBtn = document.getElementById("submitBtn");
    const loader = document.getElementById("loader");
    const ACTION_URL = form.dataset.url;
    const CSRF_TOKEN = form.dataset.csrf;

    /* ── Flatpickr ── */
    if (typeof flatpickr !== "undefined") {
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const cfg = {
        minDate: today,
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        disableMobile: false,
      };
      flatpickr("#preferred_registration_date", cfg);
      flatpickr("#prospective_start_date", cfg);
    }

    /* ── Select placeholder colour ── */
    function updateSelectColour(sel) {
      if (sel.value) {
        sel.classList.add("has-value");
      } else {
        sel.classList.remove("has-value");
      }
    }

    const selects = document.querySelectorAll(".modal-content .form-select");
    selects.forEach(function (sel) {
      updateSelectColour(sel); // run once on load
      sel.addEventListener("change", function () {
        updateSelectColour(this);
      });
    });

    /* ── Open/close ── */
    window.openEnrollmentModal = function () {
      bootstrap.Modal.getOrCreateInstance(modalEl).show();
    };

    window.closeEnrollmentModal = function () {
      bootstrap.Modal.getOrCreateInstance(modalEl).hide();
    };

    /* ── Reset form + selects when modal closes ── */
    modalEl.addEventListener("hidden.bs.modal", function () {
      form.reset();
      document.querySelectorAll(".modal-content .form-select").forEach(function (sel) {
        sel.classList.remove("has-value");
      });
    });

    /* ── Form submit ── */
    form.addEventListener("submit", function (e) {
      e.preventDefault();

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting…';
      loader.style.display = "block";

      const formData = new FormData(form);

      fetch(ACTION_URL, {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": CSRF_TOKEN },
      })
        .then(function (r) {
          return r.json();
        })
        .then(function (data) {
          loader.style.display = "none";
          if (data.success) {
            alert(data.message || "Enrollment received! Check your email 📩");
            window.closeEnrollmentModal();
          } else {
            alert(data.message || "Something went wrong. Please try again.");
          }
        })
        .catch(function (err) {
          loader.style.display = "none";
          alert("Submission failed. Please try again.");
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="ti ti-send" aria-hidden="true"></i> Submit Enrollment';
        });
    });
  });
})();