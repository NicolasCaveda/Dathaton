"""
CP -> poblacion estimada, para las 13 plazas de un solo CP por provincia (fuera de CABA y
Buenos Aires): 10 provincias con un unico CP en la lista de 47 (siempre su ciudad capital o
principal) + 3 de Santa Fe (Rosario, Rafaela, Santa Fe capital).

Correspondencia CP -> ciudad: confirmada por busqueda web (Correo Argentino / codigo-postal.ar,
etc.) para cada uno de los 13 CP. Ver CP_INFO.

Poblacion: los xlsx del Censo 2022 descargados solo tienen nivel departamento (no localidad), asi
que se usa la poblacion del departamento que contiene a esa ciudad -- nombres de departamento
verificados abriendo cada archivo, no adivinados.
"""

from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
OUT_CSV = HERE / "poblacion_por_cp_provincias.csv"

# cp -> (archivo xlsx, provincia, ciudad, departamento)
CP_INFO = {
    "2000": ("c2022_santafe_est_c1_21.xlsx", "Santa Fe", "Rosario", "Rosario"),
    "2300": ("c2022_santafe_est_c1_21.xlsx", "Santa Fe", "Rafaela", "Castellanos"),
    "3000": ("c2022_santafe_est_c1_21.xlsx", "Santa Fe", "Santa Fe (capital)", "La Capital"),
    "5000": ("c2022_cordoba_est_c1_6.xlsx", "Cordoba", "Cordoba (capital)", "Capital"),
    "4000": ("c2022_tucuman_est_c1_24.xlsx", "Tucuman", "San Miguel de Tucuman", "Capital"),
    "4400": ("c2022_salta_est_c1_17.xlsx", "Salta", "Salta (capital)", "Capital"),
    "3400": ("c2022_corrientes_est_c1_7.xlsx", "Corrientes", "Corrientes (capital)", "Capital"),
    "3500": ("c2022_chaco_est_c1_4.xlsx", "Chaco", "Resistencia", "San Fernando"),
    "8300": ("c2022_neuquen_est_c1_15.xlsx", "Neuquen", "Neuquen (capital)", "Confluencia"),
    "5300": ("c2022_larioja_est_c1_12.xlsx", "La Rioja", "La Rioja (capital)", "Capital"),
    "5730": ("c2022_sanluis_est_c1_19.xlsx", "San Luis", "Villa Mercedes", "General Pedernera"),
    "8400": ("c2022_rionegro_est_c1_16.xlsx", "Rio Negro", "San Carlos de Bariloche", "Bariloche"),
    "9100": ("c2022_chubut_est_c1_5.xlsx", "Chubut", "Trelew", "Rawson"),
}


def normalizar(nombre) -> str:
    import unicodedata
    nfkd = unicodedata.normalize("NFKD", str(nombre))
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tildes.strip().lower()


def poblacion_departamento(archivo: str, departamento: str) -> int:
    path = HERE / archivo
    xl = pd.ExcelFile(path)
    sheet = [s for s in xl.sheet_names if s.lower().startswith("cuadro")][0]
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    df.columns = ["codigo", "depto", "pob2010", "pob2022", "var_abs", "var_rel"]
    df["depto_norm"] = df["depto"].apply(normalizar)
    fila = df[df["depto_norm"] == normalizar(departamento)]
    if fila.empty:
        raise SystemExit(f"No se encontro el departamento {departamento!r} en {archivo}")
    return int(fila["pob2022"].iloc[0])


def main() -> None:
    filas = []
    for cp, (archivo, provincia, ciudad, departamento) in CP_INFO.items():
        pob = poblacion_departamento(archivo, departamento)
        filas.append({
            "cp": cp,
            "poblacion_estimada": pob,
            "zona": provincia,
            "ciudad": ciudad,
            "departamento": departamento,
            "metodo": f"poblacion 2022 de todo el Depto. {departamento} (censo no desagrega por localidad)",
        })

    tabla = pd.DataFrame(filas).sort_values("poblacion_estimada", ascending=False)
    tabla.to_csv(OUT_CSV, index=False)

    with pd.option_context("display.max_colwidth", 100, "display.width", 200):
        print(tabla.to_string(index=False))
    print(f"\nGuardado en {OUT_CSV}")


if __name__ == "__main__":
    main()
