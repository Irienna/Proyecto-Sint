const form = document.getElementById("entry-form");
const dateInput = document.getElementById("date");
const entriesBody = document.getElementById("entries-body");
const analysisOutput = document.getElementById("analysis-output");

function setDefaultDate() {
  const now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  dateInput.value = now.toISOString().slice(0, 16);
}

async function loadEntries() {
  const res = await fetch("/api/entries");
  const entries = await res.json();
  entriesBody.innerHTML = "";
  for (const entry of entries) {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${entry.date}</td>
      <td>${entry.foods.join(", ")}</td>
      <td>${entry.symptoms.join(", ")}</td>
      <td><button data-id="${entry.id}" class="delete-btn">Eliminar</button></td>
    `;
    entriesBody.appendChild(row);
  }

  document.querySelectorAll(".delete-btn").forEach((btn) => {
    btn.addEventListener("click", async () => {
      await fetch(`/api/entries/${btn.dataset.id}`, { method: "DELETE" });
      loadEntries();
      loadAnalysis();
    });
  });
}

async function loadAnalysis() {
  const res = await fetch("/api/analysis");
  const data = await res.json();

  if (data.not_enough_data) {
    analysisOutput.innerHTML = `<p class="muted">Necesitas al menos ${data.needed} registros para detectar patrones confiables (tienes ${data.count}).</p>`;
    return;
  }

  if (data.rules.length === 0) {
    analysisOutput.innerHTML = `<p class="muted">Aún no se detectan patrones claros en tus datos.</p>`;
    return;
  }

  analysisOutput.innerHTML = data.rules
    .map(
      (rule) => `
      <div class="rule">
        Cuando comes <strong>${rule.antecedent.join(", ")}</strong> →
        sientes <strong>${rule.consequent.join(", ")}</strong>
        (confianza ${(rule.confidence * 100).toFixed(0)}%, visto en ${rule.cases} de ${rule.total_matching_antecedent} casos)
      </div>
    `
    )
    .join("");
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const foods = document.getElementById("foods").value
    .split(",")
    .map((f) => f.trim())
    .filter(Boolean);

  const checkedSymptoms = Array.from(
    document.querySelectorAll('input[name="symptom-check"]:checked')
  ).map((el) => el.value);

  const extraSymptoms = document.getElementById("extra-symptoms").value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  const symptoms = [...checkedSymptoms, ...extraSymptoms];

  await fetch("/api/entries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date: dateInput.value, foods, symptoms }),
  });

  form.reset();
  setDefaultDate();
  loadEntries();
  loadAnalysis();
});

setDefaultDate();
loadEntries();
loadAnalysis();
