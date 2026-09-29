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
 * Plugin version and other meta-data are defined here.
 *
 * @package   local_inactivitynotifier
 * @copyright 2026 Daniel Ferrada
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_inactivitynotifier'; // Unique plugin name.
$plugin->version   = 2026090300;                 // Version: YYYYMMDDXX (July 20, 2026).
$plugin->requires  = 2022112800;                 // Minimum Moodle version (Moodle 4.1).
$plugin->supported = [401, 502];                  // Supported Moodle range: 4.1 to 5.2.
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = '1.0.4';
