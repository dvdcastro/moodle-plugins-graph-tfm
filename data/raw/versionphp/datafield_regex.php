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
 * Plugin for datatype regular expressions.
 * @package    datafield_regex
 * @copyright  2024 Stephan Robotta ([email])
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2026041700;        // The current plugin version (Date: YYYYMMDDXX).
$plugin->requires  = 2022112808;        // Requires this Moodle version (4.1).
$plugin->component = 'datafield_regex'; // Full name of the plugin (used for diagnostics).
$plugin->release   = '1.7';             // Readable version of this plugin.
$plugin->maturity  = MATURITY_STABLE;   // Maturity of this plugin.
$plugin->supported = [401, 502];
