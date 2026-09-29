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
 * Version 4.0 release
 *
 * @package    mod_cado
 * @copyright  2020-2022 Naomi Quirke
 * @license    http://www.gnu.org/copyleft/gpl.html GNU GPL v3 or later
 */

defined('MOODLE_INTERNAL') || die();

$plugin->version = 2023010600;
$plugin->requires = 2018051700; // Requires 3.5.
$plugin->supported = [400, 401]; // Range from 4.0 to 4.1.
$plugin->component = 'mod_cado';
$plugin->release = '4.0';
$plugin->maturity  = MATURITY_STABLE;
$plugin->dependencies = [
];
