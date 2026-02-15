(() => {
  const $ = (id) => document.getElementById(id);

  const stateLabel = $("stateLabel");
  const screenTitle = $("screenTitle");
  const logEl = $("log");

  const startBtn = $("startBtn");
  const resetBtn = $("resetBtn");
  const crashBtn = $("crashBtn");
  const boostBtn = $("boostBtn");
  const fireBtn = $("fireBtn");
  const backBtn = $("backBtn");

  let state = "TITLE";
  let boosts = 0;

  function log(line) {
    const ts = new Date().toISOString().slice(11, 19);
    logEl.textContent += `[${ts}] ${line}\n`;
    logEl.scrollTop = logEl.scrollHeight;
  }

  function setState(next) {
    state = next;
    stateLabel.textContent = state;
    screenTitle.textContent = state;
    log(`STATE -> ${state}`);
  }

  function reset() {
    boosts = 0;
    setState("TITLE");
    log("RESET");
  }

  startBtn.addEventListener("click", () => {
    boosts = 0;
    setState("PLAY");
  });

  backBtn.addEventListener("click", () => {
    setState("TITLE");
  });

  resetBtn.addEventListener("click", () => {
    reset();
  });

  crashBtn.addEventListener("click", () => {
    // Deterministic immediate crash.
    setState("CRASH");
    throw new Error("DEMO_CRASH: manual crash button clicked");
  });

  boostBtn.addEventListener("click", () => {
    if (state !== "PLAY") {
      log("BOOST ignored (not in PLAY)");
      return;
    }
    boosts += 1;
    log(`BOOST x${boosts}`);
  });

  fireBtn.addEventListener("click", () => {
    if (state !== "PLAY") {
      log("FIRE ignored (not in PLAY)");
      return;
    }
    log("FIRE");
    if (boosts >= 7) {
      // The deterministic bug path the agents should discover.
      setState("CRASH");
      throw new Error(`DEMO_CRASH: START -> BOOST x${boosts} -> FIRE`);
    }
    log("Nothing happened... (try BOOST x7)");
  });

  // Boot
  log("Booted");
  reset();
})();
