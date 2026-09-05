"""
CP -> poblacion estimada, para las 26 plazas de la provincia de Buenos Aires (21 del conurbano
+ La Plata, Mar del Plata, Bahia Blanca, Zarate, Campana).

Fuente de correspondencia CP<->localidad: cp_localidad_argentina.csv (24.742 filas, toda
Argentina), descargado de un gist publico de GitHub (lucsh/cb55fbcb4ff291c0368b7f43730cdd94,
archivo localidades.csv) que replica la vieja base de codigos postales de Correo Argentino
(pre-CPA). A diferencia de CABA, en el conurbano cada CP viejo corresponde en la practica a UNA
sola localidad principal (con barrios y "estafetas" adentro), asi que no hace falta reparto
proporcional: se identifica a mano, por CP, el partido y la(s) entidad(es) censales que le
corresponden (ver CP_INFO abajo, con la evidencia de cada eleccion).

Fuente de poblacion:
- c2022_rmba_entidades_c1.xlsx, hoja "Cuadro 1" (partido + entidad/localidad), para todos los
  CP salvo Mar del Plata y Bahia Blanca.
- c2022_bsas_est_c1_2.xlsx, hoja "Cuadro1.2" (poblacion total por partido, sin desagregar por
  localidad), para Mar del Plata (Partido de Gral. Pueyrredon) y Bahia Blanca (Partido de Bahia
  Blanca) -- esos dos archivos no traen el desglose por localidad, y no hace falta: en ambos
  partidos la ciudad que le da nombre concentra la enorme mayoria de la poblacion y no compite
  con ningun otro CP de las 47 plazas por el mismo partido.
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
RMBA_XLSX = HERE / "c2022_rmba_entidades_c1.xlsx"
BSAS_XLSX = HERE / "c2022_bsas_est_c1_2.xlsx"
OUT_CSV = HERE / "poblacion_por_cp_pba.csv"

# cp -> (partido(s), [entidades censales a sumar], nota)
# "TODAS" significa: sumar todas las entidades de ese partido (se usa solo cuando ningun otro CP
# de las 47 plazas compite por el mismo partido, asi que no hay riesgo de doble conteo).
CP_INFO = {
    "1609": [("San Isidro", ["Boulogne Sur Mer"])],
    "1613": [("Malvinas Argentinas", ["Los Polvorines"])],
    "1615": [("Malvinas Argentinas", ["Grand Bourg"])],
    "1617": [("Tigre", ["General Pacheco"])],
    "1653": [("General San Martin", ["Villa Ballester"])],
    "1665": [("Jose C. Paz", ["Jose C. Paz"])],
    "1678": [("Tres de Febrero", ["Caseros"])],
    "1686": [("Hurlingham", ["Hurlingham"])],
    "1704": [("La Matanza", ["Ramos Mejia"])],
    "1712": [("Moron", ["Castelar"])],
    "1716": [("Merlo", ["Libertad"])],
    "1722": [("Merlo", ["Merlo"])],
    "1744": [("Moreno", ["Moreno Centro", "Moreno Norte", "Moreno Sur"])],
    "1752": [("La Matanza", ["Lomas del Mirador"])],
    "1763": [("La Matanza", ["Virrey Del Pino"])],
    "1824": [("Lanus", ["Lanus Este", "Lanus Oeste"])],
    "1828": [("Lomas de Zamora", ["Banfield"])],
    "1852": [("Almirante Brown", ["Burzaco"])],
    "1875": [("Avellaneda", ["Wilde"])],
    # San Francisco Solano cruza el limite de dos partidos; se suman ambas partes.
    "1881": [("Almirante Brown", ["San Francisco Solano"]), ("Quilmes", ["San Francisco Solano"])],
    "1888": [("Florencio Varela", ["TODAS"])],
    "1900": [("La Plata", ["TODAS"])],
    "2800": [("Zarate", ["Zarate"])],
    "2804": [("Campana", ["Campana"])],
}

# CP resueltos con el total de partido (Cuadro1.2, sin desglose por localidad).
CP_PARTIDO_TOTAL = {
    "7600": "General Pueyrredon",
    "8000": "Bahia Blanca",
}


def normalizar(nombre) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", str(nombre))
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tildes.strip().lower()


def cargar_entidades_rmba() -> pd.DataFrame:
    df = pd.read_excel(RMBA_XLSX, sheet_name="Cuadro 1", header=None)
    df.columns = ["codigo", "partido", "categoria", "nombre", "viviendas", "poblacion"]
    df["partido_norm"] = df["partido"].astype(str).apply(normalizar)
    df["nombre_norm"] = df["nombre"].astype(str).apply(normalizar)
    return df[df["categoria"] == "Entidad"]


def cargar_totales_partido() -> pd.DataFrame:
    df = pd.read_excel(BSAS_XLSX, sheet_name="Cuadro1.2", header=None)
    df.columns = ["codigo", "partido", "pob2010", "pob2022", "var_abs", "var_rel"]
    df["partido_norm"] = df["partido"].astype(str).apply(normalizar)
    return df


def poblacion_partido(entidades: pd.DataFrame, partido: str, nombres: list[str]) -> tuple[int, list[str]]:
    partido_norm = normalizar(partido)
    sub = entidades[entidades["partido_norm"] == partido_norm]
    if nombres == ["TODAS"]:
        return int(sub["poblacion"].sum()), sub["nombre"].tolist()
    matches = sub[sub["nombre_norm"].isin([normalizar(n) for n in nombres])]
    faltantes = set(normalizar(n) for n in nombres) - set(matches["nombre_norm"])
    if faltantes:
        raise SystemExit(f"No matchean en partido {partido!r}: {faltantes}")
    return int(matches["poblacion"].sum()), matches["nombre"].tolist()


def main() -> None:
    entidades = cargar_entidades_rmba()
    totales = cargar_totales_partido()

    filas = []
    for cp, grupos in CP_INFO.items():
        poblacion_total = 0
        detalle = []
        for partido, nombres in grupos:
            pob, matched = poblacion_partido(entidades, partido, nombres)
            poblacion_total += pob
            detalle.append(f"{partido}: {', '.join(matched)} ({pob})")
        filas.append({
            "cp": cp,
            "poblacion_estimada": poblacion_total,
            "zona": "Buenos Aires",
            "metodo": "poblacion 2022 de la(s) localidad(es) censal(es) que corresponden a ese CP",
            "detalle": " | ".join(detalle),
        })

    for cp, partido in CP_PARTIDO_TOTAL.items():
        partido_norm = normalizar(partido)
        pob = int(totales.loc[totales["partido_norm"] == partido_norm, "pob2022"].iloc[0])
        filas.append({
            "cp": cp,
            "poblacion_estimada": pob,
            "zona": "Buenos Aires",
            "metodo": "poblacion 2022 de todo el partido (censo no desagrega por localidad en este archivo)",
            "detalle": f"{partido}: TODO EL PARTIDO ({pob})",
        })

    tabla = pd.DataFrame(filas).sort_values("poblacion_estimada", ascending=False)
    tabla.to_csv(OUT_CSV, index=False)

    with pd.option_context("display.max_colwidth", 100, "display.width", 200):
        print(tabla.to_string(index=False))
    print(f"\nGuardado en {OUT_CSV}")


if __name__ == "__main__":
    main()
