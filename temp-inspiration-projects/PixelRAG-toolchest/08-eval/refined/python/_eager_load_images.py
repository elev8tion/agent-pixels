def _eager_load_images(driver):
    """Force lazy images to load by promoting data-src and setting loading='eager'."""
    driver.execute_script("""
        (function() {
            var imgs = document.querySelectorAll('img');
            for (var i = 0; i < imgs.length; i++) {
                var img = imgs[i];
                try {
                    if (img.loading === 'lazy') img.loading = 'eager';
                    var dataSrc = img.getAttribute('data-src') || (img.dataset && img.dataset.src);
                    var dataSrcset = img.getAttribute('data-srcset') || (img.dataset && img.dataset.srcset);
                    if (dataSrc) img.setAttribute('src', dataSrc);
                    if (dataSrcset) img.setAttribute('srcset', dataSrcset);
                } catch(e) {}
            }
        })();
    """)
