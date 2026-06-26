// ==========================================
// CONFIGURACIÓN DEL REPOSITORIO
// ==========================================
const USUARIO = "ldalmanza53-cpu";
const REPOSITORIO = "dashboard-stats";

// El token ya no se escribe aquí de forma fija por seguridad
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

async function dispararRobotEnLaNube(idEquipo) {
    const GITHUB_TOKEN = obtenerTokenSeguro();
    if (!GITHUB_TOKEN) {
        alert("Se necesita el token para activar el robot.");
        return;
    }

    const boton = document.querySelector(".control-panel button");
    const mensajeError = document.getElementById('mensaje-error');
    
    boton.innerText = "⚡ Despertando Robot...";
    boton.disabled = true;

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
            boton.innerText = "⏳ Raspando datos (Espera 45s)...";
            
            setTimeout(() => {
                boton.innerText = "Cargar Datos";
                boton.disabled = false;
                cargarPartidosPorId(idEquipo);
            }, 45000);

        } else {
            throw new Error("No se pudo iniciar el robot. Verifica tu Token.");
        }

    } catch (error) {
        console.error(error);
        boton.innerText = "Cargar Datos";
        boton.disabled = false;
        mensajeError.innerText = "Error de autenticación. Es posible que debas actualizar tu Token.";
        mensajeError.classList.remove('hidden');
        // Si falló, borramos el token guardado para que te lo vuelva a pedir la próxima vez
        localStorage.removeItem('mi_token_github');
    }
}

async function cargarPartidosPorId(idEquipo) {
    const cuerpoTabla = document.getElementById('cuerpo-tabla');
    const mensajeError = document.getElementById('mensaje-error');
    
    try {
        const timestampUnico = new Date().getTime();
        const respuesta = await fetch(`./${idEquipo}.json?nocache=${timestampUnico}`);
        
        if (!respuesta.ok) {
            dispararRobotEnLaNube(idEquipo);
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
    if(idSeleccionado) cargarPartidosPorId(idSeleccionado);
}

document.addEventListener('DOMContentLoaded', () => {
    cambiarEquipo();
});
