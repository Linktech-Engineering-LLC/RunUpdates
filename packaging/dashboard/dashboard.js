async function loadDashboard() {
  const metaUrl = "metadata.json";

  let meta;
  try {
    const response = await fetch(metaUrl);
    meta = await response.json();
  } catch (err) {
    document.getElementById("build-info").innerHTML =
      "<p style='color:red'>Failed to load metadata.json</p>";
    return;
  }

  // Detect metadata version
  const isV2 = meta.meta_version === 2;

  // Build metadata (v1 fallback included)
  const build = isV2
    ? meta.build
    : {
        date: meta.date,
        commit: meta.commit,
        branch: "nightly",
        workflow_run_id: "N/A"
      };

  const toolchain = isV2
    ? meta.toolchain
    : {
        python: meta.python || "unknown",
        pyinstaller: meta.pyinstaller || "unknown"
      };

  // -----------------------------
  // ⭐ Update Badges
  // -----------------------------
  const shortCommit = build.commit ? build.commit.substring(0, 7) : "unknown";

  document.getElementById("version-badge").src =
    `https://img.shields.io/badge/version-${shortCommit}-blue`;

  document.getElementById("date-badge").src =
    `https://img.shields.io/badge/date-${encodeURIComponent(build.date)}-lightgrey`;

  document.getElementById("python-badge").src =
    `https://img.shields.io/badge/python-${toolchain.python}-yellow`;

  document.getElementById("pyi-badge").src =
    `https://img.shields.io/badge/pyinstaller-${toolchain.pyinstaller}-orange`;

  // -----------------------------
  // ⭐ Build Info Table
  // -----------------------------
  document.getElementById("build-info").innerHTML = `
    <table>
      <tr><th>Field</th><th>Value</th></tr>
      <tr><td>Date</td><td>${build.date}</td></tr>
      <tr><td>Commit</td><td>${build.commit}</td></tr>
      <tr><td>Branch</td><td>${build.branch}</td></tr>
      <tr><td>Workflow Run</td><td>${build.workflow_run_id}</td></tr>
    </table>
  `;

  // -----------------------------
  // ⭐ Artifact Table
  // -----------------------------
  const artifacts = isV2 ? meta.artifacts : meta.files;

  let rows = "";
  for (const a of artifacts) {
    rows += `
      <tr>
        <td>${a.name}</td>
        <td>${a.size}</td>
        <td>${a.sha256}</td>
        <td>${a.crc32}</td>
        <td>${a.type || "N/A"}</td>
        <td>${a.os || "N/A"}</td>
        <td>${a.arch || "N/A"}</td>
        <td><a href="https://github.com/Linktech-Engineering-LLC/RunUpdates/releases/download/nightly/${a.name}">Download</a></td>
      </tr>
    `;
  }

  document.getElementById("artifact-table").innerHTML = `
    <table>
      <tr>
        <th>Name</th>
        <th>Size</th>
        <th>SHA‑256</th>
        <th>CRC‑32</th>
        <th>Type</th>
        <th>OS</th>
        <th>Arch</th>
        <th>Download</th>
      </tr>
      ${rows}
    </table>
  `;
}

window.onload = loadDashboard;
