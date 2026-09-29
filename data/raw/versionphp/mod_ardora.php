<?php
// This file is part of Moodle - http://moodle.org/
//
// Moodle is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Moodle is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle.  If not, see <http://www.gnu.org/licenses/>.

/**
 * ardora module version information
 * created from the "Resource module" version created by 2009 Petr Skoda  {@link http://skodak.org}
 * @package    mod_ardora
 * @copyright  2026 José Manuel Bouzán Matanza (https://www.webardora.net)
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2026061002; // WEBService: Updated version to refresh services with mod_ardora_external class.
$plugin->requires  = 2022112800; // Requires Moodle 4.1.
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = '2.0.1'; // WEBService: Updated release version with web services fix.
$plugin->component = 'mod_ardora'; // Full name of the plugin (used for diagnostics).
$plugin->cron      = 0;
