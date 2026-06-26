async function cargarPartidosPorId(idEquipo) {
    const cuerpoTabla = document.getElementById('cuerpo-tabla');
    const mensajeError = document.getElementById('mensaje-error');
    
    try {
        // Truco definitivo: Rompemos la caché agregando un número único de tiempo al final
        const timestampUnico = new Date().getTime();
        
        // Forzamos la lectura exacta del archivo JSON correspondiente
        const respuesta = await fetch(`./${idEquipo}.json?nocache=${timestampUnico}`);
        
        if (!respuesta.ok) throw new Error('Archivo no encontrado');
        
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
        console.error("Detalle del error al cargar el JSON:", error);
    }
}

function cambiarEquipo() {
    const idSeleccionado = document.getElementById('selector-equipo').value;
    if(idSeleccionado) cargarPartidosPorId(idSeleccionado);
}

document.addEventListener('DOMContentLoaded', () => {
    cambiarEquipo();
});
