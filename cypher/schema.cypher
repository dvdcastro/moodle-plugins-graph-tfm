// Fase 2 - constraints e indices del modelo de datos.
// Ejecutar una sola vez antes de cargar nodos/relaciones.

CREATE CONSTRAINT plugin_component IF NOT EXISTS FOR (p:Plugin) REQUIRE p.component IS UNIQUE;
CREATE CONSTRAINT maintainer_user_id IF NOT EXISTS FOR (m:Maintainer) REQUIRE m.user_id IS UNIQUE;
CREATE CONSTRAINT category_code IF NOT EXISTS FOR (c:Category) REQUIRE c.code IS UNIQUE;
CREATE CONSTRAINT release_name IF NOT EXISTS FOR (r:MoodleRelease) REQUIRE r.release IS UNIQUE;
CREATE CONSTRAINT set_id IF NOT EXISTS FOR (s:Set) REQUIRE s.set_id IS UNIQUE;

CREATE INDEX plugin_installations IF NOT EXISTS FOR (p:Plugin) ON (p.installations);
CREATE INDEX plugin_last_release IF NOT EXISTS FOR (p:Plugin) ON (p.last_release_ts);
