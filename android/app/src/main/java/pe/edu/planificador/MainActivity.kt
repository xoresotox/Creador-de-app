package pe.edu.planificador

import android.annotation.SuppressLint
import android.os.Build
import android.os.Bundle
import android.view.View
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.appcompat.app.AppCompatActivity
import androidx.webkit.WebViewAssetLoader

/**
 * MainActivity: contenedor WebView para la app de planificación nutricional.
 *
 * Toda la lógica (Simplex Big-M, modelo de PL, base de alimentos TPCA-INS,
 * UI) vive en assets/web/index.html y corre 100% offline. Esta Activity
 * solo provee el WebView nativo y un AssetLoader para servir los archivos.
 */
class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        webView = WebView(this).apply {
            layoutParams = android.view.ViewGroup.LayoutParams(
                android.view.ViewGroup.LayoutParams.MATCH_PARENT,
                android.view.ViewGroup.LayoutParams.MATCH_PARENT
            )
        }
        setContentView(webView)

        // Configuración del WebView: JS habilitado, dom storage para
        // recordar inputs, y soporte para zoom/teclado.
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            loadWithOverviewMode = true
            useWideViewPort = true
            allowFileAccess = false
            allowContentAccess = false
            cacheMode = WebSettings.LOAD_DEFAULT
            // Service Worker funcionará con WebViewAssetLoader si la API lo permite
        }

        // AssetLoader sirve assets/web/ bajo https://appassets.androidplatform.net/
        // Esto es necesario porque los Service Workers requieren un origen HTTPS.
        val assetLoader = WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", WebViewAssetLoader.AssetsPathHandler(this))
            .build()

        webView.webViewClient = object : WebViewClient() {
            override fun shouldInterceptRequest(
                view: WebView,
                request: android.webkit.WebResourceRequest
            ) = assetLoader.shouldInterceptRequest(request.url)
        }

        // Modo edge-to-edge moderno
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            window.setDecorFitsSystemWindows(true)
        } else {
            @Suppress("DEPRECATION")
            window.decorView.systemUiVisibility = View.SYSTEM_UI_FLAG_LAYOUT_STABLE
        }

        webView.loadUrl("https://appassets.androidplatform.net/assets/web/index.html")
    }

    override fun onBackPressed() {
        if (this::webView.isInitialized && webView.canGoBack()) {
            webView.goBack()
        } else {
            @Suppress("DEPRECATION")
            super.onBackPressed()
        }
    }
}
