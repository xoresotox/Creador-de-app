# Planificador Nutricional Óptimo (NutriPL)

Aplicación de planificación nutricional basada en **Programación Lineal**
(método **Simplex Big-M** implementado desde cero) y datos de las
**Tablas Peruanas de Composición de Alimentos** (TPCA · INS-CENAN).

Disponible como:
- **APK Android** (Android 7.0+) — empaquetado nativo, funciona offline.
- **PWA** (Progressive Web App) — instalable desde el navegador.
- **Página web** simple (`web/index.html`) — abrir en cualquier navegador.

---

## Cómo descargar el APK

El APK se compila automáticamente en GitHub Actions cada vez que se hace
push a `main` o a una rama `feat/**`. **No necesitas Android Studio ni
ningún SDK local.**

### Opción A: descargar desde Actions (cualquier commit)
1. Ve a la pestaña **Actions** del repositorio en GitHub.
2. Abre el workflow más reciente llamado **Build APK**.
3. Al final de la página verás los **Artifacts**:
   - `nutripl-debug-apk` — versión de desarrollo
   - `nutripl-release-apk` — versión optimizada (firmada con debug-key)
4. Descarga el zip, extráelo y transfiere el `.apk` al teléfono.

### Opción B: release oficial (solo en tags `v*`)
Si el mantenedor crea un tag `git tag v1.0.0 && git push --tags`, el APK
queda publicado en la sección **Releases** del repositorio.

### Instalación en Android
1. Abre el `.apk` en el teléfono.
2. Habilita "Instalar de orígenes desconocidos" si Android lo solicita.
3. Confirma la instalación. La app aparecerá como **NutriPL**.

> El APK release viene firmado con la **debug-keystore** del CI. Para
> publicar en Play Store necesitarás generar tu propia keystore y
> configurar `signingConfigs` en `android/app/build.gradle.kts`.

---

## Cómo usar la app

1. **Ingresa tus datos**: peso, altura, edad, sexo, nivel de actividad, objetivo.
   - La TMB se calcula con **Mifflin-St Jeor** y se ajusta automáticamente.
2. **Configura el modelo**:
   - Función objetivo: minimizar costo o maximizar puntaje nutricional.
   - Restricciones opcionales: presupuesto en S/., variedad mínima de
     alimentos, exclusión de grupos (lácteos, gluten, etc.).
3. **Selecciona alimentos**: marca/desmarca cualquier alimento de la tabla.
   Las **calorías y macronutrientes son fijos** (vienen de TPCA).
   Solo puedes ajustar el costo en S/.
4. **Presiona "▶ Generar plan óptimo"** y obtendrás:
   - Lista exacta de alimentos en gramos.
   - Costo total y valor objetivo.
   - Pie chart de macros y semáforo nutricional.
   - Comparativa restricción vs valor obtenido.
   - Análisis de sensibilidad (ranging) sobre las calorías.
   - Proceso Simplex paso a paso (colapsable).

---

## Estructura del repositorio

```
.
├── web/                          # App web pura (PWA)
│   ├── index.html               # Toda la lógica, UI y datos
│   ├── manifest.webmanifest
│   ├── sw.js                    # Service Worker offline
│   ├── icon-192.png · icon-512.png
│
├── android/                      # Proyecto Android nativo
│   ├── build.gradle.kts
│   ├── settings.gradle.kts
│   ├── gradle.properties
│   └── app/
│       ├── build.gradle.kts
│       └── src/main/
│           ├── AndroidManifest.xml
│           ├── java/pe/edu/planificador/MainActivity.kt   # WebView wrapper
│           ├── res/...                                    # Themes, íconos
│           └── assets/web/                                # Copia de web/
│
├── .github/workflows/
│   ├── build-apk.yml             # Compila el APK en cada push
│   └── pages.yml                 # Despliega la PWA a GitHub Pages
│
├── scripts/
│   ├── gen_icons.py              # Regenera los íconos PNG
│   └── sync-web.sh               # Copia web/ → android/app/.../assets/web/
│
├── index.html                    # Copia de web/index.html (fallback raíz)
└── README.md
```

---

## Modelo de Programación Lineal

