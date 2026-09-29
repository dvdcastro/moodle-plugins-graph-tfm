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
 * Version information.
 *
 * Plugin Install Timer - This plugin displays the installation and update dates of your plugins, as well as the user who made the action.
 *
 * @package     local_plugininstalltimer
 * @copyright   2026 Luiggi Sansonetti <[email]> (Coder)
 * @copyright   2026 E-learning Touch' <[email]> (Maintainer)
 * @license     https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */
defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_plugininstalltimer';
$plugin->version   = 2026041400;
$plugin->requires  = 2024100700; // Moodle 4.5+
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = '1.1';
$plugin->supported = [405, 502];
