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
 * Block to search courses by filter out course name and description.
 *
 * @package    block_search_course
 * @copyright  3i Logic
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2017051503;        // The current plugin version (Date: YYYYMMDDXX).
$plugin->requires  = 2010112400;        // Requires this Moodle version.
$plugin->component = 'block_search_course';
$plugin->release = '3.3';
$plugin->maturity = MATURITY_STABLE;