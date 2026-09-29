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
 * Course Category Finder Block
 * Course Category Finder is an extended version of the Course Finder Block. An Option is added to
 * enable the user to search for categories as well as the courses. Aditional search filter and sort
 * filter is added to search courses by start date, end date, course format and completion criteria.
 *
 * @package    block_search_course_category
 * @copyright  Copyrights © 2016 - 2021 | BTU Cottbus-Senftenberg
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2021062300;        // The current plugin version (Date: YYYYMMDDXX)
$plugin->requires  = 2016120500;        // Requires this Moodle version (3.3).
$plugin->release = '3.7';
$plugin->component = 'block_search_course_category';
$plugin->maturity = MATURITY_STABLE;
