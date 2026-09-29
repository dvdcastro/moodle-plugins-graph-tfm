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
 * Version details
 *
 * @package   block_course_checker_info
 * @copyright 2025 Simon Gisler, Fernfachhochschule Schweiz (FFHS) <[email]>
 * @copyright 2025 Stefan Dani, Fernfachhochschule Schweiz (FFHS) <[email]>
 * @copyright based on work by 2019 Liip SA <[email]>
 * @copyright based on work by 2019 Adrian Perez, Fernfachhochschule Schweiz (FFHS) <[email]>
 * @license   http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version = 2025111400;
$plugin->requires = 2025041400;
$plugin->release = 'v5.0-r1';
$plugin->component = 'block_course_checker_info';
$plugin->maturity = MATURITY_STABLE;
$plugin->dependencies = [
        'local_course_checker' => 2025062600,
];
