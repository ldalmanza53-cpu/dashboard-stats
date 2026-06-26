import requests
import json
import sys
import time
from bs4 import BeautifulSoup

ID_EQUIPO = int(sys.argv[1]) if len(sys.argv) > 1 else 4820

def extraer_y_guardar_sofascore(id_equipo):
    print(f"Iniciando raspado del equipo: {id_equipo}")
    
    # Intentar mediante API de SofaScore (más confiable que Playwright)
    url_api = f"https://api.sofascore.com/api/v1/team/{id_equipo}/events/last/0"
    
    # Headers más realistas para evitar bloqueos
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json",
        "Referer": "https://www.sofascore.com/",
        "Accept-Language": "es-ES,es;q=0.9",
    }
    
    try:
        print(f"Solicitando: {url_api}")
        response = requests.get(url_api, headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Respuesta API exitosa")
        
        eventos = data.get("events", [])
        print(f"📊 Eventos encontrados: {len(eventos)}")
        
        partidos = []
        for evento in eventos[:10]:  # Top 10
            try:
                match_id = evento.get("id")
                home_team = evento.get("homeTeam", {}).get("name", "Equipo A")
                away_team = evento.get("awayTeam", {}).get("name", "Equipo B")
                status = evento.get("status", "").lower()
                score_home = evento.get("homeScore", {}).get("current", "-")
                score_away = evento.get("awayScore", {}).get("current", "-")
                
                # Construir URL del partido
                url_partido = f"https://www.sofascore.com/es/partido/futbol/{match_id}"
                
                # Texto descriptivo
                fecha = evento.get("startTimestamp", "")
                texto = f"{home_team} vs {away_team} | {score_home}-{score_away} | Estado: {status}"
                
                partidos.append({
                    "info": texto,
                    "url": url_partido,
                    "match_id": match_id,
                    "timestamp": fecha
                })
                
            except Exception as e:
                print(f"⚠️ Error procesando evento: {e}")
                continue
        
        # Guardar JSON
        archivo = f"{id_equipo}.json"
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(partidos, f, ensure_ascii=False, indent=4)
        
        print(f"\n✅ Guardado: {archivo}")
        print(f"📊 Total de partidos: {len(partidos)}")
        for p in partidos:
            print(f"  - {p['info']}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la solicitud HTTP: {e}")
        
        # Plan B: Intentar con Playwright como fallback
        print("\n⚠️ Intentando plan B con Playwright...")
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(
                    user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                url = f"https://www.sofascore.com/es/equipo/futbol/colombia/{id_equipo}"
                print(f"Abriendo: {url}")
                
                try:
                    page.goto(url, wait_until="networkidle", timeout=90000)
                    time.sleep(3)  # Esperar carga de JS
                    
                    # Extraer partidos usando JavaScript
                    partidos = page.evaluate("""
                    () => {
                        const results = [];
                        
                        // Selector 1: Enlaces de partidos
                        document.querySelectorAll('a[href*="/partido/"], a[href*="/match/"]').forEach(a => {
                            if (a.textContent.trim()) {
                                results.push({
                                    info: a.textContent.trim(),
                                    url: a.href
                                });
                            }
                        });
                        
                        return results.slice(0, 10);
                    }
                    """)
                    
                    # Guardar JSON
                    archivo = f"{id_equipo}.json"
                    with open(archivo, "w", encoding="utf-8") as f:
                        json.dump(partidos, f, ensure_ascii=False, indent=4)
                    
                    print(f"\n✅ Guardado con Playwright: {len(partidos)} partidos")
                    
                    # Captura de pantalla para debugging
                    page.screenshot(path="debug.png")
                    html = page.content()
                    with open("debug.html", "w", encoding="utf-8") as f:
                        f.write(html)
                    
                    page.close()
                    browser.close()
                    return len(partidos) > 0
                    
                except Exception as e:
                    print(f"❌ Error con Playwright: {e}")
                    try:
                        page.screenshot(path="debug.png")
                    except:
                        pass
                    page.close()
                    browser.close()
                    return False
                    
        except Exception as e:
            print(f"❌ Error importando Playwright: {e}")
            
            # Plan C: Guardar archivo vacío para evitar que el workflow falle
            archivo = f"{id_equipo}.json"
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump([], f)
            print(f"⚠️ Archivo vacío creado: {archivo}")
            return False

if __name__ == "__main__":
    success = extraer_y_guardar_sofascore(ID_EQUIPO)
    if not success:
        sys.exit(1)
