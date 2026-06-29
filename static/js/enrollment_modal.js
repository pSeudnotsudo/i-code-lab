(function () {
  "use strict";
  console.log("[IIFE] Script loaded and executing");

  document.addEventListener("DOMContentLoaded", function () {
    console.log("[DOMContentLoaded] DOM is ready");

    const modalEl = document.getElementById("enrollModal");
    console.log("[DOM] modalEl:", modalEl);
    if (!modalEl) {
      console.warn("[DOM] enrollModal not found — exiting early");
      return;
    }

    const form      = document.getElementById("enrollForm");
    const submitBtn = document.getElementById("submitBtn");
    const loader    = document.getElementById("loader");
    const ACTION_URL = form.dataset.url;
    const CSRF_TOKEN = form.dataset.csrf;
    console.log("[DOM] form:", form);
    console.log("[DOM] submitBtn:", submitBtn);
    console.log("[DOM] loader:", loader);
    console.log("[Config] ACTION_URL:", ACTION_URL);
    console.log("[Config] CSRF_TOKEN:", CSRF_TOKEN);

    /* ── Flatpickr ── */
    if (typeof flatpickr !== "undefined") {
      console.log("[Flatpickr] flatpickr is available — initialising date pickers");
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      console.log("[Flatpickr] minDate set to:", today);
      const cfg = {
        minDate: today,
        dateFormat: "Y-m-d",
        altInput: true,
        altFormat: "F j, Y",
        disableMobile: false,
      };
      flatpickr("#preferred_registration_date", cfg);
      console.log("[Flatpickr] #preferred_registration_date initialised");
      flatpickr("#prospective_start_date", cfg);
      console.log("[Flatpickr] #prospective_start_date initialised");
    } else {
      console.warn("[Flatpickr] flatpickr is NOT defined — skipping date picker init");
    }

    /* ── Select placeholder colour ── */
    function updateSelectColour(sel) {
      console.log("[Select] updateSelectColour called for:", sel.id || sel.name, "| value:", sel.value);
      if (sel.value) {
        sel.classList.add("has-value");
        console.log("[Select] Added 'has-value' class to:", sel.id || sel.name);
      } else {
        sel.classList.remove("has-value");
        console.log("[Select] Removed 'has-value' class from:", sel.id || sel.name);
      }
    }

    const selects = document.querySelectorAll(".modal-content .form-select");
    console.log("[Select] Found", selects.length, "form-select element(s)");
    selects.forEach(function (sel) {
      updateSelectColour(sel); // run once on load
      sel.addEventListener("change", function () {
        console.log("[Select] 'change' event fired on:", this.id || this.name, "| new value:", this.value);
        updateSelectColour(this);
      });
    });

    /* ── Open/close ── */
    window.openEnrollmentModal = function () {
      console.log("[Modal] openEnrollmentModal() called");
      bootstrap.Modal.getOrCreateInstance(modalEl).show();
    };

    window.closeEnrollmentModal = function () {
      console.log("[Modal] closeEnrollmentModal() called");
      bootstrap.Modal.getOrCreateInstance(modalEl).hide();
    };

    /* ── Reset form + selects when modal closes ── */
    modalEl.addEventListener("hidden.bs.modal", function () {
      console.log("[Modal] 'hidden.bs.modal' event fired — resetting form");
      form.reset();
      document.querySelectorAll(".modal-content .form-select").forEach(function (sel) {
        sel.classList.remove("has-value");
        console.log("[Modal] Cleared 'has-value' from:", sel.id || sel.name);
      });
      console.log("[Modal] Form reset complete");
    });

    /* ── Form submit ── */
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      console.log("[Submit] Form submit intercepted");

      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Submitting…';
      loader.style.display = "block";
      console.log("[Submit] UI locked — loader shown, button disabled");

      const formData = new FormData(form);
      console.log("[Submit] FormData entries:");
      for (const [key, value] of formData.entries()) {
        console.log("  ", key, ":", value);
      }
      console.log("[Submit] Sending POST to:", ACTION_URL);

      fetch(ACTION_URL, {
        method: "POST",
        body: formData,
        headers: { "X-CSRFToken": CSRF_TOKEN },
      })
        .then(function (r) {
          console.log("[Fetch] Response received | status:", r.status, "| ok:", r.ok);
          return r.json();
        })
        .then(function (data) {
          console.log("[Fetch] Parsed JSON response:", data);
          loader.style.display = "none";
          if (data.success) {
            console.log("[Fetch] Success — showing success alert");
            alert(data.message || "Enrollment received! Check your email 📩");
            window.closeEnrollmentModal();
          } else {
            console.warn("[Fetch] Server returned success: false — showing error alert");
            alert(data.message || "Something went wrong. Please try again.");
          }
        })
        .catch(function (err) {
          console.error("[Fetch] Network or parsing error:", err);
          loader.style.display = "none";
          alert("Submission failed. Please try again.");
        })
        .finally(function () {
          console.log("[Fetch] Finally block — re-enabling submit button");
          submitBtn.disabled = false;
          submitBtn.innerHTML = '<i class="ti ti-send" aria-hidden="true"></i> Submit Enrollment';
        });
    });

    console.log("[DOMContentLoaded] All event listeners attached — init complete");
  });

  console.log("[IIFE] DOMContentLoaded listener registered");
})();