/**
 * PyRunner - run Python in the browser (Pyodide).
 * Configure packages in packages.json - no GUI for package management.
 */
(async function () {
  const status = (msg) => {
    const el = document.getElementById("status");
    if (el) el.textContent = msg;
    console.log("[PyRunner]", msg);
  };
  const out = (msg) => {
    const el = document.getElementById("output");
    if (el) el.textContent += msg + "\n";
    console.log(msg);
  };

  status("Loading config...");
  const cfg = await fetch("packages.json").then((r) => r.json());
  const packages = cfg.packages || [];
  const entry = cfg.entry || "main.py";

  status("Loading Pyodide...");
  const pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.4/full/",
  });

  pyodide.setStdout({ batched: (s) => out(s) });
  pyodide.setStderr({ batched: (s) => out("[err] " + s) });

  status("Installing packages from packages.json...");
  await pyodide.loadPackage("micropip");
  const micropip = pyodide.pyimport("micropip");
  for (const pkg of packages) {
    if (pkg === "micropip") continue;
    try {
      status("micropip.install: " + pkg);
      await micropip.install(pkg);
    } catch (e) {
      out("Package failed: " + pkg + " -> " + e);
    }
  }

  status("Loading " + entry + "...");
  const code = await fetch(entry).then((r) => r.text());
  status("Running...");
  try {
    await pyodide.runPythonAsync(code);
    status("Done.");
  } catch (e) {
    out(String(e));
    status("Error.");
  }
})();
