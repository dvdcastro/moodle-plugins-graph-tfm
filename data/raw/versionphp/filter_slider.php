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
 * Used to display Block Slider content anywhere in Moodle contents
 *
 * @package    filter_slider
 * @copyright  2020 Kamil Łuczak <[email]>
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version = 2025100000;
$plugin->maturity = MATURITY_BETA;
$plugin->release = '1.2 (Build: 2020050300)';
$plugin->requires = 2013050100;
$plugin->component = 'filter_slider';
$plugin->dependencies = array(
    'block_slider' => 2020011302, // Block Slider must be present (version 2020011302 or later).
);
