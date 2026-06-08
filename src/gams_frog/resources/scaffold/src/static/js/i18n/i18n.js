

(() => {

        /*
        *  Supplied functionality:
        *    Translates all elements with the data-i18n attribute according
        *    to language (lang url parameter) defined in the related i18n file.
        *    @param defaultLanguage: default language to be used for translation

        *    1. data-i18n attribute on any html element will be translated (based on ids)
        *    2. query parameter 'lang' (should be ISO code - e.g. 'de', 'en')
        *    3. additional translation files in i18n folder in static
        *    4. internal links will be rewritten to keep current query parameters (like lang)
        *
        */


        /**
        * Parses a data-i18n value into translation targets.
        * Syntax:
        *   "some.key"                        → innerHTML
        *   "[alt]some.key"                   → attribute
        *   "[alt]some.key;[title]other.key"  → multiple attributes
        *   "[alt]some.key;content.key"       → attribute + innerHTML
        *
        * @param {string} raw - the data-i18n attribute value
        * @returns {Array<{attr: string|null, key: string}>}
        */
        function parseI18nValue(raw) {
            const targets = [];
            for (const part of raw.split(';')) {
                const trimmed = part.trim();
                if (!trimmed) continue;

                const match = trimmed.match(/^\[(.+?)\](.+)$/);
                if (match) {
                    targets.push({ attr: match[1], key: match[2] });
                } else if (trimmed.includes('[')) {
                    // likely malformed — bracket present but didn't match pattern
                    if(!gams_frog.utils.isProduction()){
                        console.warn(`gams_frog-i18n: Malformed data-i18n value: "${trimmed}"`);
                    }
                } else {
                    targets.push({ attr: null, key: trimmed });
                }
            }
            return targets;
        }


        //i18n whitelist
        const ALLOWED_I18N_ATTRS = new Set([
        'alt', 'title', 'placeholder', 'aria-label', 'aria-description',"data-bs-title"
        ]);

        /**
        * Applies i18n translation for given data-i18n attribute value
        * and value stored in correspondent translation file.
        *
        */
        function applyTranslationToElement(element, translationMap) {
            const targets = parseI18nValue(element.getAttribute('data-i18n'));

            for (const target of targets) {
                const value = translationMap[target.key];
                if (!value) {
                    if (!gams_frog.utils.isProduction()) {
                        console.error(`gams_frog-i18n: No translation for key: "${target.key}"`, element);
                    }
                    continue;
                }

                if (target.attr === null) {
                    element.innerHTML = value;
                } else if (ALLOWED_I18N_ATTRS.has(target.attr)) {
                    element.setAttribute(target.attr, value);
                } else {
                    if(!gams_frog.utils.isProduction()){
                        console.warn(`gams_frog-i18n: Attribute "${target.attr}" not allowed. Skipping.`);
                    }
                }
            }
        }


        let cachedTranslations = null;
        let translationPromise = null;

        async function loadTranslations(language) {
            if (cachedTranslations) return cachedTranslations;
            if (translationPromise) return translationPromise;

            // reads
            let fileName = `js/i18n/${language}.json`;

            let mappedAssetPath = gams_frog.utils.mapAsset(fileName);
            // returns empty string on error
            if(!mappedAssetPath){
                console.error("i18nTranslationFileMappingError: Failed to retrieve expected translation file from static asset mapping. Aborting i18n.");
                return;
            }

            // must be built on client side
            const url = `${gams_frog._root_path}/static/${mappedAssetPath}`;

            translationPromise = (async () => {
                try {
                    const response = await fetch(url);
                    if (!response.ok) {
                        console.error(`gams_frog-i18n: Failed to fetch ${url} (HTTP ${response.status})`);
                        return null;
                    }
                    cachedTranslations = await response.json();
                    return cachedTranslations;
                } catch (error) {
                    console.error(`gams_frog-i18n: Failed to fetch ${url}`, error);
                    return null;
                }
            })();

            return translationPromise;
        }

        /**
        * Translates all elements with the data-i18n attribute according
        * to language (lang url parameter) defined in the related i18n file.
        * @param containerElem All translations / rewritings will happen inside this container defaults to document
        *
        * 1. data-i18n attribute on any html element will be translated (based on ids)
        * 2. query parameter 'lang' (should be ISO code - e.g. 'de', 'en') is being used to decide for the translation files
        * 3. additional translation files in i18n folder in static (mus also follow iso code e.g. "de.json")
        * 4. internal links will be rewritten to keep current query parameters (like lang)
        */
        window.gams_frog.i18n.translate = async (containerElem) => {
            if (!containerElem) containerElem = document;

            const defaultLanguage = window.gams_frog.i18n.defaultISOLanguage || 'de';
            const currentLanguage = new URLSearchParams(window.location.search).get('lang') || defaultLanguage;

            const translationMap = await loadTranslations(currentLanguage);
            if (!translationMap) {
                if (!gams_frog.utils.isProduction()) {
                    console.error("No translations for language '" + currentLanguage + " found!");
                }
                return;
            };

            // translate elements
            const elements = containerElem.querySelectorAll('[data-i18n]');
            elements.forEach(el => applyTranslationToElement(el, translationMap));

            if (!gams_frog.utils.isProduction()) {
                console.debug("gams_frog-i18n: Translated elements:", elements.length);
            }

            // rewrite internal links to maintain lang parameter
            if (currentLanguage === defaultLanguage) return;

            let rewroteCount = 0;
            containerElem.querySelectorAll('a[href]').forEach(link => {
                try {
                    const url = new URL(link.href, window.location.origin);
                    if (url.origin !== window.location.origin) return;
                    // if lang was explicetily set -> keep it! (e.g. when needing a language toggle)
                    if(url.searchParams.get('lang'))return;
                    url.searchParams.set('lang', currentLanguage);
                    link.href = url.toString();
                    rewroteCount++;
                } catch (e) {
                    if (!gams_frog.utils.isProduction()) {
                        console.warn("gams_frog-i18n: Malformed href:", link);
                    }
                }
            });

            if (!gams_frog.utils.isProduction()) {
                console.debug("gams_frog-i18n: Rewrote internal links:", rewroteCount);
            }
        };

    })();