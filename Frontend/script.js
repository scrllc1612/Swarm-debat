

// =====================================
// API URL
// =====================================
const API_URL = "https://molar-lunchtime-haste.ngrok-free.dev";
//const API_URL = "http://127.0.0.1:8000";

// =====================================
// ELEMENTOS
// =====================================

const frameworkSelect = document.getElementById("framework");
const arquitecturaSelect = document.getElementById("arquitectura");
const temaInput = document.getElementById("tema");

const btnGenerar = document.getElementById("btnGenerar");
const btnEvaluar = document.getElementById("btnEvaluar");
const btnLimpiar = document.getElementById("btnLimpiar");

const resultadoDebate = document.getElementById("resultadoDebate");

const frameworkInfo = document.getElementById("frameworkInfo");
const arquitecturaInfo = document.getElementById("arquitecturaInfo");

const statusBadge = document.getElementById("statusBadge");

const loaderOverlay = document.getElementById("loaderOverlay");

const evaluationModal = document.getElementById("evaluationModal");
const evaluationResults = document.getElementById("evaluationResults");

const closeModal = document.getElementById("closeModal");

// =====================================
// GENERAR DEBATE
// =====================================

btnGenerar.addEventListener("click", async () => {

    const tema = temaInput.value.trim();
    const framework = frameworkSelect.value;
    const arquitectura = arquitecturaSelect.value;

    // =========================
    // VALIDACIÓN
    // =========================

    if (!tema) {

        alert("Ingrese un tema para el debate");
        return;
    }

    // =========================
    // MOSTRAR LOADER
    // =========================

    loaderOverlay.style.display = "flex";

    statusBadge.innerText = "Generando debate...";

    try {

        // =========================
        // REQUEST
        // =========================

        const response = await fetch(
            `${API_URL}/generar-debate`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    tema,
                    framework,
                    arquitectura
                })
            }
        );

        const data = await response.json();

        // =========================
        // ERROR
        // =========================

        if (data.error) {

            alert(data.error);
            console.error(data.detalle);

            loaderOverlay.style.display = "none";

            statusBadge.innerText = "Error";

            return;
        }

        // =========================
        // ACTUALIZAR INFO
        // =========================

        frameworkInfo.innerText =
            framework.toUpperCase();

        arquitecturaInfo.innerText =
            data.arquitectura;

        statusBadge.innerText =
            "Debate generado";

        // =========================
        // MOSTRAR DEBATE
        // =========================

        resultadoDebate.innerText =
            data.debate;

        // =========================
        // SCROLL TOP
        // =========================

        resultadoDebate.scrollTop = 0;

    } catch (error) {

        console.error(error);

        alert("Error conectando con el backend");

        statusBadge.innerText = "Error";

    } finally {

        loaderOverlay.style.display = "none";
    }
});

// =====================================
// EVALUAR DEBATE
// =====================================

btnEvaluar.addEventListener("click", async () => {

    evaluationModal.style.display = "flex";

    evaluationResults.innerHTML = `
        <div class="loading">
            Evaluando debate...
        </div>
    `;

    try {

        const response = await fetch(
            `${API_URL}/evaluar-debate`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        // =========================
        // ERROR
        // =========================

        if (data.error) {

            evaluationResults.innerHTML = `
                <p>${data.error}</p>
            `;

            return;
        }

        // =========================
// MOSTRAR RESULTADOS
// =========================

        let html = `

    <div class="evaluation-section">

        <h3>
            Información General
        </h3>

        <div class="metric-card">
            <span>Tema</span>
            <strong>${data.tema}</strong>
        </div>

        <div class="metric-card">
            <span>Arquitectura</span>
            <strong>${data.arquitectura}</strong>
        </div>

    </div>

`;


// =====================================
// EVALUACIÓN GENERAL
// =====================================

        if (data.evaluacion_general) {

            html += `
        <div class="evaluation-section">

            <h3>
                Evaluación General
            </h3>

            <div class="metrics-grid">
    `;

            for (const key in data.evaluacion_general) {

                html += `
            <div class="metric-card">

                <span>
                    ${key.replaceAll("_", " ")}
                </span>

                <strong>
                    ${data.evaluacion_general[key]}
                </strong>

            </div>
        `;
            }

            html += `
            </div>

        </div>
    `;
        }


// =====================================
// EVALUACIÓN POR AGENTE
// =====================================

        if (data.evaluacion_por_agente) {

            html += `
        <div class="evaluation-section">

            <h3>
                Evaluación por Agente
            </h3>
    `;

            for (const agente in data.evaluacion_por_agente) {

                const agenteData =
                    data.evaluacion_por_agente[agente];

                if (!agenteData) continue;

                html += `
            <div class="agent-section">

                <h4>
                    ${agente.toUpperCase()}
                </h4>

                <div class="metrics-grid">
        `;

                for (const key in agenteData) {

                    html += `
                <div class="metric-card">

                    <span>
                        ${key.replaceAll("_", " ")}
                    </span>

                    <strong>
                        ${agenteData[key]}
                    </strong>

                </div>
            `;
                }

                html += `
                </div>

            </div>
        `;
            }

            html += `
        </div>
    `;
        }


// =====================================
// PARTES DETECTADAS
// =====================================

        if (data.partes_detectadas) {

            html += `
        <div class="evaluation-section">

            <h3>
                Partes Detectadas
            </h3>

            <div class="metrics-grid">
    `;

            for (const key in data.partes_detectadas) {

                const valor =
                    data.partes_detectadas[key];

                html += `
            <div class="metric-card">

                <span>
                    ${key.replaceAll("_", " ")}
                </span>

                <strong>
                    ${valor ? "Sí" : "No"}
                </strong>

            </div>
        `;
            }

            html += `
            </div>

        </div>
    `;
        }


// =====================================
// OBSERVACIÓN GENERAL
// =====================================

        if (data.observacion_general) {

            html += `
        <div class="evaluation-section">

            <h3>
                Observación General
            </h3>

            <div class="observation-box">

                ${data.observacion_general}

            </div>

        </div>
    `;
        }

        evaluationResults.innerHTML = html;

    } catch (error) {

        console.error(error);

        evaluationResults.innerHTML = `
            <p>Error evaluando debate</p>
        `;
    }
});

// =====================================
// LIMPIAR
// =====================================

btnLimpiar.addEventListener("click", () => {

    temaInput.value = "";

    frameworkSelect.value = "langflow";

    arquitecturaSelect.value = "A1";

    frameworkInfo.innerText = "-";

    arquitecturaInfo.innerText = "-";

    statusBadge.innerText =
        "Esperando ejecución...";

    resultadoDebate.innerHTML = `
        <div class="placeholder">

            <h3>
                Sistema listo
            </h3>

            <p>
                Selecciona un framework,
                una arquitectura y genera un debate.
            </p>

        </div>
    `;
});

// =====================================
// CERRAR MODAL
// =====================================

closeModal.addEventListener("click", () => {

    evaluationModal.style.display = "none";
});

// =====================================
// CERRAR MODAL CLICK FUERA
// =====================================

window.addEventListener("click", (e) => {

    if (e.target === evaluationModal) {

        evaluationModal.style.display = "none";
    }
});