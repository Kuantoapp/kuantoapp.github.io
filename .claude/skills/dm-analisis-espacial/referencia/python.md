# Equivalencias R → Python

El curso usa R. El proyecto usa Python. Comprueba la firma exacta en la documentación de la versión instalada antes de usar una función.

| Tarea | R (curso) | Python |
|---|---|---|
| Geometrías y CRS | `sf`, `st_transform` | `geopandas`, `gdf.to_crs(25830)` |
| W contigüidad reina | `spdep::poly2nb` + `nb2listw(style="W")` | `libpysal.weights.Queen.from_dataframe(gdf)`, `w.transform = "r"` |
| W k vecinos o distancia | `knearneigh`, `dnearneigh` | `libpysal.weights.KNN.from_dataframe(gdf, k=5)`, `DistanceBand` |
| Retardo espacial | `lag.listw` | `libpysal.weights.lag_spatial(w, y)` |
| I de Moran (permutaciones) | `moran.mc` | `esda.Moran(y, w, permutations=999)` |
| LISA | `localmoran` | `esda.Moran_Local(y, w)` |
| Getis-Ord local | `localG` | `esda.G_Local(y, w, star=True)` |
| MCO con tests LM | `lm.LMtests` | `spreg.OLS(y, X, w=w, spat_diag=True, moran=True)` |
| SAR / SEM por máxima verosimilitud | `spatialreg::lagsarlm`, `errorsarlm` | `spreg.ML_Lag`, `spreg.ML_Error` |
| SAR por MC2E/GMM | `stsls` | `spreg.GM_Lag` |
| Efectos directos e indirectos | `impacts()` | `spreg.ML_Lag(..., spat_impacts=...)` en versiones recientes, o calcular (I − ρW)⁻¹ |
| GWR | `GWmodel`, `spgwr` | `mgwr.gwr.GWR` |
| Semivariograma y kriging | `gstat::variogram`, `krige` | `pykrige.ok.OrdinaryKriging`, `pykrige.uk.UniversalKriging` |
| Validación por bloques | `spatialsample::spatial_block_cv` | `sklearn.model_selection.GroupKFold` con grupos de bloque |
| Validación con buffer | `spatial_buffer_vfold_cv` | Manual: excluir de train los puntos a menos de r (con `sjoin_nearest` o `cKDTree`) |
| Coroplético | `tmap`, `ggplot2` | `geopandas.plot(scheme=...)` con `mapclassify` |

**Islas:** en `libpysal`, `w.islands` lista las zonas sin vecinos. Trátalas antes de calcular Moran o estimar.
