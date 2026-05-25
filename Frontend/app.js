const API_URL = "https://molar-lunchtime-haste.ngrok-free.dev";

// =====================================================
// GENERAR DEBATE
// =====================================================

async function generarDebate() {

    const tema = document.getElementById("tema").value;

    const arquitectura = document.getElementById("arquitectura").value;

    const debateDiv = document.getElementById("debate");

    const metricasDiv = document.getElementById("metricas");

    const btnGenerar = document.getElementById("btnGenerar");

    const btnEvaluar = document.getElementById("btnEvaluar");

    if (!tema.trim()) {

        alert("Por favor, escribe un tema para el debate.");

        return;
    }

    // ======================================
    // Estado de carga
    // ======================================

    btnGenerar.disabled = true;

    btnGenerar.innerText = "Generando...";

    if (btnEvaluar) {

        btnEvaluar.disabled = true;

        btnEvaluar.innerText = "Evaluar debate";
    }

    debateDiv.innerHTML = `
        <div class="loading-box">
            <div class="spinner"></div>
            <span>
                Generando debate con arquitectura ${arquitectura}...
            </span>
        </div>
    `;

    metricasDiv.innerHTML = `
        <p>
            Aquí aparecerán los resultados de evaluación.
        </p>
    `;

    try {

        // ======================================
        // Request backend
        // ======================================

        const response = await fetch(`${API_URL}/generar-debate`, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                tema: tema,
                arquitectura: arquitectura
            })
        });

        const data = await response.json();

        console.log("RESPUESTA GENERAR DEBATE:", data);

        // ======================================
        // Error backend
        // ======================================

        if (data.error) {

            debateDiv.innerHTML = `
                <div class="error-box">
                    <h3>Error</h3>
                    <p>${data.detalle || data.error}</p>
                </div>
            `;

            return;
        }

        // ======================================
        // Mostrar debate
        // ======================================

        debateDiv.innerHTML = `
            <h2>${data.arquitectura}</h2>

            <pre class="debate-output">
${data.debate || "No se recibió debate desde el backend."}
            </pre>
        `;

    } catch (error) {

        debateDiv.innerHTML = `
            <div class="error-box">
                <h3>Error de conexión</h3>
                <p>${error}</p>
            </div>
        `;

    } finally {

        btnGenerar.disabled = false;

        btnGenerar.innerText = "Generar debate";

        if (btnEvaluar) {

            btnEvaluar.disabled = false;

            btnEvaluar.innerText = "Evaluar debate";
        }
    }
}


// =====================================================
// EVALUAR DEBATE
// =====================================================

async function evaluarDebate() {

    const metricasDiv = document.getElementById("metricas");

    const btnEvaluar = document.getElementById("btnEvaluar");

    if (btnEvaluar) {

        btnEvaluar.disabled = true;

        btnEvaluar.innerText = "Evaluando...";
    }

    metricasDiv.innerHTML = `
        <div class="loading-box">
            <div class="spinner"></div>
            <span>
                Evaluando métricas del debate...
            </span>
        </div>
    `;

    try {

        // ======================================
        // Request backend
        // ======================================

        const response = await fetch(`${API_URL}/evaluar-debate`, {

            method: "POST"
        });

        const data = await response.json();

        console.log("RESPUESTA EVALUAR DEBATE:", data);

        // ======================================
        // Error backend
        // ======================================

        if (data.error) {

            metricasDiv.innerHTML = `
                <div class="error-box">
                    <h3>Error</h3>
                    <p>${data.error}</p>
                </div>
            `;

            return;
        }

        // ======================================
        // Render dinámico
        // ======================================

        if (data.arquitectura.includes("A2")) {

            renderA2(data);

        } else if (data.arquitectura.includes("A4")) {

            renderA4(data);

        } else {

            metricasDiv.innerHTML = `
                <div class="error-box">
                    <h3>Error</h3>
                    <p>
                        Arquitectura no soportada para visualización.
                    </p>
                </div>
            `;
        }

    } catch (error) {

        metricasDiv.innerHTML = `
            <div class="error-box">
                <h3>Error de conexión</h3>
                <p>${error}</p>
            </div>
        `;

    } finally {

        if (btnEvaluar) {

            btnEvaluar.disabled = false;

            btnEvaluar.innerText = "Evaluar debate";
        }
    }
}


