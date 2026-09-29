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
 * Version information for AI Grader Central Config.
 *
 * @package    local_aiconfig
 * @copyright  2025 Essay Grader AI
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'local_aiconfig';
$plugin->version   = 2026082400;  // 10-digit Marketplace scheme, v1.0.16.
$plugin->requires  = 2022041900;
$plugin->supported = [400, 500];  // Moodle 4.0 to 5.x
$plugin->maturity  = MATURITY_STABLE;
$plugin->release   = '1.0.16';