```
Variables:
    x_i = cantidad del alimento i en porciones de 100 g    (x_i ≥ 0)

Objetivo (uno de los dos):
    MIN  Σ costo_i · x_i        (plan más económico)
    MAX  Σ puntaje_i · x_i      (plan más nutritivo)
                                  puntaje = prot + 0.4·carb − 0.25·gras

Restricciones obligatorias:
    R1)   Σ cal_i · x_i  ≥  0.95 · TMB
    R2)   Σ cal_i · x_i  ≤  1.05 · TMB
    R3)   Σ prot_i · x_i ≥  0.8  · peso_kg               (recomendación OMS)
    R4)   Σ gras_i · x_i ≤  0.35 · TMB / 9
    R5)   Σ carb_i · x_i ≥  0.45 · TMB / 4

Restricciones opcionales:
    R6)   Σ costo_i · x_i ≤ presupuesto
    R7)   x_i = 0  para alimentos excluidos por grupo
    R8)   x_i ≤ 5  (máx 500 g/alimento — evita degeneración)
    R9)   x_i ≥ 0.3 para N alimentos diversos             (variedad mínima)
```

### Algoritmo

**Simplex Big-M**, implementado desde cero en `web/index.html`
(función `simplexBigM`). Sin librerías externas. Convierte automáticamente:
- restricciones `≤` con variable de holgura,
- restricciones `≥` con variable de superávit + artificial Big-M,
- restricciones `=` con variable artificial Big-M,
- maximización a minimización de `−c`.

Detecta `optimal`, `infeasible` y `unbounded`. Guarda snapshot de cada
iteración para mostrar el proceso paso a paso en la UI.

### Análisis de sensibilidad

Ranging numérico sobre la cota inferior calórica (R1): se perturba ±200 kcal
y se reporta el rango contiguo donde la composición óptima del plan no cambia.

---

## Datos de alimentos

48 alimentos peruanos en 11 grupos (Cereales, Tubérculos, Legumbres, Carnes,
Pescados, Huevos, Lácteos, Frutas, Verduras, Grasas, Frutos secos),
con valores de calorías, proteínas, grasas y carbohidratos por 100 g
basados en las **Tablas Peruanas de Composición de Alimentos** (TPCA),
publicación oficial del **Instituto Nacional de Salud (INS) - CENAN, Perú**.

Costos referenciales de mercados peruanos 2024 (S/. por 100 g).

> **Importar tu propia tabla.** Si tienes el JSON oficial extraído de
> la última edición de TPCA, ábrelo en el panel "Importar/exportar tabla
> de alimentos (JSON)" de la app y reemplaza la base de datos. La
> estructura debe ser un arreglo de objetos:
> `{nombre, grupo, cal, prot, gras, carb, costo}` (todo por 100 g).

---

## Desarrollo local

### Probar la app web (sin instalar nada)

```bash
# Cualquier servidor estático sirve. Ej:
python3 -m http.server -d web 8080
# Abrir http://localhost:8080
```

Para que el Service Worker funcione, debes servirla por HTTP (no `file://`).

### Compilar el APK localmente

Requiere **Java 17**, **Gradle 8.7+** y el **Android SDK** (con
`platforms;android-34` y `build-tools;34.0.0`).

```bash
bash scripts/sync-web.sh                # copia web/ → assets/web/
cd android
gradle :app:assembleDebug               # produce app/build/outputs/apk/debug/*.apk
```

### Regenerar los íconos

```bash
python3 scripts/gen_icons.py
```

---

## CI/CD

| Workflow              | Disparador                         | Salida                                |
|-----------------------|------------------------------------|---------------------------------------|
| `build-apk.yml`       | push a `main` o `feat/**`, PR, tag | APKs como artifacts (+ release en tag)|
| `pages.yml`           | push a `main`                      | PWA desplegada en GitHub Pages        |

---

## Licencia

Código MIT. Los datos de TPCA son propiedad del INS-CENAN, Perú.

---

## Limitaciones conocidas

- Los planes pueden incluir cantidades inusuales de un único alimento
  cuando minimizamos costo sin restricciones de variedad. Por eso se
  recomienda activar "Mín. variedad" ≥ 5.
- El análisis de sensibilidad es numérico (re-resolución), no analítico.
  Para un ranging exacto se requeriría exponer el dual del LP.
- El Service Worker dentro del WebView de Android funciona pero no es
  estrictamente necesario: la app ya está empaquetada en assets locales.
