// Deck navigation — keyboard, hash routing, presenter notes, progress.
// Inlined into the generated deck; no external dependencies.
(function () {
  "use strict";
  var slides = Array.prototype.slice.call(document.querySelectorAll(".slide"));
  var progress = document.getElementById("progress");
  var counter = document.getElementById("counter");
  var notesPane = document.getElementById("notes-pane");
  var current = 0;
  var notesVisible = false;

  function clamp(n) {
    return Math.max(0, Math.min(slides.length - 1, n));
  }

  function render() {
    slides.forEach(function (slide, i) {
      var active = i === current;
      slide.classList.toggle("active", active);
      // Hide inactive slides from assistive tech, not just from view.
      slide.setAttribute("aria-hidden", active ? "false" : "true");
    });
    if (progress) {
      progress.style.width = ((current + 1) / slides.length) * 100 + "%";
    }
    if (counter) {
      counter.textContent = current + 1 + " / " + slides.length;
    }
    if (notesPane) {
      var notes = slides[current].getAttribute("data-notes") || "";
      notesPane.textContent = notes || "(no speaker notes)";
    }
    if (window.location.hash !== "#" + (current + 1)) {
      history.replaceState(null, "", "#" + (current + 1));
    }
    // Move focus to the slide so screen readers announce the new content.
    slides[current].focus({ preventScroll: true });
  }

  function go(n) {
    current = clamp(n);
    render();
  }

  function fromHash() {
    var n = parseInt((window.location.hash || "").replace("#", ""), 10);
    return isNaN(n) ? 0 : n - 1;
  }

  function toggleNotes() {
    notesVisible = !notesVisible;
    document.body.classList.toggle("notes-open", notesVisible);
    render();
  }

  function toggleTheme() {
    var root = document.documentElement;
    var explicit = root.getAttribute("data-theme");
    var dark = explicit
      ? explicit === "dark"
      : window.matchMedia("(prefers-color-scheme: dark)").matches;
    root.setAttribute("data-theme", dark ? "light" : "dark");
  }

  document.addEventListener("keydown", function (event) {
    if (event.metaKey || event.ctrlKey || event.altKey) return;
    switch (event.key) {
      case "ArrowRight":
      case "ArrowDown":
      case "PageDown":
      case " ":
        go(current + 1);
        event.preventDefault();
        break;
      case "ArrowLeft":
      case "ArrowUp":
      case "PageUp":
        go(current - 1);
        event.preventDefault();
        break;
      case "Home":
        go(0);
        event.preventDefault();
        break;
      case "End":
        go(slides.length - 1);
        event.preventDefault();
        break;
      case "n":
      case "N":
        toggleNotes();
        break;
      case "t":
      case "T":
        toggleTheme();
        break;
      case "f":
      case "F":
        if (document.fullscreenElement) {
          document.exitFullscreen();
        } else if (document.documentElement.requestFullscreen) {
          document.documentElement.requestFullscreen();
        }
        break;
      default:
        break;
    }
  });

  window.addEventListener("hashchange", function () {
    go(fromHash());
  });

  go(fromHash());
})();
