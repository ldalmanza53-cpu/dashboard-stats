from playwright.sync_api import sync_playwright
import os
import json
import sys

ID_EQUIPO = int(sys.argv[1]) if len(sys.argv) > 1 else 4820


def extraer_y_guardar_sofascore(id_equipo):

    print(f"Iniciando raspado para ID {id_equipo}")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-blink-features=AutomationControlled"
            ]
        )

        context = browser.new_context(
            viewport={
                "width": 1366,
                "height": 768
            },
            locale="es-ES",
            timezone_id="America/Bogota",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()

        page.set_extra_http_headers({
            "Accept-Language": "es-ES,es;q=0.9",
            "Referer": "https://www.google.com/"
        })

        url = (
            f"https://www.sofascore.com/es/equipo/"
            f"futbol/colombia/{id_equipo}"
        )

        print("Abriendo:", url)

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=90000
        )

        page.wait_for_timeout(10000)

        print("Haciendo scroll...")

        for _ in range(6):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(2500)

        print("Esperando carga final...")

        page.wait_for_timeout(8000)

        page.screenshot(path="debug.png")

        with open(
            "debug.html",
            "w",
            encoding="utf-8"
        ) as f:
            f.write(page.content())

        print("Capturas guardadas")

        print("URL:", page.url)

        try:
            print("Título:", page.title())
        except:
            pass

        datos = page.evaluate("""
() => {

const resultados=[];

document.querySelectorAll("a").forEach(a=>{

const url=a.href||"";

if(
url.includes("/match/")
||
url.includes("/evento/")
){

const texto=
(
a.innerText
||
a.textContent
||
"Partido"
)
.replace(/\\n/g," ")
.trim();

resultados.push({
info:texto,
url:url
});

}

});

return resultados;

}
""")

        print("Links encontrados:", len(datos))

        unicos = []
        vistas = set()

        for x in datos:

            if x["url"] not in vistas:

                vistas.add(x["url"])
                unicos.append(x)

        resultados = unicos[:15]

        print("Únicos:", len(resultados))

        ruta = os.path.dirname(
            os.path.abspath(__file__)
        )

        archivo = os.path.join(
            ruta,
            f"{id_equipo}.json"
        )

        with open(
            archivo,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                resultados,
                f,
                indent=4,
                ensure_ascii=False
            )

        print("JSON creado:", archivo)

        context.close()
        browser.close()


if __name__ == "__main__":
    extraer_y_guardar_sofascore(ID_EQUIPO)
