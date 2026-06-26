// ==========================================
// CONFIGURACIÓN DEL REPOSITORIO
// ==========================================
const USUARIO = "ldalmanza53-cpu";
const REPOSITORIO = "dashboard-stats";

// Recupera o solicita el token de forma segura
function obtenerTokenSeguro() {
    let token = localStorage.getItem('mi_token_github');
    if (!token) {
        token = prompt("Por seguridad, introduce tu GitHub Personal Access Token (ghp_...):");
        if (token) {
            localStorage.setItem('mi_token_github', token);
        }
    }
    return token;
}

// BOTÓN 1: SÓLO ENCIENDE EL ROBOT EN LA NUBE
async function forzarRaspadoEnLaNube() {
    const idEquipo = document.getElementById('selector-equipo').value;
    if (!idEquipo) {
        alert("Por favor, escribe un ID de equipo primero.");
        return;
    }

    const GITHUB_TOKEN = obtenerTokenSeguro();
    if (!GITHUB_TOKEN) {
        alert("Se necesita el token para activar el robot.");
        return;
    }

    const botonRobot = document.querySelector(".control-panel button:nth-of-type(1)");
    const mensajeError = document.getElementById('mensaje-error');
    
    botonRobot.innerText = "🚀 Enviando orden...";
    botonRobot.disabled = true;

    try {
        const respuesta = await fetch(`https://api.github.com/repos/${USUARIO}/${REPOSITORIO}/actions/workflows/ejecutar_scraper.yml/dispatches`, {
            method: "POST",
            headers: {
                "Authorization": `token ${GITHUB_TOKEN}`,
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                ref: "main",
                inputs: {
                    id_equipo: idEquipo.toString()
                }
            })
        });

        if (respuesta.status === 204) {
            botonRobot.innerText = "✅ ¡Robot en camino!";
            mensajeError.innerText = `El robot está trabajando en el ID ${idEquipo}. Espera 45 segundos y luego presiona el botón verde 'Ver / Refrescar Tabla'.`;
            mensajeError.style.backgroundColor = "#1e293b";
            mensajeError.style.color = "#38bdf8";
            mensajeError.classList.remove('hidden');
            
            setTimeout(() => {
                botonRobot.innerText = "⚡ Despertar Robot";
                botonRobot.disabled = false;
            }, 5000);

        } else {
            throw new Error("No se pudo iniciar el robot.");
        }

    } catch (error) {
        console.error(error);
        botonRobot.innerText = "⚡ Despertar Robot";
        botonRobot.disabled = false;
        mensajeError.innerText = "Error al conectar con GitHub Actions. Verifica tu Token.";
        mensajeError.style.backgroundColor = "#2a1a1f";
        mensajeError.style.color = "#ef4444";
        mensajeError.classList.remove('hidden');
        localStorage.removeItem('mi_token_github');
    }
}

// BOTÓN 2: SÓLO BUSCA LOS DATOS EXISTENTES
// BOTÓN 2: BUSCA LOS DATOS DIRECTO DESDE LA API DE GITHUB (SOLUCIÓN DEFINITIVA)
async function buscarDatosExistentes(idEquipo) {
    const cuerpoTabla = document.getElementById('cuerpo-tabla');
    const mensajeError = document.getElementById('mensaje-error');
    const GITHUB_TOKEN = localStorage.getItem('mi_token_github');

    try {
        const respuesta = await fetch(`https://api.github.com/repos/${USUARIO}/${REPOSITORIO}/contents/${idEquipo}.json`, {
            headers: { "Authorization": `token ${GITHUB_TOKEN}` }
        });
        
        const data = await respuesta.json();
        
        // Decodificación segura
        const contenidoBase64 = data.content.replace(/\n/g, ''); 
        const jsonString = decodeURIComponent(escape(atob(contenidoBase64)));
        const partidos = JSON.parse(jsonString);
        
        cuerpoTabla.innerHTML = '';
        mensajeError.classList.add('hidden');

        partidos.forEach(partido => {
            // Protección avanzada: si viene vacío o son puros espacios, mostramos alerta
            let texto = partido.info;
            if (!texto || texto.trim() === "") {
                texto = "⚽ Partido detectado (Sin título renderizado)";
            }
            
            const enlace = partido.url ? partido.url : "#";
            
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${texto}</strong></td>
                <td><a href="${enlace}" target="_blank" class="btn-analisis">Ver Estadísticas</a></td>
            `;
            cuerpoTabla.appendChild(tr);
        });
        
    } catch (error) {
        console.error("Error final:", error);
        mensajeError.innerText = "Error: El robot no guardó bien los datos o el archivo está corrupto. Verifica la estructura en el archivo JSON.";
        mensajeError.classList.remove('hidden');
    }
}
function cambiarEquipo() {
    const idSeleccionado = document.getElementById('selector-equipo').value;
    if(idSeleccionado) buscarDatosExistentes(idSeleccionado);
}

document.addEventListener('DOMContentLoaded', () => {
    cambiarEquipo();
});
