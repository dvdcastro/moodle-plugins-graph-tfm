<?php
// This file is part of Moodle - https://moodle.org/
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
 * Version metadata for the My Grades block.
 *
 * @package    block_my_grades
 * @copyright  2026 Brickfield Education Labs <https://www.brickfield.ie/>
 * @license    https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'block_my_grades';
$plugin->version   = 2026071204;
$plugin->requires  = 2024100700;       // Moodle 4.5 and up.
$plugin->supported = [405, 501];       // Moodle 4.5 to 5.1.
$plugin->release   = '2.405.4 (Build: 2026071204)';
$plugin->maturity  = MATURITY_STABLE;
