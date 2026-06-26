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

    // Buscamos el botón de despertar (el primero del panel)
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
            botonRobot.innerText = "✅ ¡Robot activado en la nube!";
            mensajeError.innerText = `El robot está raspando el ID ${idEquipo}. Espera unos 45-60 segundos y luego presiona el botón verde 'Ver / Refrescar Tabla'.`;
            mensajeError.style.backgroundColor = "#1e293b";
            mensajeError.style.color = "#38bdf8";
            mensajeError.classList.remove('hidden');
            
            // Restauramos el botón después de 5 segundos
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

// BOTÓN 2: SÓLO BUSCA LOS DATOS LOCALES EXILESTENTES
async function buscarDatosExistentes(idEquipo) {
    const cuerpoTabla = document.getElementById('cuerpo-tabla');
    const mensajeError = document.getElementById('mensaje-error');
    
    try {
        const timestampUnico = new Date().getTime();
        const respuesta = await fetch(`./${idEquipo}.json?nocache=${timestampUnico}`);
        
        if (!respuesta.ok) {
            cuerpoTabla.innerHTML = '';
            mensajeError.innerText = `No se encontraron datos listos en internet para el ID ${idEquipo}. Si ya despertaste al robot, espera unos segundos más y vuelve a presionar el botón verde. Si es un ID nuevo, presiona primero el botón rojo.`;
            mensajeError.style.backgroundColor = "#2a1a1f";
            mensajeError.style.color = "#ef4444";
            mensajeError.classList.remove('hidden');
            return;
        }
        
        const partidos = await respuesta.json();
        cuerpoTabla.innerHTML = '';
        mensajeError.classList.add('hidden');

        partidos.forEach(partido => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${partido.info}</strong></td>
                <td><a href="${partido.url}" target="_blank" class="btn-analisis">Ver Estadísticas</a></td>
            `;
            cuerpoTabla.appendChild(tr);
        });
        
    } catch (error) {
        cuerpoTabla.innerHTML = '';
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
