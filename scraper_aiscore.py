from playwright.sync_api import sync_playwright
import os
import json
import sys

ID_EQUIPO = int(sys.argv[1]) if len(sys.argv) > 1 else 4820

def extraer_y_guardar_sofascore(id_equipo):
    print(f"Iniciando raspado para el ID: {id_equipo}...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        url_perfil = f"https://www.sofascore.com/es/equipo/futbol/colombia/{id_equipo}"
        page.goto(url_perfil, wait_until="networkidle")

        print("Esperando carga...")

        page.wait_for_timeout(8000)

        page.screenshot(path="debug.png")

        print("URL actual:", page.url)
        print("Título:", page.title())

        page.wait_for_selector("body", timeout=15000)
        print("Extrayendo partidos...")

datos_partidos = page.evaluate("""() => {
    const resultados = [];

    const contenedorPrincipal =
        document.querySelector('main') ||
        document.querySelector('#__next');

    if (contenedorPrincipal) {
        const enlaces =
            Array.from(contenedorPrincipal.querySelectorAll('a'));

        enlaces.forEach(a => {
            const url = a.href;

            if (
                url &&
                (
                    url.includes('/evento/') ||
                    url.includes('/match/')
                ) &&
                !url.includes('/campeonato/')
            ) {

                let esGlobal =
                    a.closest('header') ||
                    a.closest('aside') ||
                    a.closest('[class*="Header"]') ||
                    a.closest('[class*="Sidebar"]');

                if (!esGlobal) {
                    let texto =
                        a.innerText
                        ? a.innerText.replace(/\\n/g,' ').trim()
                        : "Partido";

                    resultados.push({
                        info: texto,
                        url: url
                    });
                }
            }
        });
    }

    return resultados;

}""")

print("Encontrados:", len(datos_partidos))
print(datos_partidos[:3])

partidos_unicos = []
urls_vistas = set()

for item in datos_partidos:
    if item['url'] not in urls_vistas:
        urls_vistas.add(item['url'])
        partidos_unicos.append(item)

resultados_finales = partidos_unicos[:10]

if resultados_finales:
    ruta_repo = os.path.dirname(os.path.abspath(__file__))

    archivo_json = os.path.join(
        ruta_repo,
        f"{id_equipo}.json"
    )

    with open(archivo_json, "w", encoding="utf-8") as f:
        json.dump(
            resultados_finales,
            f,
            ensure_ascii=False,
            indent=4
        )

    print(f"[+] Archivo guardado en: {archivo_json}")

else:
    print("No se encontraron partidos.")

browser.close()    extraer_y_guardar_sofascore(ID_EQUIPO)
