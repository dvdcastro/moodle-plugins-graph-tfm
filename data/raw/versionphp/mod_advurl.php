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
 * Version metadata for the advanced URL plugin.
 *
 * @package    mod_advurl
 * @copyright  2025 Greystone College
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

// The current plugin version (date: YYYYMMDDXX).
$plugin->version   = 2025100102;
// Required Moodle version.
$plugin->requires  = 2022041900; // Moodle 4.0 or later.
// Full name of the plugin (used for diagnostics).
$plugin->component = 'mod_advurl';
// Maturity level of this plugin version.
$plugin->maturity  = MATURITY_STABLE;
// Human readable release version.
$plugin->release   = '1.1.7';