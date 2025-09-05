import matplotlib.pyplot as plt
import numpy as np
from flask import Flask, render_template, request, url_for
import io, base64

app = Flask(__name__)
plt.switch_backend("Agg")


# --- FUNCIÓN KOCH ---
def koch_curve(p1, p2, iteraciones):
    if iteraciones == 0:
        return [p1, p2]

    p1 = np.array(p1)
    p2 = np.array(p2)
    diff = (p2 - p1) / 3

    a = p1
    b = p1 + diff
    d = p1 + 2 * diff
    c = b + np.array([
        diff[0] * np.cos(np.pi / 3) - diff[1] * np.sin(np.pi / 3),
        diff[0] * np.sin(np.pi / 3) + diff[1] * np.cos(np.pi / 3)
    ])

    return (koch_curve(a, b, iteraciones - 1)[:-1] +
            koch_curve(b, c, iteraciones - 1)[:-1] +
            koch_curve(c, d, iteraciones - 1)[:-1] +
            koch_curve(d, p2, iteraciones - 1))


# --- OBTENER MITAD SEGÚN PARTE ---
def obtener_parte(puntos, parte):
    if not puntos:
        return []

    x, y = zip(*puntos)
    x = np.array(x)
    y = np.array(y)

    x_min, x_max = np.min(x), np.max(x)
    y_min, y_max = np.min(y), np.max(y)

    mask_superior = y >= np.mean(y)
    x_sup, y_sup = x[mask_superior], y[mask_superior]

    if parte == "superior":
        x_new, y_new = x_sup, y_sup
    elif parte == "inferior":
        y_new = y_max - (y_sup - y_min)
        x_new = x_sup
    elif parte == "derecha":
        x_new = y_sup - y_min
        y_new = x_max - x_sup
    elif parte == "izquierda":
        x_new = y_max - y_sup
        y_new = x_sup - x_min
    else:
        x_new, y_new = x, y

    return list(zip(x_new, y_new))


# --- HOME ---
@app.route("/", methods=["GET", "POST"])
def index():
    img = None
    parte = "superior"

    if request.method == "POST":
        parte = request.form["parte"]

        # Solo iteraciones 2 a 6
        iteraciones = list(range(2, 7))

        fig, axes = plt.subplots(1, len(iteraciones), figsize=(3 * len(iteraciones), 3))
        for i, it in enumerate(iteraciones):
            puntos = koch_curve([0, 0], [1, 0], it)
            puntos = obtener_parte(puntos, parte)
            x, y = zip(*puntos) if puntos else ([], [])
            axes[i].plot(x, y, color="black")
            axes[i].set_title(f"Iter {it}")
            axes[i].axis("equal")
            axes[i].axis("off")

        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight")
        plt.close()
        buf.seek(0)
        img = base64.b64encode(buf.getvalue()).decode("utf-8")

    return render_template("index.html", imagen=img, parte=parte)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
