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
 * Version metadata for the Adaptive course audit local plugin.
 *
 * @package     local_adaptive_course_audit
 * @copyright   2025 Bastian Schmidt-Kuhl <[email]>
 * @license     http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2026063001;
$plugin->requires  = 2024100700; // Moodle 4.5 release.
$plugin->supported = [405, 502]; // Moodle 4.5 LTS to 5.2.
$plugin->component = 'local_adaptive_course_audit';
$plugin->dependencies = [
    'tool_usertours' => 2024100700,
];
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = '1.3.1';
