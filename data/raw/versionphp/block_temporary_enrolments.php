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
 * MOODLE VERSION INFORMATION
 *
 * This file contains version information for the Temporary Enrolment Block by Andrew Zito
 *
 * @package    block_temporary_enrolments
 * @copyright  2018 onwards Lafayette College ITS
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die;

$plugin->version = 2019031836;                      // The current plugin version (Date: YYYYMMDDXX).
$plugin->requires = 2018120300;                     // Requires Moodle 3.6.
$plugin->component = 'block_temporary_enrolments';  // Full name of the plugin (used for diagnostics).
$plugin->maturity = MATURITY_BETA;
$plugin->release = '1.0.3-36.0'; // Pattern: [major].[minor].[patch]-[Moodle Version].[Moodle version specific patch].
$plugin->dependencies = array(
  'local_temporary_enrolments' => 2019031336 // v1.1.0-36.0.
);