from playwright.sync_api import sync_playwright
import os
import json
import sys

ID_EQUIPO = int(sys.argv[1]) if len(sys.argv) > 1 else 4820


def extraer_y_guardar_sofascore(id_equipo):

    print(f"Iniciando raspado: {id_equipo}")

    with sync_playwright() as p:

        perfil = "/tmp/playwright-profile"

        context = p.chromium.launch_persistent_context(
            perfil,

            headless=True,

            viewport={
                "width": 1280,
                "height": 720
            },

            user_agent=(
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "(KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),

            locale="es-ES",

            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage"
            ]
        )

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        page.set_extra_http_headers({
            "Accept-Language": "es-ES,es;q=0.9"
        })

        url = (
            f"https://www.sofascore.com/"
            f"es/equipo/futbol/"
            f"colombia/{id_equipo}"
        )

        print("Abriendo:", url)

        page.goto(
            url,
            wait_until="commit",
            timeout=90000
        )

        page.wait_for_timeout(15000)

        print("Pequeño scroll igual que local")

        page.evaluate(
            "window.scrollBy(0,500)"
        )

        page.wait_for_timeout(2000)

        page.screenshot(
            path="debug.png"
        )

        with open(
            "debug.html",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                page.content()
            )

        print("Extrayendo partidos...")

        print("Titulo:", page.title())

        print(
            "Body:",
            page.locator("body")
            .inner_text()[:1000]
        )

        datos = page.evaluate("""
        () => {

            const resultados=[];

            const root=
                document.querySelector("main")
                ||
                document.querySelector("#__next");

            if(!root)
                return [];

            const enlaces=
                Array.from(
                    root.querySelectorAll("a")
                );

            enlaces.forEach(a=>{

                const url=a.href;

                if(
                    url
                    &&
                    (
                        url.includes("/evento/")
                        ||
                        url.includes("/match/")
                    )
                    &&
                    !url.includes("/campeonato/")
                ){

                    const texto=
                        (
                            a.innerText
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

        print("Encontrados:", len(datos))

        vistos=set()
        finales=[]

        for x in datos:

            if x["url"] not in vistos:

                vistos.add(
                    x["url"]
                )

                finales.append(
                    x
                )

        finales=finales[:10]

        archivo=f"{id_equipo}.json"

        with open(
            archivo,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                finales,
                f,
                ensure_ascii=False,
                indent=4
            )

        print("Guardado:", archivo)

        context.close()


if __name__=="__main__":
    extraer_y_guardar_sofascore(
        ID_EQUIPO
    )
