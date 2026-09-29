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
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Moodle. If not, see <https://www.gnu.org/licenses/>.

/**
 * Version information for the Focus Journey course format.
 *
 * @package    format_focusjourney
 * @copyright  2026 FoneRep Technologies
 * @license    https://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->component = 'format_focusjourney';
$plugin->version = 2026080704;
$plugin->requires = 2024100700; // Moodle 4.5 or later.
$plugin->supported = [405, 502];
$plugin->maturity = MATURITY_STABLE;
$plugin->release = '1.2.3';
$plugin->dependencies = [
    'format_topics' => 2024100700,
];
