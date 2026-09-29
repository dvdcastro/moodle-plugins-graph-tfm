<?php
// This file is part of the customcert module for Moodle - https://moodle.org/
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
 * Plugin version information.
 *
 * @package   customcertelement_assignfeedbackcomments
 * @copyright 2026 Joe Rebbeck <[email]>
 * @license   https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'customcertelement_assignfeedbackcomments';
$plugin->version   = 2026031901;
$plugin->requires  = 2022112800; // Updated to Moodle 4.1+ per README
$plugin->maturity  = MATURITY_BETA;
$plugin->release   = '1.0.0';

// Declare explicit dependencies for robust installation checks
$plugin->dependencies = [
    'mod_customcert' => 2022112800, // Matching Moodle 4.1 timeframe
    'mod_assign'     => 2022112800,
];