// =====================================================
// RENDER A2
// =====================================================

function renderA2(data) {

    const metricasDiv = document.getElementById("metricas");

    const general = data.evaluacion_general || {};

    const agentes = data.evaluacion_por_agente || {};

    const proponente = agentes.proponente || {};

    const oponente = agentes.oponente || {};

    const replica = agentes.replica_proponente || {};

    function valor(obj, campo) {

        return obj && obj[campo] !== undefined
            ? obj[campo] + "/5"
            : "No detectado";
    }

    function valorSimple(obj, campo) {

        return obj && obj[campo] !== undefined
            ? obj[campo]
            : "No detectado";
    }

    metricasDiv.innerHTML = `

        <h2>${data.arquitectura}</h2>

        <h3>Evaluación general del debate</h3>

        <table>

            <tr>
                <th>Métrica</th>
                <th>Puntaje</th>
            </tr>

            <tr>
                <td>Calidad argumentativa</td>
                <td>${valor(general, "calidad_argumentativa")}</td>
            </tr>

            <tr>
                <td>Coherencia</td>
                <td>${valor(general, "coherencia")}</td>
            </tr>

            <tr>
                <td>Formalidad académica</td>
                <td>${valor(general, "formalidad_academica")}</td>
            </tr>

            <tr>
                <td>Uso de evidencia</td>
                <td>${valor(general, "uso_evidencia")}</td>
            </tr>

            <tr>
                <td>Capacidad de refutación</td>
                <td>${valor(general, "capacidad_refutacion")}</td>
            </tr>

            <tr>
                <td><strong>Promedio general</strong></td>
                <td><strong>${valor(general, "promedio")}</strong></td>
            </tr>

            <tr>
                <td>Nivel</td>
                <td>${valorSimple(general, "nivel")}</td>
            </tr>

        </table>

        <h3>Evaluación por agente</h3>

        <table>

            <tr>
                <th>Criterio</th>
                <th>Proponente</th>
                <th>Oponente</th>
                <th>Réplica</th>
            </tr>

            <tr>
                <td>Calidad argumentativa</td>
                <td>${valor(proponente, "calidad_argumentativa")}</td>
                <td>${valor(oponente, "calidad_argumentativa")}</td>
                <td>${valor(replica, "calidad_argumentativa")}</td>
            </tr>

            <tr>
                <td>Coherencia</td>
                <td>${valor(proponente, "coherencia")}</td>
                <td>${valor(oponente, "coherencia")}</td>
                <td>${valor(replica, "coherencia")}</td>
            </tr>

            <tr>
                <td>Formalidad académica</td>
                <td>${valor(proponente, "formalidad_academica")}</td>
                <td>${valor(oponente, "formalidad_academica")}</td>
                <td>${valor(replica, "formalidad_academica")}</td>
            </tr>

            <tr>
                <td>Uso de evidencia</td>
                <td>${valor(proponente, "uso_evidencia")}</td>
                <td>${valor(oponente, "uso_evidencia")}</td>
                <td>${valor(replica, "uso_evidencia")}</td>
            </tr>

            <tr>
                <td>Capacidad de refutación</td>
                <td>${valor(proponente, "capacidad_refutacion")}</td>
                <td>${valor(oponente, "capacidad_refutacion")}</td>
                <td>${valor(replica, "capacidad_refutacion")}</td>
            </tr>

            <tr>
                <td><strong>Promedio</strong></td>
                <td><strong>${valor(proponente, "promedio")}</strong></td>
                <td><strong>${valor(oponente, "promedio")}</strong></td>
                <td><strong>${valor(replica, "promedio")}</strong></td>
            </tr>

            <tr>
                <td>Nivel</td>
                <td>${valorSimple(proponente, "nivel")}</td>
                <td>${valorSimple(oponente, "nivel")}</td>
                <td>${valorSimple(replica, "nivel")}</td>
            </tr>

        </table>

        <h3>Partes detectadas</h3>

        <p>
            <strong>Proponente detectado:</strong>
            ${data.partes_detectadas?.proponente_detectado ? "Sí" : "No"}
        </p>

        <p>
            <strong>Oponente detectado:</strong>
            ${data.partes_detectadas?.oponente_detectado ? "Sí" : "No"}
        </p>

        <p>
            <strong>Réplica detectada:</strong>
            ${data.partes_detectadas?.replica_detectada ? "Sí" : "No"}
        </p>

        <h3>Observación general</h3>

        <p>${data.observacion_general}</p>
    `;
}


