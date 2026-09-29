<?php
// This file is part of Moodle - https://moodle.org/
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
// along with Moodle.  If not, see <https://www.gnu.org/licenses/>.

/**
 * Plugin version and other meta-data are defined here.
 *
 * @package     tiny_ubicast
 * @copyright   2025 UbiCast {@link https://www.ubicast.eu}
 * @license     https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'tiny_ubicast';      // Full name of the plugin (used for diagnostics).
$plugin->maturity = MATURITY_STABLE;      // Maturity of module.
$plugin->release = '1.5';                 // Human-readable version name.
$plugin->version = 2026081300;            // The current module version (Date: YYYYMMDDXX).
$plugin->requires = 2023042400;  // 4.2   // Requires this Moodle version.
$plugin->dependencies = [                 // Other plugins required.
    'mod_ubicast' => 2025112000,
];
