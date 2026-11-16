# Correlación parcial y GLM por zona

Para «¿cuánto explica X de Y controlando por Z?» con datos por municipio o zona. El orden es siempre el mismo: modelo sin espacio, Moran de sus residuos y, si es significativo, [regresion-espacial.md](regresion-espacial.md).

## Correlación parcial

- Regresa `x` y `y` sobre los controles (Frisch–Waugh) y correlaciona los residuos: eso es la correlación parcial r.
- Con k controles y n zonas, `t = r·√((n−2−k)/(1−r²))` con n−2−k grados de libertad. Es el t del coeficiente de `x` en el MCO de `y` sobre `x` y los controles: si no coincide, hay un error.
- IC de Fisher: `z = arctanh(r)`, error típico `1/√(n−3−k)`, y se deshace con `tanh`.
- Si los residuos tienen autocorrelación espacial (Moran de residuos significativo), la p es optimista: el n efectivo es menor. Se pasa a SEM o SAR, o se declara.

## Conteos y tasas

- Conteos con población en riesgo: binomial negativa con `offset = log(población)` (`sm.NegativeBinomial(y, X, offset=...)` o `sm.GLM` con `family=NegativeBinomial`). Poisson solo si no hay sobredispersión: compara α y AIC.
- Proporciones: `sm.GLM(y, X, family=sm.families.Binomial(), var_weights=denominador)`; con sobredispersión, quasi-binomial con `scale="X2"` en `fit`.
- Comprueba la convergencia (`res.converged`) y que α no esté en un límite: un α enorme o cero indica que el modelo no identifica la dispersión.

## Leer los residuos

- I de Moran de los residuos de Pearson (`res.resid_pearson`). Si es significativa, la p y los IC del GLM son optimistas: el GLM no modela el espacio. Se declara o se pasa a un modelo con componente espacial.
- Residuos grandes en zonas pequeñas suelen ser ruido de la tasa, no efecto: mira antes el tamaño de la población.