// =====================================================
// RENDER A4 SWARM
// =====================================================

function renderA4(data) {

    const metricasDiv = document.getElementById("metricas");

    const general = data.evaluacion_general || {};

    const swarm = data.evaluacion_swarm || {};

    const proponente = swarm.proponente || {};

    const oponente = swarm.oponente || {};

    const analisis = swarm.analisis_comparativo || {};

    metricasDiv.innerHTML = `

        <h2>${data.arquitectura}</h2>

        <h3>Evaluación general swarm</h3>

        <table>
            <tr>
                <th>Métrica</th>
                <th>Puntaje</th>
            </tr>

            <tr>
                <td>Calidad argumentativa</td>
                <td>${general.calidad_argumentativa}/5</td>
            </tr>

            <tr>
                <td>Coherencia</td>
                <td>${general.coherencia}/5</td>
            </tr>

            <tr>
                <td>Formalidad académica</td>
                <td>${general.formalidad_academica}/5</td>
            </tr>

            <tr>
                <td>Uso de evidencia</td>
                <td>${general.uso_evidencia}/5</td>
            </tr>

            <tr>
                <td>Capacidad de refutación</td>
                <td>${general.capacidad_refutacion}/5</td>
            </tr>

            <tr>
                <td>Integración swarm</td>
                <td>${general.integracion_swarm}/5</td>
            </tr>

            <tr>
                <td><strong>Promedio</strong></td>
                <td><strong>${general.promedio}/5</strong></td>
            </tr>

            <tr>
                <td>Nivel</td>
                <td>${general.nivel}</td>
            </tr>
        </table>

        <h3>Evaluación distribuida</h3>

        <table>

            <tr>
                <th>Métrica</th>
                <th>Proponente</th>
                <th>Oponente</th>
                <th>Análisis</th>
            </tr>

            <tr>
                <td>Promedio</td>
                <td>${proponente.promedio || "N/D"}/5</td>
                <td>${oponente.promedio || "N/D"}/5</td>
                <td>${analisis.promedio || "N/D"}/5</td>
            </tr>

            <tr>
                <td>Nivel</td>
                <td>${proponente.nivel || "N/D"}</td>
                <td>${oponente.nivel || "N/D"}</td>
                <td>${analisis.nivel || "N/D"}</td>
            </tr>

        </table>

        <h3>Partes detectadas</h3>

        <p>
            <strong>Proponente:</strong>
            ${data.partes_detectadas?.proponente_detectado ? "Sí" : "No"}
        </p>

        <p>
            <strong>Oponente:</strong>
            ${data.partes_detectadas?.oponente_detectado ? "Sí" : "No"}
        </p>

        <p>
            <strong>Análisis comparativo:</strong>
            ${data.partes_detectadas?.analisis_detectado ? "Sí" : "No"}
        </p>

        <h3>Observación general</h3>

        <p>${data.observacion_general}</p>
    `;
}