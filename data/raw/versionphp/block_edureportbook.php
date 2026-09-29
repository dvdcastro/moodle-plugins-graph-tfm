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
 *
 * @package    block_edureportbook
 * @copyright  2019 Robert Schrenk, Digital Education Society, @link www.dibig.at, based on enrol_manual from 2010 Petr Skoda {@link http://skodak.org}
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version   = 2021122500;
$plugin->requires  = 2018050800;
$plugin->component = 'block_edureportbook';
$plugin->maturity = MATURITY_STABLE;
$plugin->release = 'V 2.1.1';
$plugin->dependencies = [
    'block_enrolcode' => 2021111801,
];
