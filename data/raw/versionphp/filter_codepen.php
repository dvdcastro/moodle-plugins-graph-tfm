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
 * plugin details
 *
 * @package filter
 * @subpackage codepen
 * @copyright 2017 Arnaud Trouvé <[email]>
 * @copyright 2014 Danny Wahl www.iyWare.com
 * @license http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'filter_codepen'; // Full name of the plugin (used for diagnostics)
$plugin->version   = 2026051800;       // The current plugin version (Date: YYYYMMDDXX)
$plugin->requires  = 2024100700;       // Requires this Moodle version
$plugin->release   = '3.6.0';       // Human-friendly version name http://docs.moodle.org/dev/Releases
$plugin->maturity  = MATURITY_STABLE;  // This version's maturity level.
