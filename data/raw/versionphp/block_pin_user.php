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
 * Defines the version details.
 *
 * @package     block_pin_user
 * @copyright   2024 Miguël Dhyne <[email]>
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2026062112;            // Plugin version (date-based numbering).
$plugin->requires  = 2021051700;            // Requires Moodle version 3.11 or higher.
$plugin->component = 'block_pin_user';      // Full name of the plugin (used for diagnostics).
$plugin->maturity  = MATURITY_STABLE;       // Plugin maturity level.
$plugin->release   = 'v2.5.5';              // Release version.
