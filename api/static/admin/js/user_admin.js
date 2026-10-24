(function () {
  function init() {
    const submitRow = document.querySelector(".submit-row");
    const form = document.querySelector("#user_form");

    if (!submitRow || !form) return;

    submitRow.style.display = "none";

    let changed = false;

    const fields = form.querySelectorAll("input, select, textarea");

    fields.forEach((field) => {
      field.addEventListener("input", show);
      field.addEventListener("change", show);
    });

    function show() {
      if (!changed) {
        changed = true;
        submitRow.style.display = "flex";
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
