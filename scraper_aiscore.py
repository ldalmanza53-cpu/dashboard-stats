from playwright.sync_api import sync_playwright
import os
import json
import sys

ID_EQUIPO = int(sys.argv[1]) if len(sys.argv) > 1 else 4820


def extraer_y_guardar_sofascore(id_equipo):
    print(f"Iniciando raspado para el ID: {id_equipo}...")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            ),
            viewport={
                "width": 1366,
                "height": 768
            },
            locale="es-ES",
            timezone_id="America/Bogota"
        )

        page = context.new_page()

        page.set_extra_http_headers({
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/"
        })

        url_perfil = (
            f"https://www.sofascore.com/es/equipo/"
            f"futbol/colombia/{id_equipo}"
        )

        print("Abriendo página...")

        page.goto(
            url_perfil,
            wait_until="domcontentloaded",
            timeout=60000
        )

        print("Esperando carga...")

        page.wait_for_timeout(12000)

        page.screenshot(path="debug.png")

        print("Captura guardada")
        print("URL actual:", page.url)

        try:
            print("Título:", page.title())
        except:
            print("No se pudo obtener el título")

        page.wait_for_selector("body", timeout=15000)

        print("Extrayendo partidos...")

        datos_partidos = page.evaluate("""() => {

            const resultados = [];

            const contenedor =
                document.querySelector("main") ||
                document.querySelector("#__next") ||
                document.body;

            const enlaces =
                Array.from(
                    contenedor.querySelectorAll("a[href]")
                );

            enlaces.forEach(a => {

                const url = a.href || "";

                if (
                    url.includes("/match/")
                ) {

                    const texto =
                        (
                            a.innerText ||
                            a.textContent ||
                            "Partido"
                        )
                        .replace(/\\n/g, " ")
                        .trim();

                    resultados.push({
                        info: texto,
                        url: url
                    });
                }

            });

            return resultados;

        }""")

        print("Encontrados:", len(datos_partidos))

        if datos_partidos:
            print(datos_partidos[:3])

        partidos_unicos = []
        urls_vistas = set()

        for item in datos_partidos:

            if item["url"] not in urls_vistas:

                urls_vistas.add(item["url"])
                partidos_unicos.append(item)

        resultados_finales = partidos_unicos[:10]

        if resultados_finales:

            ruta_repo = os.path.dirname(
                os.path.abspath(__file__)
            )

            archivo_json = os.path.join(
                ruta_repo,
                f"{id_equipo}.json"
            )

            with open(
                archivo_json,
                "w",
                encoding="utf-8"
            ) as f:

                json.dump(
                    resultados_finales,
                    f,
                    ensure_ascii=False,
                    indent=4
                )

            print(f"[+] Archivo guardado en: {archivo_json}")

        else:
            print("No se encontraron partidos")

        context.close()
        browser.close()


if __name__ == "__main__":
    extraer_y_guardar_sofascore(ID_EQUIPO)
