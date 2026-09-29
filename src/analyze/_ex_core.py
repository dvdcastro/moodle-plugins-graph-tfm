"""Plugins del directorio con historia en el nucleo de Moodle (confusor documentado).

Evidencia: frase literal de la propia ficha del plugin en el directorio
(cache data/raw/html/<component>.html, snapshot 2026-09). Solo se incluyen
plugins cuya ficha lo afirma explicitamente; no hay inferencias.

EX_CORE: salieron del nucleo al directorio. Heredan dependientes (temas hijos
de Moodle 2.x) y traducciones de los paquetes de idioma del nucleo, lo que
infla su centralidad en G_dep y sus cifras de traduccion.
INTO_CORE: hicieron el camino inverso (el directorio conserva la ficha).
"""

_MOVED_27 = "This theme was part of the Moodle core distribution, but for Moodle 2.7+ has been moved to Moodle plugins"
_MOVED_32 = "This theme was part of the Moodle core distribution, but for Moodle 3.2+ has now been moved to Moodle plugins"

EX_CORE = {
    **{f"theme_{t}": _MOVED_27 for t in [
        "afterburner", "anomaly", "arialist", "binarius", "boxxie", "brick", "formfactor", "fusion",
        "leatherbound", "magazine", "nimble", "nonzero", "overlay", "serenity", "sky_high", "splash",
        "standard", "standardold"]},
    "theme_base": _MOVED_32,
    "theme_canvas": _MOVED_32,
    "block_course_overview": "a legacy version of the block which used to be part of the standard Moodle installation. Starting with Moodle 3.3 ...",
    "webservice_xmlrpc": "This plugin was part of core until Moodle 4.0, finally removed for Moodle 4.1",
}

INTO_CORE = {
    "qtype_gapselect": "This question type became part of the standard Moodle package in Moodle 3.2.",
    "quizaccess_seb": "This plugin will be part of the standard Moodle distributions from versions 3.9+",
}
