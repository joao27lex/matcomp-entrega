import numpy as np
import pandas as pd
from CubicSplineCustom import CubicSplineCustom
from Universo import Universo


def refinar_tempo_interceptacao_newton(spline_x, spline_y, v_proj, p0_x, p0_y, t0, max_iter=20, tol=1e-3):
    def f(t):
        x_ast = spline_x(t)
        y_ast = spline_y(t)
        dx = x_ast - p0_x
        dy = y_ast - p0_y
        d2 = dx**2 + dy**2
        return d2 - (v_proj**2) * t**2

    def df_dt(t, h=1e-3):
        return (f(t + h) - f(t - h)) / (2 * h)

    t = t0
    for _ in range(max_iter):
        ft = f(t)
        dft = df_dt(t)
        if abs(dft) < 1e-8:
            print("[WARN] Derivada muito pequena. Encerrando Newton-Raphson.")
            break
        t_new = t - ft / dft
        if abs(t_new - t) < tol:
            #print(f"[INFO] returning t_new = {t_new} | from refinar_tempo_interceptacao_newton")
            return t_new
        t = t_new
    print("[WARN] Newton-Raphson não convergiu após", max_iter, "iterações.")
    return t


def simular_projetil_com_newton(
    posicao_x_asteroide,
    posicao_y_asteroide,
    tempos_asteroide,
    velocidade_projetil,
    po_x,
    po_y,
    spline_x,
    spline_y,
):
    
    raio_do_planeta = 6.371e6
    tempo_impacto = None
    for i in range(len(posicao_x_asteroide)):
        
        dist = np.hypot(posicao_x_asteroide[i] - po_x, posicao_y_asteroide[i] - po_y)
        #print(f"[INFO] Posicao asteroide x: {posicao_x_asteroide[i]}, Posicao asteroide y: {posicao_y_asteroide[i]}")
        if dist <= raio_do_planeta:
            tempo_impacto = tempos_asteroide[i]
            #print(f"[INFO] Dist: {dist}")
            #print("[INFO] Tempo_impacto exist")
            break
    if tempo_impacto is None:
        #print("[INFO] Tempo_impacto is None")
        tempo_impacto = tempos_asteroide[-1]
    #print(f"[INFO] Tempo_impacto: {tempo_impacto}")

    melhor_ponto = None
    melhor_t = None
    menor_erro = float("inf")

    for i in range(len(tempos_asteroide)):
        t_ast = tempos_asteroide[i]
        if t_ast >= tempo_impacto:
            break
        x_ast = posicao_x_asteroide[i]
        y_ast = posicao_y_asteroide[i]
        d = np.hypot(x_ast - po_x, y_ast - po_y)
        tempo_projetil = d / velocidade_projetil
        erro = abs(tempo_projetil - t_ast)
        if erro < menor_erro:
            menor_erro = erro
            melhor_ponto = (x_ast, y_ast)
            melhor_t = t_ast

    if melhor_ponto is None:
        print("[ALERTA] Nenhuma interceptação possível antes da colisão.")
        return None


    t_refinado = refinar_tempo_interceptacao_newton(spline_x, spline_y, velocidade_projetil, po_x, po_y, melhor_t)

    if not np.isfinite(t_refinado):
        print("[ERRO] Tempo refinado inválido (NaN ou infinito). Abortando projétil.")
        return None

    x_ast = spline_x(t_refinado)
    y_ast = spline_y(t_refinado)
    direcao = np.array([x_ast - po_x, y_ast - po_y])
    dist = np.linalg.norm(direcao)

    if dist == 0:
        print("[ERRO] Vetor de direção nulo na interceptação. Abortando projétil.")
        return None

    t_proj = np.linspace(0, t_refinado, 200)
    direcao_unitaria = direcao / dist
    x_proj = po_x + velocidade_projetil * direcao_unitaria[0] * t_proj
    y_proj = po_y + velocidade_projetil * direcao_unitaria[1] * t_proj

    return pd.DataFrame({"x_proj": x_proj, "y_proj": y_proj, "tempo": t_proj})

    


if __name__ == "__main__":
    universo = Universo()
    solucao = universo.simular()

    terra = next(c for c in universo.corpos_celestes if c.name == "Terra")
    terra_x0, terra_y0 = terra.trace[0]

    asteroide = next(c for c in universo.corpos_celestes if c.name == "Asteroide")
    trajetoria_x = [p[0] for p in asteroide.trace]
    trajetoria_y = [p[1] for p in asteroide.trace]
    lista_tempos = np.linspace(0, universo.duracao, len(trajetoria_x))

    spline_real_x = CubicSplineCustom(lista_tempos, trajetoria_x)
    spline_real_y = CubicSplineCustom(lista_tempos, trajetoria_y)

    df_trajetoria_projetil = None

    df_trajetoria_projetil = simular_projetil_com_newton(
        posicao_x_asteroide=trajetoria_x,
        posicao_y_asteroide=trajetoria_y,
        tempos_asteroide=lista_tempos,
        #velocidade_projetil=3e5,
        velocidade_projetil=5e4,
        po_x=terra_x0,
        po_y=terra_y0,
        spline_x=spline_real_x,
        spline_y=spline_real_y,
        )

    universo.animar(solucao, df_trajetoria_projetil=df_trajetoria_projetil)