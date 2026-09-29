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
 * Meta-data about the plugin (like the version number, dependencies or the maturity level) are defined here.
 *
 *
 * File         version.php
 * Encoding     UTF-8
 *
 * @copyright   Bongo
 * @package     local_bongo
 * @author      Brian Kelly <[email]>
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 *
 */

if (!defined('MOODLE_INTERNAL')) {
    die('Direct access to this script is forbidden.'); // It must be included from a Moodle page.
}

// YYYYMMDDXX where XX is an incremental counter for the given year.
$plugin->version = 2021032201;

// Moodle 2.7.0 is required. This is because the mod_lti plugin was not available until 2.7.0.
$plugin->requires = 2014051200;

// Name of the plugin inside of moodle.
$plugin->component = 'local_bongo';

// How stable the plugin is: MATURITY_ALPHA, MATURITY_BETA, MATURITY_RC or MATURITY_STABLE.
$plugin->maturity = MATURITY_STABLE;

// This is the first revision for Bongo 1.6.
$plugin->release = '1.0-r1';


$plugin->dependencies = [
    // Bongo depends on an LTI tool to be installed.
    // It doesn't matter which version because Bongo doesn't do anything out of standard.
    'mod_lti' => ANY_VERSION

    // While Bongo relies on the course module, it is built into Moodle and is assumed to exist in every Moodle install.
];
